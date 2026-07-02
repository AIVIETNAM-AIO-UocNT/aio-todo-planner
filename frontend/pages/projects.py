"""
pages/projects.py — Project management
"""

import streamlit as st

from api.client import (
    get_projects, create_project, update_project,
    delete_project, get_project_progress, get_labels,
)
from utils.ui import inject_css, render_sidebar, build_label_map

st.set_page_config(page_title="Projects · TaskPlanner", page_icon="📁", layout="wide")
inject_css()
render_sidebar()

st.title("📁 Projects")

# ── Load data ─────────────────────────────────────────────────────────────────
if "projects_refreshed" not in st.session_state:
    st.session_state.projects_refreshed = False

projects  = get_projects()
labels    = get_labels()
label_map = build_label_map(labels)

# ── Create project button ─────────────────────────────────────────────────────
col_title, col_btn = st.columns([5, 1])
with col_btn:
    if st.button("➕ New Project", use_container_width=True, type="primary"):
        st.session_state["show_create_project"] = True

# ── Create project form ───────────────────────────────────────────────────────
if st.session_state.get("show_create_project"):
    with st.container(border=True):
        st.markdown("#### Create new project")
        new_name = st.text_input("Project name *", key="new_proj_name",
                                 placeholder="e.g. Work, Study...")
        new_desc = st.text_area("Description", key="new_proj_desc", height=80,
                                placeholder="Short description of this project...")
        c1, c2 = st.columns([1, 1])
        if c1.button("💾 Save", use_container_width=True, type="primary"):
            if new_name.strip():
                create_project(new_name.strip(), new_desc.strip())
                st.session_state.pop("show_create_project", None)
                st.success(f"✅ Project **{new_name}** created!")
                st.rerun()
            else:
                st.error("Project name cannot be empty.")
        if c2.button("✕ Cancel", use_container_width=True):
            st.session_state.pop("show_create_project", None)
            st.rerun()

st.divider()

# ── Project list ──────────────────────────────────────────────────────────────
if not projects:
    st.info("No projects yet. Create your first project!")
else:
    # Display as a 2-column grid
    cols = st.columns(2, gap="medium")
    for idx, proj in enumerate(projects):
        prog = get_project_progress(proj["id"])
        pct  = prog["percent"]
        done = prog["done"]
        total= prog["total"]

        with cols[idx % 2]:
            with st.container(border=True):
                # ── Header ──────────────────────────────────────────────────
                h_col, btn_col = st.columns([5, 2])
                h_col.markdown(f"### {proj['name']}")
                with btn_col:
                    if st.session_state.pop(f"_reset_proj_action_{proj['id']}", False):
                        st.session_state[f"proj_action_{proj['id']}"] = "—"
                    action = st.selectbox(
                        "Action",
                        ["—", "✏️ Edit", "🗑️ Delete"],
                        key=f"proj_action_{proj['id']}",
                        label_visibility="collapsed",
                    )

                # ── Description ─────────────────────────────────────────────
                if proj.get("description"):
                    st.caption(proj["description"])

                # ── Progress ─────────────────────────────────────────────────
                p_col, n_col = st.columns([5, 1])
                p_col.progress(pct / 100)
                n_col.markdown(
                    f"<div style='font-size:12px;color:#666;margin-top:6px'>"
                    f"{pct}%</div>",
                    unsafe_allow_html=True,
                )
                st.caption(f"✅ {done} / {total} tasks completed")

                # ── Handle action ────────────────────────────────────────────
                if action == "✏️ Edit":
                    st.session_state[f"edit_proj_{proj['id']}"] = True
                    st.session_state[f"_reset_proj_action_{proj['id']}"] = True
                    st.rerun()

                if action == "🗑️ Delete":
                    st.session_state[f"confirm_del_proj_{proj['id']}"] = True
                    st.session_state[f"_reset_proj_action_{proj['id']}"] = True
                    st.rerun()

                # ── Edit form ─────────────────────────────────────────────────
                if st.session_state.get(f"edit_proj_{proj['id']}"):
                    with st.form(key=f"edit_form_{proj['id']}"):
                        st.markdown("**Edit project**")
                        e_name = st.text_input("Name", value=proj["name"])
                        e_desc = st.text_area("Description", value=proj.get("description",""), height=70)
                        s1, s2 = st.columns(2)
                        if s1.form_submit_button("💾 Save", use_container_width=True, type="primary"):
                            if e_name.strip():
                                update_project(proj["id"], e_name.strip(), e_desc.strip())
                                st.session_state.pop(f"edit_proj_{proj['id']}", None)
                                st.rerun()
                            else:
                                st.error("Name cannot be empty.")
                        if s2.form_submit_button("✕ Cancel", use_container_width=True):
                            st.session_state.pop(f"edit_proj_{proj['id']}", None)
                            st.rerun()

                # ── Delete confirmation ───────────────────────────────────────
                if st.session_state.get(f"confirm_del_proj_{proj['id']}"):
                    st.warning(f"Are you sure you want to delete project **{proj['name']}**?")
                    d1, d2 = st.columns(2)
                    if d1.button("🗑️ Delete", key=f"do_del_{proj['id']}",
                                 use_container_width=True, type="primary"):
                        delete_project(proj["id"])
                        st.session_state.pop(f"confirm_del_proj_{proj['id']}", None)
                        st.rerun()
                    if d2.button("Cancel", key=f"cancel_del_{proj['id']}",
                                 use_container_width=True):
                        st.session_state.pop(f"confirm_del_proj_{proj['id']}", None)
                        st.rerun()