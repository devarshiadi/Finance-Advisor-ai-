import joblib
import pandas as pd

# Load enhanced model pipeline
pipeline = joblib.load('enhanced_portfolio_model.pkl')

# Sample input (MUST include Profession/City)
test_case = {
    'Profession': 'Software Engineer',
    'City': 'Mumbai',
    'Salary': 150000,
    'Expenses': 100000,
    'Savings': 50000,
    'Lifecycle Stage': 'Mid-Career',
    'Risk Appetite': 'Medium',
    'Investment Horizon': 'Long-term'
}

# Convert categorical features
test_case['Profession'] = pipeline['profession_encoder'].transform([test_case['Profession']])[0]
test_case['City'] = pipeline['city_encoder'].transform([test_case['City']])[0]
test_case['Lifecycle Stage'] = pipeline['mappings']['lifecycle'][test_case['Lifecycle Stage']]
test_case['Risk Appetite'] = pipeline['mappings']['risk'][test_case['Risk Appetite']]
test_case['Investment Horizon'] = pipeline['mappings']['horizon'][test_case['Investment Horizon']]

# Create feature array IN EXACT ORDER:
# ['Profession', 'City', 'Salary', 'Expenses', 'Savings',
#  'Lifecycle Stage', 'Risk Appetite', 'Investment Horizon']
X = [
    test_case['Profession'],
    test_case['City'],
    test_case['Salary'],
    test_case['Expenses'],
    test_case['Savings'],
    test_case['Lifecycle Stage'],
    test_case['Risk Appetite'],
    test_case['Investment Horizon']
]

# Scale and predict
X_scaled = pipeline['scaler'].transform([X])
pred = pipeline['model'].predict(X_scaled)[0]

# Normalize to 100%
total = pred.sum()
final_allocation = {
    'Equity': round((pred[0]/total)*100, 1),
    'Debt': round((pred[1]/total)*100, 1),
    'Gold': round((pred[2]/total)*100, 1),
    'FD/Cash': round((pred[3]/total)*100, 1)
}

print("Enhanced Model Recommended Portfolio:")
for asset, perc in final_allocation.items():
    print(f"{asset}: {perc}%")
print(f"Total: {sum(final_allocation.values())}%")