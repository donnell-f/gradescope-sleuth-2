import streamlit as st

st.title("About Configuration")

st.write("**Assignment Name:**", st.session_state.get("saved_assn_name", "N/A"))
st.write("**Submissions Path:**", st.session_state.get("saved_assn_path", "N/A"))
st.write("**Due Date:**", st.session_state.get("saved_due_date", "N/A"))

has_late = st.session_state.get("saved_has_late_due_date", "No")
st.write("**Has Late Due Date:**", has_late)
if has_late == "Yes":
    st.write("**Late Due Date:**", st.session_state.get("saved_late_due_date", "N/A"))
