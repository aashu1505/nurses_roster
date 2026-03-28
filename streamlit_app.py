import streamlit as st
import pandas as pd

st.set_page_config(page_title="GMC Akola - Nurses Roster", layout="wide")

st.title("🏥 GMC Akola Nurses Duty Roster")
st.subheader("Weekly Demand Submission")

# 1. Setup Data
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
# You can edit this list below to add your actual staff names!
nurses = ["Nurse A", "Nurse B", "Nurse C", "Nurse D", "Nurse E"]
shifts = ["Off", "Morning (M)", "Evening (E)", "Night (N)"]

# Initialize the roster in session state if it doesn't exist
if 'roster_data' not in st.session_state:
    st.session_state.roster_data = pd.DataFrame(index=nurses, columns=days).fillna("None")

# 2. Sidebar: Weekly Form
with st.sidebar:
    st.header("Submit Weekly Demands")
    selected_nurse = st.selectbox("Select Your Name", nurses)
    
    st.write(f"Select shifts for **{selected_nurse}**:")
    
    # Create a dictionary to hold the week's selections
    weekly_choices = {}
    for day in days:
        weekly_choices[day] = st.selectbox(f"{day}", shifts, key=f"{selected_nurse}_{day}")
    
    if st.button("Add Demands to Chart"):
        # Update the dataframe for the selected nurse
        for day, shift in weekly_choices.items():
            st.session_state.roster_data.at[selected_nurse, day] = shift
        st.success(f"Updated schedule for {selected_nurse}!")

# 3. Main Display
st.write("### Current Duty Chart")
st.table(st.session_state.roster_data)

if st.button("Clear All Demands"):
    st.session_state.roster_data = pd.DataFrame(index=nurses, columns=days).fillna("None")
    st.rerun()