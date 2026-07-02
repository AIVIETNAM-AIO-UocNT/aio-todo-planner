"""
utils/ui.py — Shared helpers used across the entire frontend
"""

import streamlit as st
from datetime import date


# ─── Label colors ───────────────────────────────────────────────────────────

LABEL_BG_MAP = {
    "#3B6D11": "#EAF3DE",
    "#185FA5": "#E6F1FB",
    "#BA7517": "#FAEEDA",
    "#993C1D": "#FAECE7",
    "#533AB7": "#EEEDFE",
    "#0F6E56": "#E1F5EE",
    "#A32D2D": "#FCEBEB",
    "#888780": "#F1EFE8",
}

STATUS_COLOR = {
    "todo":  ("#888780", "#F1EFE8", "To Do"),
    "doing": ("#854F0B", "#FAEEDA", "Doing"),
    "done":  ("#3B6D11", "#EAF3DE", "Done"),
}


# ─── CSS inject ────────────────────────────────────────────────────────────

APP_CSS = """
<style>
/* ── Global ── */
[data-testid="stSidebarNav"] {display: none;}
[data-testid="stSidebarHeader"] {display: none;}
[data-testid="stAppViewContainer"] { background: #fafafa; }
[data-testid="stSidebar"] { background: #f4f4f2 !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    font-size: 13px; color: #444;
}

/* ── Metric cards ── */
div[data-testid="metric-container"] {
    background: #f4f4f2;
    border-radius: 10px;
    padding: 14px 16px 10px;
    border: 0.5px solid #ddd;
}

/* ── Progress bar ── */
div[data-testid="stProgress"] > div { border-radius: 4px; }

/* ── Buttons ── */
.stButton > button {
    border-radius: 8px;
    font-size: 13px;
}

/* ── Kanban column ── */
.kanban-col {
    background: #f4f4f2;
    border-radius: 12px;
    padding: 12px;
    min-height: 300px;
}
.kanban-header {
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── Task card ── */
.task-card {
    background: #fff;
    border: 0.5px solid #e0e0e0;
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 8px;
}
.task-card.done-card {
    opacity: 0.55;
    text-decoration: line-through;
}
.task-title {
    font-size: 13px;
    color: #1a1a1a;
    font-weight: 500;
    margin-bottom: 5px;
}
.task-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    align-items: center;
}

/* ── Label pill ── */
.label-pill {
    display: inline-block;
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 10px;
    font-weight: 600;
}

/* ── Deadline badge ── */
.deadline-badge {
    font-size: 10px;
    padding: 2px 7px;
    border-radius: 8px;
    font-weight: 500;
}
.deadline-ok      { background: #f1efe8; color: #5f5e5a; }
.deadline-overdue { background: #fcebeb; color: #a32d2d; }
.deadline-soon    { background: #faeeda; color: #854f0b; }

/* ── Project card ── */
.project-card {
    background: #fff;
    border: 0.5px solid #e0e0e0;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.project-name { font-size: 15px; font-weight: 600; color: #1a1a1a; }
.project-desc { font-size: 12px; color: #666; margin: 4px 0 8px; }

/* ── Overdue alert card ── */
.overdue-item {
    background: #fcebeb;
    border-left: 3px solid #a32d2d;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 6px;
    font-size: 13px;
    color: #501313;
}
.overdue-meta { font-size: 11px; color: #a32d2d; margin-top: 2px; }
</style>
"""


def inject_css():
    st.markdown(APP_CSS, unsafe_allow_html=True)


# ─── Label helpers ─────────────────────────────────────────────────────────

def label_pill_html(name: str, color: str) -> str:
    bg = LABEL_BG_MAP.get(color, "#f0f0f0")
    return (f'<span class="label-pill" '
            f'style="background:{bg};color:{color};">{name}</span>')


def deadline_badge_html(deadline_str: str) -> str:
    if not deadline_str:
        return ""
    try:
        dl = date.fromisoformat(deadline_str)
    except ValueError:
        return ""
    today = date.today()
    diff = (dl - today).days
    fmt  = dl.strftime("%d/%m")
    if diff < 0:
        css = "deadline-overdue"
        label = f"⚠ {fmt} (overdue)"
    elif diff <= 3:
        css = "deadline-soon"
        label = f"⏰ {fmt}"
    else:
        css = "deadline-ok"
        label = f"📅 {fmt}"
    return f'<span class="deadline-badge {css}">{label}</span>'


def status_badge_html(status: str) -> str:
    color, bg, label = STATUS_COLOR.get(status, ("#888", "#eee", status))
    return (f'<span class="label-pill" '
            f'style="background:{bg};color:{color};">{label}</span>')


# ─── Label lookup helper ────────────────────────────────────────────────────

def build_label_map(labels: list) -> dict:
    """Returns {id: {name, color}} from the labels list."""
    return {l["id"]: l for l in labels}


# ─── Sidebar navigation ─────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown("## 📋 TaskPlanner")
        st.caption("Personal task manager")
        st.divider()
        st.page_link("app.py",              label="🏠  Dashboard",  )
        st.page_link("pages/projects.py",   label="📁  Projects",   )
        st.page_link("pages/tasks.py",      label="✅  Tasks",      )
        st.page_link("pages/labels.py",     label="🏷️  Labels",    )
        st.divider()
        st.caption("🟢 Mode: Live API")