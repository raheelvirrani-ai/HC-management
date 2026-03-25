import pandas as pd

# SETTINGS
cook_rate = 16
foh_rate = 13
tax_multiplier = 1.168
target_labour_pct = 30

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

rows = []
total_wasted = 0

print("\nEnter hourly data:\n")

for h in hours:
    sales = float(input(f"{h} Sales (£): "))
    foh = int(input(f"{h} FOH staff: "))
    cooks = int(input(f"{h} Cooks: "))
    
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

print("\n--- STAFFING ANALYSIS ---")
print(df)

print("\n--- SUMMARY ---")
print(f"Total Wasted Labour: £{total_wasted:.0f}")
