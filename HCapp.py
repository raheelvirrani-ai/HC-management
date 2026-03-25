# streamlit_staffing.py
import streamlit as st
import pandas as pd

# SETTINGS
cook_rate = 16
foh_rate = 13
tax_multiplier = 1.168

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

st.title("🍴 Staffing & Labour Analysis")

st.write("Enter sales and staff numbers for each hour:")

# Containers for input
hourly_data = []

for h in hours:
    st.subheader(f"{h}")
    col1, col2, col3 = st.columns(3)
    with col1:
        sales = st.number_input(f"Sales (£) {h}", min_value=0.0, step=1.0, key=f"sales_{h}")
    with col2:
        foh = st.number_input(f"FOH Staff {h}", min_value=0, step=1, key=f"foh_{h}")
    with col3:
        cooks = st.number_input(f"Cooks {h}", min_value=0, step=1, key=f"cooks_{h}")
    
    hourly_data.append((h, sales, foh, cooks))

if st.button("Calculate Staffing Analysis"):
    rows = []
    total_wasted = 0

    for h, sales, foh, cooks in hourly_data:
        req_foh, req_cooks = required_staff(sales)
        actual_cost = (foh * foh_rate + cooks * cook_rate) * tax_multiplier
        optimal_cost = (req_foh * foh_rate + req_cooks * cook_rate) * tax_multiplier
        labour_pct = (actual_cost / sales * 100) if sales > 0 else 0
        wasted_cost = max(0, actual_cost - optimal_cost)
        total_wasted += wasted_cost
        
        if foh > req_foh or cooks > req_cooks:
            status = "Overstaffed"
            action = f"Reduce {max(foh-req_foh,0)} FOH, {max(cooks-req_cooks,0)} cooks"
        elif foh < req_foh or cooks < req_cooks:
            status = "Understaffed"
            action = f"Add {max(req_foh-foh,0)} FOH, {max(req_cooks-cooks,0)} cooks"
        else:
            status = "Optimal"
            action = "OK"
        
        rows.append([
            h, sales, foh, cooks,
            req_foh, req_cooks,
            round(actual_cost,1),
            round(labour_pct,1),
            round(wasted_cost,1),
            status,
            action
        ])
    
    df = pd.DataFrame(rows, columns=[
        "Hour","Sales","FOH","Cooks",
        "Req FOH","Req Cooks",
        "Cost","Labour %","Wasted £","Status","Action"
    ])

    st.subheader("📊 Staffing Analysis")
    st.dataframe(df)

    st.subheader("💰 Summary")
    st.write(f"**Total Wasted Labour:** £{total_wasted:.0f}")
