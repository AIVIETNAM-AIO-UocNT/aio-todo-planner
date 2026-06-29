"""
pages/tasks.py — Task management in Kanban view
"""

import streamlit as st
from datetime import date

from frontend.api.client import (
    get_tasks, get_projects, get_labels,
    create_task, update_task, delete_task,
)
from frontend.utils.ui import (
    inject_css, render_sidebar,
    label_pill_html, deadline_badge_html, build_label_map,
)

st.set_page_config(page_title="Tasks · TaskPlanner", page_icon="✅", layout="wide")
inject_css()
render_sidebar()

st.title("✅ Tasks")

# ── Load data ─────────────────────────────────────────────────────────────────
projects  = get_projects()
labels    = get_labels()
label_map = build_label_map(labels)
proj_map  = {p["id"]: p["name"] for p in projects}

# ── Filter bar ────────────────────────────────────────────────────────────────
with st.container(border=True):
    fc1, fc2, fc3, fc4 = st.columns([3, 2, 2, 2])

    search_q = fc1.text_input("🔍 Search tasks", placeholder="Title...",
                              label_visibility="collapsed")

    proj_options = {"All": None} | {p["name"]: p["id"] for p in projects}
    sel_proj_name = fc2.selectbox("Project", list(proj_options.keys()),
                                  label_visibility="collapsed")
    sel_proj_id   = proj_options[sel_proj_name]

    status_options = {"All statuses": None, "To Do": "todo",
                      "Doing": "doing", "Done": "done"}
    sel_status_name = fc3.selectbox("Status", list(status_options.keys()),
                                    label_visibility="collapsed")
    sel_status = status_options[sel_status_name]

    label_options = {"All labels": None} | {l["name"]: l["id"] for l in labels}
    sel_label_name = fc4.selectbox("Label", list(label_options.keys()),
                                   label_visibility="collapsed")
    sel_label_id   = label_options[sel_label_name]

# ── Load tasks with filters ───────────────────────────────────────────────────
all_tasks = get_tasks(
    project_id=sel_proj_id,
    status=sel_status,
    label_id=sel_label_id,
)
if search_q:
    all_tasks = [t for t in all_tasks
                 if search_q.lower() in t["title"].lower()]

tasks_by_status = {
    "todo":  [t for t in all_tasks if t["status"] == "todo"],
    "doing": [t for t in all_tasks if t["status"] == "doing"],
    "done":  [t for t in all_tasks if t["status"] == "done"],
}

# ── Add task button ───────────────────────────────────────────────────────────
_, btn_col = st.columns([6, 1])
with btn_col:
    if st.button("➕ Add Task", use_container_width=True, type="primary"):
        st.session_state["show_create_task"] = True

# ── Create task form ──────────────────────────────────────────────────────────
if st.session_state.get("show_create_task"):
    with st.container(border=True):
        st.markdown("#### Create new task")
        r1c1, r1c2 = st.columns([3, 2])
        t_title = r1c1.text_input("Title *", placeholder="Task name...")
        t_proj_name = r1c2.selectbox(
            "Project *",
            [p["name"] for p in projects],
            key="new_task_proj",
        )
        t_proj_id = next(p["id"] for p in projects if p["name"] == t_proj_name)

        r2c1, r2c2 = st.columns([3, 2])
        t_desc     = r2c1.text_area("Description", height=70, placeholder="Details (optional)...")
        t_deadline = r2c2.date_input("Deadline", value=None, min_value=date.today())

        t_label_names = st.multiselect(
            "Assign labels",
            [l["name"] for l in labels],
            key="new_task_labels",
        )
        t_label_ids = [l["id"] for l in labels if l["name"] in t_label_names]

        bc1, bc2 = st.columns(2)
        if bc1.button("💾 Save Task", use_container_width=True, type="primary"):
            if t_title.strip():
                create_task(
                    project_id  = t_proj_id,
                    title       = t_title.strip(),
                    description = t_desc.strip(),
                    deadline    = t_deadline.isoformat() if t_deadline else None,
                    label_ids   = t_label_ids,
                )
                st.session_state.pop("show_create_task", None)
                st.success(f"✅ Task **{t_title}** added")
                st.rerun()
            else:
                st.error("Title cannot be empty.")
        if bc2.button("✕ Cancel", use_container_width=True):
            st.session_state.pop("show_create_task", None)
            st.rerun()

st.divider()

# ═══════════════════════════════════════════════════════════════
#  KANBAN — 3 columns
# ═══════════════════════════════════════════════════════════════

COL_CFG = [
    ("todo",  "⬜ To Do",  "#888780"),
    ("doing", "🔄 Doing",  "#BA7517"),
    ("done",  "✅ Done",   "#3B6D11"),
]

kanban_cols = st.columns(3, gap="medium")

for col_widget, (status_key, status_label, accent) in zip(kanban_cols, COL_CFG):
    tasks = tasks_by_status[status_key]

    with col_widget:
        # ── Kanban column header ──────────────────────────────────────────
        st.markdown(
            f"<div style='background:#f4f4f2;border-radius:10px;"
            f"padding:8px 12px;margin-bottom:10px;"
            f"border-left:3px solid {accent};'>"
            f"<b style='color:{accent};font-size:13px;'>{status_label}</b> "
            f"<span style='font-size:11px;color:#888;'>({len(tasks)})</span></div>",
            unsafe_allow_html=True,
        )

        if not tasks:
            st.markdown(
                "<div style='text-align:center;padding:20px;"
                "color:#aaa;font-size:12px;'>No tasks</div>",
                unsafe_allow_html=True,
            )

        # ── Task cards ────────────────────────────────────────────────────
        for task in tasks:
            label_html = " ".join(
                label_pill_html(label_map[lid]["name"], label_map[lid]["color"])
                for lid in task.get("label_ids", [])
                if lid in label_map
            )
            dl_html    = deadline_badge_html(task.get("deadline"))
            proj_name  = proj_map.get(task["project_id"], "—")
            done_class = "done-card" if task["status"] == "done" else ""

            with st.container():
                st.markdown(
                    f"""<div class="task-card {done_class}">
                        <div class="task-title">{task['title']}</div>
                        <div class="task-meta">{label_html} {dl_html}</div>
                        <div style="font-size:10px;color:#aaa;margin-top:4px;">
                            📁 {proj_name}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

                # ── Actions per card ──────────────────────────────────────
                with st.expander("⚙️ Options", expanded=False):
                    # Change status
                    status_opts = ["todo", "doing", "done"]
                    new_status  = st.selectbox(
                        "Change status",
                        status_opts,
                        index=status_opts.index(task["status"]),
                        key=f"status_{task['id']}",
                        format_func=lambda s: {"todo":"⬜ To Do","doing":"🔄 Doing","done":"✅ Done"}[s],
                    )
                    if new_status != task["status"]:
                        if st.button("Update", key=f"upd_status_{task['id']}",
                                     use_container_width=True):
                            update_task(task["id"], status=new_status)
                            st.rerun()

                    # Quick edit deadline
                    cur_dl = date.fromisoformat(task["deadline"]) if task.get("deadline") else None
                    new_dl = st.date_input("Deadline", value=cur_dl,
                                           key=f"dl_{task['id']}")
                    if new_dl != cur_dl:
                        if st.button("Save deadline", key=f"upd_dl_{task['id']}",
                                     use_container_width=True):
                            update_task(task["id"], deadline=new_dl.isoformat())
                            st.rerun()

                    # Reassign labels
                    cur_label_names = [label_map[lid]["name"]
                                       for lid in task.get("label_ids",[])
                                       if lid in label_map]
                    new_label_names = st.multiselect(
                        "Labels",
                        [l["name"] for l in labels],
                        default=cur_label_names,
                        key=f"lbl_{task['id']}",
                    )
                    if set(new_label_names) != set(cur_label_names):
                        if st.button("Save labels", key=f"upd_lbl_{task['id']}",
                                     use_container_width=True):
                            new_ids = [l["id"] for l in labels
                                       if l["name"] in new_label_names]
                            update_task(task["id"], label_ids=new_ids)
                            st.rerun()

                    st.markdown("---")
                    if st.button("🗑️ Delete task", key=f"del_{task['id']}",
                                 use_container_width=True):
                        delete_task(task["id"])
                        st.rerun()
