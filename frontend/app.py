"""
app.py — Dashboard home page
Run: streamlit run app.py  (from inside the frontend/ directory)
"""

import streamlit as st

from api.client import (
    get_dashboard_summary, get_projects,
    get_project_progress, get_overdue_tasks, get_labels,
)
from utils.ui import inject_css, render_sidebar, label_pill_html, build_label_map

st.set_page_config(
    page_title="TaskPlanner",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()
render_sidebar()

st.title("📊 Dashboard")
st.caption("Your work progress overview")

summary  = get_dashboard_summary()
projects = get_projects()
overdue  = get_overdue_tasks()
labels   = get_labels()
label_map = build_label_map(labels)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📌 Total Tasks",  summary["total"])
c2.metric("⬜ To Do",         summary["todo"])
c3.metric("🔄 Doing",         summary["doing"])
c4.metric("✅ Done",           summary["done"])
c5.metric("⚠️ Overdue",       summary["overdue"],
          delta=f"-{summary['overdue']}" if summary["overdue"] else None,
          delta_color="inverse")

st.divider()

left, right = st.columns([3, 2], gap="large")

with left:
    st.subheader("📁 Project Progress")

    if not projects:
        st.info("No projects yet. Create your first project!")
    else:
        for proj in projects:
            prog = get_project_progress(proj["id"])
            pct  = prog["percent"]
            done = prog["done"]
            total= prog["total"]

            col_name, col_pct = st.columns([5, 1])
            col_name.markdown(f"**{proj['name']}**")
            col_pct.markdown(
                f"<div style='text-align:right;font-size:12px;color:#666;'>"
                f"{done}/{total} · {pct}%</div>",
                unsafe_allow_html=True,
            )
            st.progress(pct / 100)

    st.divider()

    st.subheader("📈 Task Status Distribution")

    import pandas as pd
    chart_data = pd.DataFrame({
        "Tasks": [summary["todo"], summary["doing"], summary["done"]]
    }, index=["To Do", "Doing", "Done"])
    
    import plotly.express as px
    status_df = pd.DataFrame({
        "status": ["To Do", "Doing", "Done"],
        "count": [summary["todo"], summary["doing"], summary["done"]]
    })
    fig = px.bar(status_df, x="status", y="count", color="status",
                color_discrete_map={"To Do": "#a1a1aa", "Doing": "#3b82f6", "Done": "#22c55e"},
                text="count")
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=10, r=10),
        height=280,
    )
    fig.update_traces(textposition="outside", marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True)

with right:
    overdue_count = len(overdue)
    header_color  = "🔴" if overdue_count > 0 else "🟢"
    st.subheader(f"{header_color} Overdue Tasks ({overdue_count})")

    if not overdue:
        st.success("Great! No overdue tasks.")
    else:
        # Map project name
        proj_map = {p["id"]: p["name"] for p in projects}
        for task in overdue:
            proj_name = proj_map.get(task["project_id"], "—")
            label_html = " ".join(
                label_pill_html(label_map[lid]["name"], label_map[lid]["color"])
                for lid in task.get("label_ids", [])
                if lid in label_map
            )
            st.markdown(
                f"""<div class="overdue-item">
                    <strong>{task['title']}</strong><br>
                    <span class="overdue-meta">📁 {proj_name} &nbsp;·&nbsp;
                    ⏰ Due: {task['deadline']}</span><br>
                    <div style="margin-top:4px">{label_html}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.divider()

    st.subheader("📌 Quick Summary")
    total = summary["total"] or 1
    st.markdown(
        f"- Completion rate: **{round(summary['done']/total*100)}%**"
    )
    st.markdown(f"- Active projects: **{len(projects)}**")
    st.markdown(f"- Labels in use: **{len(labels)}**")
    if overdue_count:
        st.warning(f"You have **{overdue_count}** overdue task(s) to address.")