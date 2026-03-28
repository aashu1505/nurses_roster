import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="GMC Akola - Nurses Roster", layout="wide")

st.title("🏥 GMC Akola Nurses Duty Roster")

# 1. Setup & Session State Management
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
shifts = ["Morning (M)", "Evening (E)", "Night (N)", "Off"]

# Initialize nurse list if it doesn't exist
if 'nurse_list' not in st.session_state:
    st.session_state.nurse_list = ["Nurse A", "Nurse B", "Nurse C"]

# Initialize roster data if it doesn't exist or if staff changed
if 'roster_data' not in st.session_state:
    st.session_state.roster_data = pd.DataFrame("Pending", index=st.session_state.nurse_list, columns=days)

# --- SIDEBAR: STAFF MANAGEMENT ---
with st.sidebar:
    st.header("👥 Staff Management")
    
    # Add a Nurse
    new_nurse = st.text_input("Add New Nurse Name:")
    if st.button("➕ Add Nurse"):
        if new_nurse and new_nurse not in st.session_state.nurse_list:
            st.session_state.nurse_list.append(new_nurse)
            # Update the dataframe to include the new nurse
            new_row = pd.Series(["Pending"] * len(days), index=days, name=new_nurse)
            st.session_state.roster_data = pd.concat([st.session_state.roster_data, new_row.to_frame().T])
            st.rerun()

    # Delete a Nurse
    nurse_to_delete = st.selectbox("Remove a Nurse:", st.session_state.nurse_list)
    if st.button("🗑️ Delete Selected Nurse"):
        if len(st.session_state.nurse_list) > 1:
            st.session_state.nurse_list.remove(nurse_to_delete)
            st.session_state.roster_data = st.session_state.roster_data.drop(nurse_to_delete)
            st.rerun()
        else:
            st.error("You must have at least one nurse on the roster!")

    st.divider()

    # --- SIDEBAR: DEMANDS ---
    st.header("📅 Individual Demands")
    selected_nurse = st.selectbox("Select Your Name", st.session_state.nurse_list)
    
    with st.expander(f"Set preferences for {selected_nurse}"):
        weekly_choices = {}
        for day in days:
            weekly_choices[day] = st.selectbox(f"{day}", ["Pending"] + shifts, key=f"pref_{selected_nurse}_{day}")
        
        if st.button("Save My Preferences"):
            for day, shift in weekly_choices.items():
                if shift != "Pending":
                    st.session_state.roster_data.at[selected_nurse, day] = shift
            st.success("Preferences Saved!")

    st.divider()

    # --- SIDEBAR: MAGIC BUTTON ---
    st.header("🪄 Roster Tools")
    if st.button("✨ Generate Full Roster"):
        for day in days:
            for nurse in st.session_state.nurse_list:
                if st.session_state.roster_data.at[nurse, day] == "Pending":
                    st.session_state.roster_data.at[nurse, day] = random.choice(shifts)
        st.balloons()

# --- MAIN DISPLAY ---
st.write("### 📋 Current Duty Chart")
# Using data_editor allows you to click and type directly in the table too!
st.data_editor(st.session_state.roster_data, use_container_width=True)

if st.button("Reset All Shifts to Pending"):
    st.session_state.roster_data = pd.DataFrame("Pending", index=st.session_state.nurse_list, columns=days)
    st.rerun()