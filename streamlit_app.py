import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="GMC Akola - Nurses Roster", layout="wide")

st.title("🏥 GMC Akola Nurses Duty Roster")

# 1. Setup Constants
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
working_shifts = ["Morning (M)", "Evening (E)", "Night (N)"]

if 'nurse_list' not in st.session_state:
    st.session_state.nurse_list = ["Nurse A", "Nurse B", "Nurse C", "Nurse D", "Nurse E"]

if 'roster_data' not in st.session_state:
    st.session_state.roster_data = pd.DataFrame("Pending", index=st.session_state.nurse_list, columns=days)

# --- SIDEBAR: STAFF MANAGEMENT ---
with st.sidebar:
    st.header("👥 Staff Management")
    new_nurse = st.text_input("Add New Nurse Name:")
    if st.button("➕ Add Nurse"):
        if new_nurse and new_nurse not in st.session_state.nurse_list:
            st.session_state.nurse_list.append(new_nurse)
            new_row = pd.Series(["Pending"] * len(days), index=days, name=new_nurse)
            st.session_state.roster_data = pd.concat([st.session_state.roster_data, new_row.to_frame().T])
            st.rerun()

    nurse_to_delete = st.selectbox("Remove a Nurse:", st.session_state.nurse_list)
    if st.button("🗑️ Delete Selected Nurse"):
        if len(st.session_state.nurse_list) > 1:
            st.session_state.nurse_list.remove(nurse_to_delete)
            st.session_state.roster_data = st.session_state.roster_data.drop(nurse_to_delete)
            st.rerun()

    st.divider()

    # --- SIDEBAR: INDIVIDUAL DEMANDS ---
    st.header("📅 Individual Demands")
    selected_nurse = st.selectbox("Select Nurse for Demands", st.session_state.nurse_list)
    
    with st.expander(f"Set preferences for {selected_nurse}"):
        for day in days:
            current_val = st.session_state.roster_data.at[selected_nurse, day]
            options = ["Pending", "Off"] + working_shifts
            idx = options.index(current_val) if current_val in options else 0
            
            choice = st.selectbox(f"{day}", options, index=idx, key=f"pref_{selected_nurse}_{day}")
            st.session_state.roster_data.at[selected_nurse, day] = choice
        st.success("Preferences saved to table!")

    st.divider()

    # --- SIDEBAR: SMART MAGIC BUTTON WITH REST RULES ---
    st.header("🪄 Roster Tools")
    if st.button("✨ Generate Full Roster"):
        error_days = []
        
        for i, day in enumerate(days):
            # 1. Identify what is already filled by demands
            current_day_assignments = st.session_state.roster_data[day].tolist()
            filled_working_shifts = [s for s in current_day_assignments if s in working_shifts]
            
            # 2. Identify which working shifts are still needed
            needed_shifts = [s for s in working_shifts if s not in filled_working_shifts]
            
            # 3. Available Nurses (exclude those who had Night (N) yesterday)
            available_nurses = []
            for nurse in st.session_state.nurse_list:
                # Rule: If yesterday was Night, today MUST be Pending/Off (Post-Night Off)
                if i > 0:
                    yesterday = days[i-1]
                    if st.session_state.roster_data.at[nurse, yesterday] == "Night (N)":
                        # If they were assigned Night yesterday, ensure they are Off today
                        if st.session_state.roster_data.at[nurse, day] == "Pending":
                            st.session_state.roster_data.at[nurse, day] = "Off"
                        continue # Skip to next nurse, they can't work today
                
                # Only add to available if they are currently "Pending"
                if st.session_state.roster_data.at[nurse, day] == "Pending":
                    available_nurses.append(nurse)
            
            # 4. Try to fill needed shifts
            if len(available_nurses) < len(needed_shifts):
                error_days.append(day)
            else:
                random.shuffle(available_nurses)
                for shift in needed_shifts:
                    nurse = available_nurses.pop()
                    st.session_state.roster_data.at[nurse, day] = shift
                
                # Remaining pending nurses get "Off"
                for nurse in available_nurses:
                    st.session_state.roster_data.at[nurse, day] = "Off"
        
        if error_days:
            st.error(f"⚠️ Coverage Error on: {', '.join(error_days)}. Remember: Nurses who work Night shifts MUST get the next day off. Add more staff or change demands!")
        else:
            st.balloons()
            st.success("Roster generated with Post-Night Off rules applied!")

# --- MAIN DISPLAY ---
st.write("### 📋 Current Duty Chart")
st.data_editor(st.session_state.roster_data, use_container_width=True)

if