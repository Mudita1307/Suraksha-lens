from __future__ import annotations

import json
import logging
import statistics
from typing import Optional, TypedDict

import streamlit as st
import streamlit.components.v1 as components

from i18n import t

logger = logging.getLogger(__name__)


LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "si": "Sinhala",
    "ta": "Tamil",
    "be": "Bengali",
    "ka": "Kannada",
    "ma": "Malayalam",
}



def init_chat_state() -> None:
    """Initialize the app-wide chat session_state keys exactly once.

    Called from main.py before page routing (pg.run()), so these keys exist
    regardless of which page loads first and survive page navigation.

    Streamlit reruns the whole script top-to-bottom on every interaction, so this
    runs on every rerun — it MUST be idempotent. Each guard only seeds a key when
    absent, so an in-progress conversation, stored snapshot, open/closed panel
    state, and version counter are never reset mid-session.
    """
    if "chat_history" not in st.session_state:
        # list[{"role": "user" | "assistant", "content": str}]
        st.session_state.chat_history = []
    if "dashboard_snapshot" not in st.session_state:
        # previous-turn snapshot, dict or None
        st.session_state.dashboard_snapshot = None
    if "chat_panel_open" not in st.session_state:
        st.session_state.chat_panel_open = False
    if "_snapshot_version" not in st.session_state:
        # server-side / log only, never sent to the LLM
        st.session_state._snapshot_version = 0
    if "chat_chart_data" not in st.session_state:
        st.session_state.chat_chart_data = None
    if "chat_chart_context" not in st.session_state:
        st.session_state.chat_chart_context = None



class DashboardSnapshot(TypedDict):
    page: str
    tier: str
    country: Optional[str]
    states: list
    districts: list
    metric: str
    language: str
    active_filters: dict
    summary_stats: dict
    chart_context: Optional[dict]
    chart_data: Optional[list]



def _collect_active_filters() -> dict:
    return dict(st.session_state.get("_active_filters", {}) or {})


def _collect_visible_summary_stats() -> dict:
    return dict(st.session_state.get("_visible_summary_stats", {}) or {})


# -----------------------------------------------------------------------
# Chart-context registry
# -----------------------------------------------------------------------
# Every dashboard page that renders a chart should call clear_chart_context()
# near the top of the script (before any chart is built) and set_chart_context()
# right after it computes the data behind the chart it displays. This keeps
# the naming and shape identical across tier1-4, so build_snapshot() always
# knows where to find "what the user is currently looking at."

def clear_chart_context() -> None:
    """Call at the top of a dashboard page, before any chart is built, so a
    page that errors out (e.g. a missing column) or takes a branch with no
    chart doesn't leave a stale chart from a previous render in the snapshot.
    """
    st.session_state["chat_chart_data"] = None
    st.session_state["chat_chart_context"] = None


# Groq's on_demand tier for this model is capped at a small tokens-per-minute
# budget, so the full snapshot (instructions + json) must stay well under it.
# Raw per-district-per-year tables get large fast (Tier 3 alone can have 20+
# indicators across dozens of districts), so anything above this row count
# gets collapsed into yearly aggregates + top/bottom categories instead of
# being sent row-by-row.
MAX_RAW_CHART_ROWS = 60
TOP_BOTTOM_N = 5

# Fields whose full before/after values are too large to duplicate in the
# "changed since last turn" diff (see diff_snapshots) — the current value is
# already present in full in the main snapshot above it.
_HEAVY_DIFF_FIELDS = {"chart_data"}


def _round_value(value):
    if isinstance(value, float):
        return round(value, 3)
    return value


def _round_records(records: list) -> list:
    return [
        {k: _round_value(v) for k, v in row.items()}
        for row in records
    ]


def _summarize_chart_data(
    data_records: list,
    year_column: str,
    category_column: str,
    metric_column: str,
) -> tuple[object, bool]:
    """Collapse a large chart table into something that fits the token
    budget: per-year mean/min/max, plus the highest and lowest categories by
    mean value. Returns (payload, was_summarized).
    """
    if len(data_records) <= MAX_RAW_CHART_ROWS:
        return _round_records(data_records), False

    by_year: dict = {}
    by_category: dict = {}

    for row in data_records:
        year = row.get(year_column)
        category = row.get(category_column)
        value = row.get(metric_column)
        if value is None:
            continue
        try:
            value = float(value)
        except (TypeError, ValueError):
            continue
        by_year.setdefault(year, []).append(value)
        by_category.setdefault(category, []).append(value)

    yearly_summary = [
        {
            year_column: year,
            "mean": round(statistics.mean(values), 3),
            "min": round(min(values), 3),
            "max": round(max(values), 3),
            "n": len(values),
        }
        for year, values in sorted(by_year.items(), key=lambda kv: str(kv[0]))
    ]

    category_means = {
        category: round(statistics.mean(values), 3)
        for category, values in by_category.items()
    }
    ranked = sorted(category_means.items(), key=lambda kv: kv[1], reverse=True)

    payload = {
        "yearly_summary": yearly_summary,
        "top_categories_by_mean": [
            {category_column: c, "mean_value": v} for c, v in ranked[:TOP_BOTTOM_N]
        ],
        "bottom_categories_by_mean": [
            {category_column: c, "mean_value": v} for c, v in ranked[-TOP_BOTTOM_N:]
        ],
        "total_categories": len(by_category),
        "total_rows_omitted": len(data_records),
    }
    return payload, True


def set_chart_context(
    *,
    tier: str,
    country: Optional[str],
    metric: str,
    metric_column: str,
    year_column: str,
    category_column: str,
    chart_title: str,
    data_records: list,
    chart_kind: str = "line",
    note: str = "",
) -> None:
    """Register the data + metadata behind the chart currently on screen.

    data_records should be the same rows feeding the chart (e.g.
    trend_df.to_dict(orient="records")). Large tables are automatically
    summarized (see _summarize_chart_data) to stay within the LLM's token
    budget; small ones are passed through as-is (with floats rounded).
    """
    payload, was_summarized = _summarize_chart_data(
        data_records, year_column, category_column, metric_column
    )
    st.session_state["chat_chart_data"] = payload
    st.session_state["chat_chart_context"] = {
        "tier": tier,
        "country": country,
        "metric": metric,
        "metric_column": metric_column,
        "year_column": year_column,
        "category_column": category_column,
        "chart_title": chart_title,
        "chart_kind": chart_kind,
        "note": note,
        "data_summarized": was_summarized,
    }


def build_snapshot() -> DashboardSnapshot:
    return {
        "page": st.session_state.get("_current_page", "unknown"),
        "tier": st.session_state.get("tier", "T1"),
        "country": st.session_state.get("country"),
        "states": list(st.session_state.get("states") or []),
        "districts": list(st.session_state.get("districts") or []),
        "metric": st.session_state.get("metric", "unknown"),
        "language": st.session_state.get("lang", "en"),
        "active_filters": _collect_active_filters(),
        "summary_stats": _collect_visible_summary_stats(),
        "chart_context": st.session_state.get("chat_chart_context"),
        "chart_data": st.session_state.get("chat_chart_data"),
    }



def diff_snapshots(
    previous: Optional[DashboardSnapshot],
    current: DashboardSnapshot,
) -> dict:
    if previous is None:
        return {}

    changed: dict = {}
    for key in current:
        prev_val = previous.get(key)
        curr_val = current.get(key)
        if prev_val == curr_val:
            continue
        if key in _HEAVY_DIFF_FIELDS:
            # The current value already sits in full above (under
            # "Current Dashboard Snapshot"). Repeating both the old and new
            # copies of a potentially large chart table here would burn
            # tokens for no real benefit — a note that it changed is enough.
            changed[key] = {
                "changed": True,
                "note": "chart_data changed since the previous turn; "
                        "see the current chart_data in the snapshot above "
                        "for the up-to-date values",
            }
        else:
            changed[key] = {"from": prev_val, "to": curr_val}
    return changed



def _format_diff_block(diff: dict) -> str:
    lines = []
    for field, change in diff.items():
        lines.append(f"{field}:")
        if "from" in change:
            lines.append(f"  {change['from']} -> {change['to']}")
        else:
            # Fields in _HEAVY_DIFF_FIELDS carry a note rather than their
            # before/after values, which are too large to repeat here.
            lines.append(f"  {change['note']}")
    return "\n".join(lines)


def build_system_prompt(snapshot: DashboardSnapshot, diff: dict) -> str:
    lang_name = LANGUAGE_NAMES.get(snapshot["language"], "English")

    parts = [
        "You are the in-app assistant for Suraksha Lens, a climate-related "
        "exploitation early warning dashboard. You can see the current "
        "dashboard snapshot provided below. The snapshot contains the "
        "currently displayed dashboard state and, when available, the "
        "numerical data behind the currently displayed graph.\n\n"

        "Answer the question that was actually asked, in the form it was "
        "asked and in the user's own words. When the user puts forward their "
        "own reading of the chart, or asks anything answerable with yes or "
        "no, open with the verdict — 'Yes', 'No', or 'Almost, except...' — "
        "and then give only the detail that settles it. Restating the figures "
        "neutrally is not an answer to that kind of question: the reader "
        "cannot tell from it whether they were right. If part of their "
        "reading holds and part does not, say which part is wrong.\n\n"

        "Write back the way a colleague would answer out loud — the same "
        "vocabulary the user used, and roughly the length the question "
        "deserves. Something that can be settled in one sentence gets one "
        "sentence.\n\n"

        "Never walk chart_data back to the reader value by value, whether as "
        "prose, a list or a table, and however few rows it holds. Listing "
        "every year is transcribing the chart, not answering a question about "
        "it. Quote only the specific figures the answer turns on, inline in "
        "the sentence that uses them. For an open-ended question, characterise "
        "what the data shows — the trend, the extremes, anything notable — "
        "rather than enumerating it. Reach for bullet points only when the "
        "answer genuinely has several parallel parts; a yes-or-no answer "
        "almost never does.\n\n"

        "If the snapshot cannot answer the question, say so in the first "
        "sentence and name what is missing, or what would have to change on "
        "the dashboard to get it. Do not quietly answer a nearby question "
        "instead, and do not speculate.\n\n"

        "Avoid Markdown tables unless the user explicitly asks for one. Keep "
        "replies short enough to read comfortably in a narrow chat panel, and "
        "never produce wide tables.\n\n"

        "Reply in the language the user asked in, and in the same script they "
        "used: a question typed in Devanagari is answered in Devanagari, one "
        "typed in romanised Hindi is answered in romanised Hindi. Carry their "
        "register across too — the same level of formality and politeness "
        "they chose, and wording just as plain and gentle as theirs. This "
        "dashboard deals with violence and exploitation, so keep the tone "
        "measured and humane, and never phrase an answer more bluntly or more "
        "clinically than the question was put. When the question is too short "
        "or too ambiguous to tell which language it is in, answer in "
        f"{lang_name}, the language the dashboard is currently set to.",

        "",

        "=== Current Dashboard Snapshot ===",

        """
The snapshot contains the current dashboard state.

The `tier` field is authoritative:
T1 = Hazard
T2 = Exposure
T3 = Vulnerability
T4 = Climate Exploitation Risk Index

Always answer according to the current tier, country, metric, filters,
and chart data.

If `chart_data` is present, it contains the numerical data used to
generate the graph currently displayed on the dashboard. `chart_context`
describes what that data means: the metric, the underlying column names,
the chart title, what kind of chart it is (line / stacked_bar / map), and
an optional data-availability note.

`chart_context.data_summarized` tells you the shape of `chart_data`:
- false: `chart_data` is the raw list of rows behind the chart (one row per
  category/year combination), exactly as plotted.
- true: the raw table was too large to send in full, so `chart_data` is
  instead an object with `yearly_summary` (mean/min/max/n per year),
  `top_categories_by_mean` and `bottom_categories_by_mean` (the highest and
  lowest categories by mean value), `total_categories`, and
  `total_rows_omitted`. In this case you can describe overall trends and
  the highest/lowest categories, but you do NOT have every individual data
  point — if asked for an exact value for a specific category/year that
  isn't in the summary, say the dashboard would need to be filtered
  (fewer states/districts selected) to see that exact figure.

You CAN analyze `chart_data`.

Do NOT say that you cannot see graphs when `chart_data` is available.

When the user asks about a trend, pattern, increase, decrease, peak,
minimum, comparison, or change over time, analyze the values in
`chart_data` directly.

If `chart_data` is null, no chart is currently displayed (e.g. the user is
on a page or view with no chart, or the selected metric/column could not
be found) — say so rather than guessing at values.

Do not invent values that are not present in the snapshot.
""",

        json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")),

        "===================================",
    ]

    if diff:
        parts += [
            "",
            "=== Dashboard Changes Since Previous Turn ===",
            _format_diff_block(diff),
            "==============================================",
        ]

    return "\n".join(parts)



class LLMCallError(Exception):
    """Raised for any recoverable model-call failure (rate limit, timeout,
    malformed/empty response). handle_user_message() catches this and shows the
    translated chat_bot.error_message rather than a raw traceback."""


GROQ_MODEL = "openai/gpt-oss-120b"

_groq_client = None


def _get_client():
    global _groq_client

    if _groq_client is None:
        from groq import Groq

        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except KeyError as e:
            raise LLMCallError(
                f"Missing Groq config in secrets: {e}"
            ) from e

        _groq_client = Groq(api_key=api_key)

    return _groq_client


def call_llm(system_prompt: str, history: list[dict]) -> str:
    try:
        client = _get_client()
    except LLMCallError:
        raise
    except Exception as e:
        raise LLMCallError(f"client initialization failed: {e}") from e

    messages = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]}
        for m in history
    ]

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_completion_tokens=1024,
        )

        finish_reason = response.choices[0].finish_reason

        logger.info(
            "LLM finish_reason=%s, usage=%s",
            finish_reason,
            response.usage,
        )

        if finish_reason == "length":
            logger.warning(
                "LLM response was truncated at the token limit"
            )

    except Exception as e:
        raise LLMCallError(f"model request failed: {e}") from e

    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as e:
        raise LLMCallError(f"malformed response: {e}") from e

    if not content or not content.strip():
        raise LLMCallError("empty response from model")

    return content




def handle_user_message(user_text: str) -> None:
    current_snapshot = build_snapshot()
    previous_snapshot = st.session_state.dashboard_snapshot
    diff = diff_snapshots(previous_snapshot, current_snapshot)

    system_prompt = build_system_prompt(current_snapshot, diff)

    st.session_state.chat_history.append({"role": "user", "content": user_text})

    try:
        reply = call_llm(
            system_prompt=system_prompt,
            # NOTE: this was `chat_history[-5]` (a single element, and an
            # IndexError on the very first message when len < 5). It must be
            # a slice. Kept short (last 3 turns) since this Groq tier's
            # tokens-per-minute budget is small (8000) and the system prompt
            # already carries the full dashboard snapshot every turn.
            history=st.session_state.chat_history[-3:],
        )
        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply}
        )

        # Commit the new snapshot as "previous" only AFTER a successful call.
        st.session_state.dashboard_snapshot = current_snapshot
        st.session_state._snapshot_version += 1

    except LLMCallError as e:
        st.session_state.chat_history.append(
            {"role": "assistant", "content": t("chat_bot.error_message")}
        )
        logger.warning("Chat call failed: %s", e)




def _inject_chat_fab_css() -> None:
    """CSS for the round chat opener pinned to the bottom-right corner.

    Targets `.st-key-chat_toggle_btn`, the class Streamlit puts on the button's
    own element container, so no extra wrapper is involved. Three Streamlit
    specifics this has to work around:

    - Streamlit blocks are width:100%, so `right` alone stretches the box across
      the whole viewport and leaves the button sitting at the far left (under
      the sidebar). It needs an explicit width to shrink to the button.
    - Streamlit's own sidebar is z-index 999991 and its header 999990, so a
      lower z-index hides the button behind them.
    - Positioning the button rather than a surrounding st.container keeps it
      from costing a 16px flex-gap slot in the page, which would shift all the
      dashboard content down whenever the chat is closed.
    """
    st.markdown(
        """
        <style>
        .st-key-chat_toggle_btn {
            position: fixed;
            right: 28px;
            bottom: 28px;
            width: 58px;
            z-index: 1000000;
        }
        .st-key-chat_toggle_btn button {
            border-radius: 50%;
            width: 58px;
            height: 58px;
            padding: 0;
            font-size: 26px;
            line-height: 1;
            border: none;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_chat_toggle_button() -> None:
    """Floating chat opener, fixed to the bottom-right of the viewport.

    Only rendered while the panel is closed. Once open, the panel's own '✕'
    (see render_chat_panel) is the close control.
    """
    if st.session_state.get("chat_panel_open", False):
        return

    _inject_chat_fab_css()

    if st.button(
        "💬",
        key="chat_toggle_btn",
        help=t("chat_bot.open_button"),
    ):
        st.session_state.chat_panel_open = True
        st.rerun()


# Starter questions offered on an empty chat, as locale keys. Three fixed,
# page-agnostic prompts rather than a rotating pool — see render_chat_panel.
SUGGESTION_KEYS = ("suggestion_1", "suggestion_2", "suggestion_3")


def _inject_chat_panel_css() -> None:
    """Layout for the open chat: a viewport-tall panel with the composer at the
    foot of it and the greeting centred in the space above.

    The CSS is deliberately flush against the left margin, and injected with
    st.html rather than st.markdown. A rule that opens with `[attr="value"]:`
    also reads as Markdown's link-reference-definition syntax, so when it is
    indented inside a Markdown-parsed block it is silently dropped and never
    reaches the page — which is exactly what the stLayoutWrapper rules below are.
    """
    st.html(
        """
<style>
/* The chat rides along at viewport height instead of stretching to match the
dashboard column, so the composer stays reachable however long the page is. */
.st-key-chat_panel {
/* 8rem is where the column already starts under Streamlit's header, so the
panel sticks exactly where it sat and never jumps as the dashboard scrolls;
the extra 1rem of height keeps the composer clear of the viewport edge. */
position: sticky;
top: 8rem;
height: calc(100vh - 9rem);
/* flex:0 0 auto is load-bearing: Streamlit gives the block flex:1 1 0%, and in
its column-flex wrapper that basis wins over height, stretching the panel to
the full dashboard height and pushing the composer off-screen. */
flex: 0 0 auto;
display: flex;
flex-direction: column;
}
[data-testid="stLayoutWrapper"]:has(> .st-key-chat_panel) {
flex: 1 1 auto;
}
/* Streamlit wraps every st.container in a layout div; the wrapper is the real
flex child, so it has to grow for the body to take the leftover height. */
[data-testid="stLayoutWrapper"]:has(> .st-key-chat_body) {
flex: 1 1 auto;
min-height: 0;
display: flex;
flex-direction: column;
}
.st-key-chat_body {
flex: 1 1 auto;
min-height: 0;
overflow-y: auto;
}
.st-key-chat_body:has(.chat-greeting) {
justify-content: center;
}
.chat-greeting {
text-align: center;
padding: 0 4px 2px;
}
.chat-greeting-title {
font-size: 1.3rem;
font-weight: 600;
margin-bottom: 6px;
}
.chat-greeting-body {
font-size: 0.88rem;
line-height: 1.5;
opacity: 0.7;
}
</style>
        """
    )


def _scroll_transcript_to_latest(token: str) -> None:
    """Pin the transcript to the newest message after a rerun.

    Streamlit replays the script but leaves the scroll container at whatever
    offset it had, so a fresh reply lands below the fold and has to be scrolled
    to by hand. st.html and st.markdown both strip <script>, so this rides in a
    components iframe — the one place Streamlit still executes JS — and reaches
    back into the parent document.

    token is interpolated into the markup on purpose: Streamlit only remounts a
    component when its html changes, so without something that moves every turn
    the iframe would be reused and the scroll would never re-fire.

    The pin repeats on mutation rather than once on mount because the echoed
    question, the spinner and the reply are each painted after this component
    lands, and a single scroll would fire before any of them existed.
    """
    components.html(
        f"""
<span hidden>{token}</span>
<script>
const doc = window.parent.document;
const pin = () => {{
    const body = doc.querySelector('.st-key-chat_body');
    if (body) {{ body.scrollTop = body.scrollHeight; }}
}};
pin();
const body = doc.querySelector('.st-key-chat_body');
if (body) {{
    const observer = new MutationObserver(pin);
    observer.observe(body, {{childList: true, subtree: true}});
    setTimeout(() => observer.disconnect(), 3000);
}}
</script>
        """,
        height=0,
    )


def _render_chat_empty_state() -> Optional[str]:
    """Greeting plus tappable starter questions. Returns the tapped question."""
    st.markdown(
        "<div class='chat-greeting'>"
        f"<div class='chat-greeting-title'>{t('chat_bot.greeting_title')}</div>"
        f"<div class='chat-greeting-body'>{t('chat_bot.greeting_body')}</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    for index, suggestion_key in enumerate(SUGGESTION_KEYS):
        question = t(f"chat_bot.{suggestion_key}")
        if st.button(
            question,
            key=f"chat_suggestion_{index}",
            use_container_width=True,
        ):
            return question

    return None


def render_chat_panel() -> None:
    """Chat conversation, rendered into the column main.py reserves for it.

    The starter questions are the same three every time rather than a rotating
    selection: they exist to show what the assistant can be asked, and Streamlit
    reruns this script on every filter change and page switch, so a random pick
    would reshuffle under the reader mid-sentence.
    """
    _inject_chat_panel_css()

    with st.container(key="chat_panel"):
        header_col, close_col = st.columns([5, 1])

        with header_col:
            st.subheader(t("chat_bot.title"))

        with close_col:
            if st.button("✕", key="chat_close_btn"):
                st.session_state.chat_panel_open = False
                st.rerun()

        with st.container(key="chat_body"):
            tapped_question = None

            if st.session_state.chat_history:
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
            else:
                tapped_question = _render_chat_empty_state()

            # Claimed here, at the foot of the transcript, because Streamlit
            # renders a spinner wherever execution happens to be standing. The
            # question is not known until st.chat_input below has run, by which
            # point the panel is closed and the spinner would appear under the
            # composer instead of where the reply is about to land.
            pending_reply = st.empty()

        typed_question = st.chat_input(
            t("chat_bot.placeholder"),
            key="chat_input",
        )

    question = tapped_question or typed_question

    if st.session_state.chat_history or question:
        # outside the panel container so the component's own element cannot
        # take a row of the panel's flex layout. The pending marker keeps the
        # token moving on submit, when the history has not grown yet, so the
        # echoed question below is scrolled into view rather than left under
        # the fold.
        _scroll_transcript_to_latest(
            f"{len(st.session_state.chat_history)}"
            f"{'-pending' if question else ''}"
        )

    if question:
        with pending_reply.container():
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner(t("chat_bot.thinking")):
                    handle_user_message(question)

        st.rerun()