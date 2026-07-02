
import streamlit as st

from api.client import get_labels, get_tasks, create_label, update_label, delete_label
from utils.ui import inject_css, render_sidebar, label_pill_html

st.set_page_config(page_title="Labels · TaskPlanner", page_icon="🏷️", layout="wide")
inject_css()
render_sidebar()

st.title("🏷️ Labels")
st.caption("Create and manage labels to categorize tasks more easily")

labels = get_labels()
tasks  = get_tasks()

# Count tasks using each label
label_usage = {}
for t in tasks:
    for lid in t.get("label_ids", []):
        label_usage[lid] = label_usage.get(lid, 0) + 1

_, btn_col = st.columns([6, 1])
with btn_col:
    if st.button("➕ New Label", use_container_width=True, type="primary"):
        st.session_state["show_create_label"] = True

if st.session_state.get("show_create_label"):
    with st.container(border=True):
        st.markdown("#### Create new label")
        lc1, lc2 = st.columns([3, 2])
        new_lname = lc1.text_input("Label name *", placeholder="e.g. Urgent, Study...")
        new_lcolor = lc2.color_picker("Color", value="#185FA5")

        # Preview
        if new_lname:
            st.markdown(
                "**Preview:** " + label_pill_html(new_lname, new_lcolor),
                unsafe_allow_html=True,
            )

        bc1, bc2 = st.columns(2)
        if bc1.button("💾 Save Label", use_container_width=True, type="primary"):
            if new_lname.strip():
                create_label(new_lname.strip(), new_lcolor)
                st.session_state.pop("show_create_label", None)
                st.success(f"✅ Label **{new_lname}** created")
                st.rerun()
            else:
                st.error("Label name cannot be empty.")
        if bc2.button("✕ Cancel", use_container_width=True):
            st.session_state.pop("show_create_label", None)
            st.rerun()

st.divider()

if not labels:
    st.info("No labels yet. Create your first label!")
else:
    # Header row
    h1, h2, h3, h4 = st.columns([1, 4, 2, 2])
    h1.markdown("<span style='font-size:11px;color:#999;'>COLOR</span>", unsafe_allow_html=True)
    h2.markdown("<span style='font-size:11px;color:#999;'>LABEL NAME</span>", unsafe_allow_html=True)
    h3.markdown("<span style='font-size:11px;color:#999;'>TASKS</span>", unsafe_allow_html=True)
    h4.markdown("<span style='font-size:11px;color:#999;'>ACTION</span>", unsafe_allow_html=True)

    st.markdown("<hr style='margin:6px 0;border-color:#eee;'>", unsafe_allow_html=True)

    for label in labels:
        usage = label_usage.get(label["id"], 0)
        c1, c2, c3, c4 = st.columns([1, 4, 2, 2])

        # Color dot
        c1.markdown(
            f"<div style='width:18px;height:18px;border-radius:50%;"
            f"background:{label['color']};margin-top:6px;'></div>",
            unsafe_allow_html=True,
        )

        # Name + pill preview
        c2.markdown(
            label_pill_html(label["name"], label["color"]),
            unsafe_allow_html=True,
        )

        # Task count
        c3.markdown(
            f"<div style='font-size:13px;color:#555;margin-top:4px;'>"
            f"{'📌 ' + str(usage) + ' task' if usage else '—'}</div>",
            unsafe_allow_html=True,
        )

        # Delete button
        with c4:
            if st.button("🗑️ Delete", key=f"del_label_{label['id']}",
                         use_container_width=True):
                st.session_state[f"confirm_del_label_{label['id']}"] = True

        # Delete confirmation
        if st.session_state.get(f"confirm_del_label_{label['id']}"):
            warn_text = (
                f"Deleting label **{label['name']}** will remove it from "
                f"**{usage} task(s)**. Continue?"
                if usage else
                f"Delete label **{label['name']}**?"
            )
            st.warning(warn_text)
            d1, d2 = st.columns(2)
            if d1.button("🗑️ Confirm delete", key=f"do_del_label_{label['id']}",
                         use_container_width=True, type="primary"):
                delete_label(label["id"])
                st.session_state.pop(f"confirm_del_label_{label['id']}", None)
                st.rerun()
            if d2.button("Cancel", key=f"cancel_del_label_{label['id']}",
                         use_container_width=True):
                st.session_state.pop(f"confirm_del_label_{label['id']}", None)
                st.rerun()

        st.markdown("<hr style='margin:4px 0;border-color:#f0f0f0;'>",
                    unsafe_allow_html=True)

if labels and any(label_usage.values()):
    st.divider()
    st.subheader("📊 Label Statistics")

    import pandas as pd
    chart_data = {
        l["name"]: label_usage.get(l["id"], 0)
        for l in labels
        if label_usage.get(l["id"], 0) > 0
    }
    if chart_data:
        df = pd.DataFrame.from_dict(
            chart_data, orient="index", columns=["Tasks"]
        )
        st.bar_chart(df, color="#185FA5", height=200)