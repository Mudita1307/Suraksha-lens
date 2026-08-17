from __future__ import annotations

import json
import logging
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



def _collect_active_filters() -> dict:
    return dict(st.session_state.get("_active_filters", {}) or {})


def _collect_visible_summary_stats() -> dict:
    return dict(st.session_state.get("_visible_summary_stats", {}) or {})


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
        if previous.get(key) != current.get(key):
            changed[key] = {"from": previous.get(key), "to": current.get(key)}
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

Always answer according to the current tier, country, metric, filters, "
and chart data.

If `chart_data` is present, it contains the numerical data used to "
"generate the graph currently displayed on the dashboard.

You CAN analyze `chart_data`.

Do NOT say that you cannot see graphs when `chart_data` is available.

When the user asks about a trend, pattern, increase, decrease, peak, "
"minimum, comparison, or change over time, analyze the values in "
"`chart_data` directly.

Do not invent values that are not present in the snapshot.
""",

        json.dumps(snapshot, ensure_ascii=False, indent=2),

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
            max_completion_tokens=2048,
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
            history=st.session_state.chat_history[-5],
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