# streamlit_daily_roster.py
import streamlit as st
import pandas as pd
import math

# SETTINGS
cook_rate = 16
foh_rate = 13
tax_multiplier = 1.168
max_shift_length = 4  # max hours per shift
hours = ["11AM","12PM","1PM","2PM","3PM","4PM",
         "5PM","6PM","7PM","8PM","9PM","10PM"]

def required_staff(sales):
    if sales < 200:
        return 2, 1
    elif sales < 400:
        return 3, 1
    elif sales < 700:
        return 4, 2
    else:
        return 5, 2

def color_status(row):
    if row["Status"] == "Overstaffed":
        return ['background-color: #FF9999']*len(row)
    elif row["Status"] == "Understaffed":
        return ['background-color: #FFEB99']*len(row)
    else:
        return ['background-color: #99FF99']*len(row)

st.title("📅 Full Daily Roster Generator")
st.write("Enter forecast sales, generate employee shifts, and view total hours per employee.")

# Input: hourly sales
sales_forecast = []
for h in hours:
    sales = st.number_input(f"Forecast Sales (£) {h}", min_value=0.0, step=1.0, key=f"sales_{h}")
    sales_forecast.append((h, sales))

# Helper: assign shifts to employees
def assign_shifts(req_count, role):
    employee_shifts = {}  # key=employee_id, value=list of hours
    emp_counter = 1
    start_idx = 0
    while start_idx < len(hours):
        end_idx = min(start_idx + max_shift_length - 1, len(hours)-1)
        for i in range(req_count):
            emp_id = f"{role} E{emp_counter}"
            emp_hours = hours[start_idx:end_idx+1]
            if emp_id not in employee_shifts:
                employee_shifts[emp_id] = emp_hours
            else:
                employee_shifts[emp_id].extend(emp_hours)
            emp_counter += 1
        start_idx += max_shift_length
    return employee_shifts

# Generate shifts
foh_all = {}
cook_all = {}
rows = []
total_wasted = 0

for h, sales in sales_forecast:
    req_foh, req_cooks = required_staff(sales)
    actual_foh = req_foh
    actual_cooks = req_cooks
    
    actual_cost = (actual_foh * foh_rate + actual_cooks * cook_rate) * tax_multiplier
    optimal_cost = (req_foh * foh_rate + req_cooks * cook_rate) * tax_multiplier
    labour_pct = (actual_cost / sales * 100) if sales > 0 else 0
    wasted_cost = max(0, actual_cost - optimal_cost)
    total_wasted += wasted_cost
    
    status = "Optimal"
    action = "OK"
    
    # Assign employee shifts
    foh_shifts = assign_shifts(actual_foh, "FOH")
    cook_shifts = assign_shifts(actual_cooks, "Cook")
    
    # Merge into global dict for full daily roster
    for k, v in foh_shifts.items():
        if k not in foh_all:
            foh_all[k] = set(v)
        else:
            foh_all[k].update(v)
    for k, v in cook_shifts.items():
        if k not in cook_all:
            cook_all[k] = set(v)
        else:
            cook_all[k].update(v)
    
    # Only show shifts relevant to this hour
    foh_for_hour = [k for k, v in foh_shifts.items() if h in v]
    cook_for_hour = [k for k, v in cook_shifts.items() if h in v]
    
    rows.append([
        h, sales, actual_foh, actual_cooks,
        req_foh, req_cooks,
        round(actual_cost,1),
        round(labour_pct,1),
        round(wasted_cost,1),
        status,
        action,
        ", ".join(foh_for_hour),
        ", ".join(cook_for_hour)
    ])

# Hourly table
df = pd.DataFrame(rows, columns=[
    "Hour","Forecast Sales","FOH","Cooks",
    "Req FOH","Req Cooks",
    "Cost","Labour %","Wasted £","Status","Action",
    "FOH Shifts","Cook Shifts"
])

st.subheader("📊 Hourly Staffing & Shifts")
st.dataframe(df.style.apply(color_status, axis=1))

st.subheader("💰 Summary")
st.write(f"**Total Wasted Labour:** £{total_wasted:.0f}")

# Daily FOH roster
st.subheader("🧑‍🍳 Daily FOH Roster")
foh_roster = pd.DataFrame([
    {"Employee": emp, "Hours": sorted(list(hours_set)), "Total Hours": len(hours_set)}
    for emp, hours_set in foh_all.items()
])
st.dataframe(foh_roster)

# Daily Cook roster
st.subheader("🍳 Daily Cook Roster")
cook_roster = pd.DataFrame([
    {"Employee": emp, "Hours": sorted(list(hours_set)), "Total Hours": len(hours_set)}
    for emp, hours_set in cook_all.items()
])
st.dataframe(cook_roster)

# Labour % chart
st.subheader("📈 Labour % vs Target")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10,4))
ax.plot(df["Hour"], df["Labour %"], marker='o', label="Labour %")
ax.axhline(30, color='red', linestyle='--', label="Target 30%")
ax.set_ylabel("Labour %")
ax.set_xlabel("Hour")
ax.set_title("Labour % per Hour vs Target")
ax.legend()
st.pyplot(fig)
