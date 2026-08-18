from __future__ import annotations

import json
import logging
import statistics
from typing import Optional, TypedDict

import streamlit as st

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
        lines.append(f"  {change['from']} -> {change['to']}")
    return "\n".join(lines)


def build_system_prompt(snapshot: DashboardSnapshot, diff: dict) -> str:
    lang_name = LANGUAGE_NAMES.get(snapshot["language"], "English")

    parts = [
        "You are the in-app assistant for Suraksha Lens, a climate-related "
        "exploitation early warning dashboard. You can see the current "
        "dashboard snapshot provided below. The snapshot contains the "
        "currently displayed dashboard state and, when available, the "
        "numerical data behind the currently displayed graph.\n\n"

        "If a question requires information that is not present in the "
        "current snapshot, say so plainly rather than speculating.\n\n"

        "When responding in the dashboard chat, prioritize readable prose "
        "and bullet points. Avoid Markdown tables unless the user explicitly "
        "asks for a table or a table is clearly the best way to compare "
        "multiple items. Keep responses concise enough to fit comfortably "
        "within a narrow chat panel. Break long explanations into short "
        "paragraphs and bullet points. Never produce extremely wide tables.\n\n"

        "Do not restate chart_data row by row or transcribe it back in "
        "full — synthesize it (trend, highest/lowest, notable changes) "
        "instead. Default to a short answer (a few sentences or a handful "
        "of bullet points); only go longer if the user explicitly asks for "
        "a full breakdown or every value.\n\n"

        f"Respond only in {lang_name}, regardless of what language the "
        "user's question is written in.",

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




def render_chat_toggle_button() -> None:
    if st.sidebar.button(
        t("chat_bot.close_button")
        if st.session_state.get("chat_panel_open", False)
        else t("chat_bot.open_button"),
        key="chat_toggle_btn",
    ):
        st.session_state.chat_panel_open = not st.session_state.get(
            "chat_panel_open", False
        )
        st.rerun()


def render_chat_panel() -> None:
    st.markdown(
        """
        <div class="chat-panel">
        """,
        unsafe_allow_html=True,
    )

    header_col, close_col = st.columns([5, 1])

    with header_col:
        st.subheader(t("chat_bot.title"))

    with close_col:
        if st.button("✕", key="chat_close_btn"):
            st.session_state.chat_panel_open = False
            st.rerun()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_text = st.chat_input(t("chat_bot.placeholder"))

    if user_text:
        with st.spinner(t("chat_bot.thinking")):
            handle_user_message(user_text)
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)