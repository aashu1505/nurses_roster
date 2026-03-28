import streamlit as st
import pandas as pd

# Set page title and icon
st.set_page_config(page_title="GMC Akola Nursing Roster", page_icon="🏥", layout="wide")

st.title("🏥 GMC Akola: Nursing Duty Chart")
st.markdown("---")

# 1. Setup - You can change these names later!
nurses = ["Nurse Priya", "Nurse Sunil", "Nurse Anita", "Nurse Rahul", "Nurse Meena"]
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
shifts = ["Morning", "Evening", "Night"]

# 2. Sidebar for Demands
st.sidebar.header("📋 Enter Nurse Demands")
st.sidebar.info("Select a nurse and their requested shift, then click 'Add Demand'.")

selected_day = st.sidebar.selectbox("Select Day", days)
selected_nurse = st.sidebar.selectbox("Select Nurse", nurses)
selected_shift = st.sidebar.selectbox("Requested Shift", ["None", "Morning", "Evening", "Night", "Off"])

# Initialize session state to store demands if not already there
if 'demands' not in st.session_state:
    st.session_state.demands = {day: {} for day in days}

if st.sidebar.button("Add Demand to Chart"):
    if selected_shift != "None":
        st.session_state.demands[selected_day][selected_nurse] = selected_shift
        st.sidebar.success(f"Added: {selected_nurse} on {selected_day}")

# 3. The Logic Function (Fair Distribution)
def generate_roster(nurses, days, demands_dict):
    roster = pd.DataFrame(index=nurses, columns=days)
    counts = {nurse: 0 for nurse in nurses}

    for day_idx, day in enumerate(days):
        available_shifts = ["Morning", "Evening", "Night"]
        assigned_today = []

        # First, Lock in the Demands
        for nurse, shift in demands_dict[day].items():
            if shift != "Off" and shift in available_shifts:
                roster.at[nurse, day] = shift
                available_shifts.remove(shift)
                assigned_today.append(nurse)
                counts[nurse] += 1
            else:
                roster.at[nurse, day] = "Off"
                assigned_today.append(nurse)

        # Second, Fill Gaps Fairly
        for shift in available_shifts:
            candidates = [n for n in nurses if n not in assigned_today]
            
            # Rule: No Morning after a Night shift
            if day_idx > 0:
                yesterday = days[day_idx-1]
                candidates = [n for n in candidates if not (shift == "Morning" and roster.at[n, yesterday] == "Night")]
            
            if candidates:
                # Pick the nurse with the lowest total shift count
                chosen_nurse = min(candidates, key=lambda n: counts[n])
                roster.at[chosen_nurse, day] = shift
                assigned_today.append(chosen_nurse)
                counts[chosen_nurse] += 1

        # Third, Everyone else is Off
        for nurse in nurses:
            if pd.isna(roster.at[nurse, day]):
                roster.at[nurse, day] = "Off"
    return roster

# 4. Display the Table
final_roster = generate_roster(nurses, days, st.session_state.demands)

st.subheader("Weekly Schedule")
st.table(final_roster)

# Clear button
if st.button("Reset All Demands"):
    st.session_state.demands = {day: {} for day in days}
    st.rerun()