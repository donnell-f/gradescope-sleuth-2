import streamlit as st

st.title("About Configuration")

st.write("**Assignment Name:**", st.session_state.get("saved_assn_name", "N/A"))
st.write("**Submissions Path:**", st.session_state.get("saved_assn_path", "N/A"))
st.write("**Due Date:**", st.session_state.get("saved_due_date", "N/A"))

has_late = st.session_state.get("saved_has_late_due_date", "No")
st.write("**Has Late Due Date:**", has_late)
if has_late == "Yes":
    st.write("**Late Due Date:**", st.session_state.get("saved_late_due_date", "N/A"))

has_network = st.session_state.get("saved_has_network_settings", "No")
st.write("**Has Network Settings:**", has_network)
if has_network == "Yes":
    st.write("**Course ID:**", st.session_state.get("saved_course_id", "N/A"))
    st.write("**Assignment ID:**", st.session_state.get("saved_assignment_id", "N/A"))
    st.write("**remember_me cookie:**", st.session_state.get("saved_remember_me_cookie", "N/A"))
    st.write("**signed_token cookie:**", st.session_state.get("saved_signed_token_cookie", "N/A"))
