import joblib

# Load the basic model pipeline
pipeline = joblib.load('basic_portfolio_model.pkl')

input_data = {
    'Salary': 150000,
    'Expenses': 100000,
    'Savings': 50000,
    'Lifecycle Stage': 'Mid-Career',
    'Risk Appetite': 'Medium',
    'Investment Horizon': 'Long-term'
}

# Convert categorical features (FIXED SYNTAX)
input_data['Lifecycle Stage'] = pipeline['mappings']['lifecycle'][input_data['Lifecycle Stage']]  # Added closing ]
input_data['Risk Appetite'] = pipeline['mappings']['risk'][input_data['Risk Appetite']]  # Added closing ]
input_data['Investment Horizon'] = pipeline['mappings']['horizon'][input_data['Investment Horizon']]  # Added closing ]

# Create feature array in correct order
X = [
    input_data['Salary'],
    input_data['Expenses'],
    input_data['Savings'],
    input_data['Lifecycle Stage'],
    input_data['Risk Appetite'],
    input_data['Investment Horizon']
]

# Scale and predict
X_scaled = pipeline['scaler'].transform([X])
pred = pipeline['model'].predict(X_scaled)[0]

# Normalize and format
total = pred.sum()
final_allocation = {
    'Equity': round((pred[0]/total)*100, 1),
    'Debt': round((pred[1]/total)*100, 1),
    'Gold': round((pred[2]/total)*100, 1),
    'FD/Cash': round((pred[3]/total)*100, 1)
}

print("Recommended Portfolio:")
for asset, perc in final_allocation.items():
    print(f"{asset}: {perc}%")
print(f"Total: {sum(final_allocation.values())}%")