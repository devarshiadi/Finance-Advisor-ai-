import datetime
import math

# --- Helper Functions (mostly unchanged) ---
def get_float(prompt):
    """Helper to get a non-negative float from the user."""
    while True:
        try:
            val_str = input(prompt).strip()
            if not val_str:
                raise ValueError("Input cannot be empty.")
            val = float(val_str)
            if val < 0:
                raise ValueError("Please enter a non-negative number.")
            return val
        except ValueError as e:
            print(f"Invalid input: {e}")

def get_int(prompt):
    """Helper to get a non-negative integer from the user."""
    while True:
        try:
            val_str = input(prompt).strip()
            if not val_str:
                raise ValueError("Input cannot be empty.")
            val = int(val_str)
            if val < 0:
                raise ValueError("Please enter a non-negative whole number.")
            return val
        except ValueError as e:
            print(f"Invalid input: {e}")

def yes_no(prompt):
    """Helper to get a yes/no response."""
    while True:
        resp = input(prompt + " (y/n): ").strip().lower()
        if resp in ("y", "yes"):
            return True
        if resp in ("n", "no"):
            return False
        print("Please answer 'y' or 'n'.")

# --- Simplified Profile and Financials Gathering ---

def get_user_profile():
    """Gathers lifecycle stage, risk appetite, and investment horizon."""
    print("\n--- Let's Understand Your Investor Profile ---")

    # 1. Lifecycle Stage
    print("\nWhich of these best describes your current life stage?")
    lifecycle_options = {
        "1": "Student (Focus: Learning, initial savings)",
        "2": "Early Career (20s-early 30s, Focus: Growth, accumulation)",
        "3": "Mid-Career (Mid 30s-late 40s, Focus: Balancing growth & responsibilities)",
        "4": "Late Career/Pre-Retirement (50s+, Focus: Capital preservation, income generation)",
        "5": "Retired (Focus: Sustainable income, capital preservation)"
    }
    for key, value in lifecycle_options.items():
        print(f"{key}. {value}")
    while True:
        choice = input("Enter number (1-5): ").strip()
        if choice in lifecycle_options:
            lifecycle_stage = lifecycle_options[choice].split('(')[0].strip() # Get "Student", "Early Career" etc.
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

    # 2. Risk Appetite
    print("\nHow would you describe your risk tolerance for investments?")
    risk_options = {
        "1": "Low (Prefer safety and capital preservation, okay with lower returns)",
        "2": "Medium (Willing to take some risk for moderate growth, comfortable with some fluctuations)",
        "3": "High (Willing to take significant risk for potentially high returns, can handle large fluctuations)"
    }
    for key, value in risk_options.items():
        print(f"{key}. {value}")
    while True:
        choice = input("Enter number (1-3): ").strip()
        if choice == "1": risk_appetite = "low"; break
        elif choice == "2": risk_appetite = "medium"; break
        elif choice == "3": risk_appetite = "high"; break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

    # 3. Investment Horizon
    print("\nWhat is your general investment time horizon for the majority of your savings?")
    horizon_options = {
        "1": "Short-term (Less than 3 years)",
        "2": "Medium-term (3-7 years)",
        "3": "Long-term (More than 7 years)"
    }
    for key, value in horizon_options.items():
        print(f"{key}. {value}")
    while True:
        choice = input("Enter number (1-3): ").strip()
        if choice == "1": investment_horizon = "short-term"; break
        elif choice == "2": investment_horizon = "medium-term"; break
        elif choice == "3": investment_horizon = "long-term"; break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

    return lifecycle_stage, risk_appetite, investment_horizon

def get_financial_details():
    """Gets annual package, monthly in-hand salary, and total monthly expenses."""
    print("\n--- Let's Get Your Financial Details ---")
    annual_package = get_float("What is your approximate annual salary package (CTC)? \u20B9 ")

    # Simplified monthly in-hand: Ask directly or provide a rough estimate and ask for correction
    print(f"\nBased on an annual package of \u20B9 {annual_package:.2f}, your monthly in-hand salary might be around \u20B9 {annual_package / 14:.2f} to \u20B9 {annual_package / 13:.2f} (this is a rough estimate).")
    monthly_in_hand_salary = get_float("What is your actual average monthly in-hand salary? \u20B9 ")

    total_monthly_expenses = get_float("What are your total estimated monthly expenses (all inclusive)? \u20B9 ")

    monthly_savings = monthly_in_hand_salary - total_monthly_expenses

    print(f"\nBased on your input:")
    print(f"  Monthly In-hand Salary: \u20B9 {monthly_in_hand_salary:.2f}")
    print(f"  Total Monthly Expenses: \u20B9 {total_monthly_expenses:.2f}")
    if monthly_savings > 0:
        print(f"  Calculated Monthly Savings: \u20B9 {monthly_savings:.2f}")
    else:
        print(f"  Calculated Monthly Deficit: \u20B9 {abs(monthly_savings):.2f}")
        print("  It seems your expenses exceed your income. Please review your budget.")

    return monthly_in_hand_salary, total_monthly_expenses, monthly_savings

# --- Simplified Investment Allocation Logic ---
def allocate_savings_simplified(savings, risk_profile, horizon, lifecycle):
    """
    Determines investment allocation percentages based on simplified profile.
    Returns a dictionary of { "Asset Class": percentage, ... }
    """
    allocations = {}
    justification_points = [
        f"This allocation considers your {risk_profile} risk profile, {horizon} horizon, and {lifecycle} stage."
    ]

    # Prioritize Emergency Fund if not explicitly covered or if savings are first-time
    # For simplicity, this version assumes user will manage EF separately or this is for surplus post-EF.
    # A more robust version would inquire about EF status.

    if risk_profile == "low":
        allocations = {
            "Fixed Deposits / Recurring Deposits (Safety & Stability)": 0.35,
            "Debt Mutual Funds (Liquid/Short Duration - Better than savings account returns)": 0.30,
            "Gold (SGBs/ETFs - Inflation Hedge, Diversification)": 0.10,
            "Equity MFs (Large Cap/Index Funds - Long-term inflation beating, low volatility equity)": 0.15,
            "Cash / Savings Account (Immediate Liquidity)": 0.10
        }
        justification_points.append("- Focus on capital preservation and stable returns.")
        justification_points.append("- Suitable for short-term goals or very conservative investors.")
        if horizon != "short-term":
            justification_points.append("- Even with a longer horizon, a 'low' risk choice emphasizes safety above all.")


    elif risk_profile == "medium":
        allocations = {
            "Equity MFs (Diversified - Large & Mid Cap/Flexi Cap SIPs for growth)": 0.45,
            "Debt Mutual Funds (For stability and portfolio balance)": 0.25,
            "Fixed Deposits / PPF (Secure, long-term component)": 0.10,
            "Gold (SGBs/ETFs - Diversification)": 0.10,
            "Equity MFs (International - For global diversification, if comfortable)": 0.05, # Optional
            "Cash / Savings Account (Buffer)": 0.05
        }
        justification_points.append("- Aims for a balance between growth (equity) and stability (debt, gold).")
        justification_points.append("- Suitable for medium to long-term goals.")
        if lifecycle in ["Early Career", "Student"] and horizon == "long-term":
            justification_points.append("- Your stage and horizon allow for good equity exposure for wealth creation.")
            # Could slightly increase equity for very young, long-term, medium risk.
            # allocations["Equity MFs (Diversified - Large & Mid Cap/Flexi Cap SIPs for growth)"] = 0.50
            # allocations["Debt Mutual Funds (For stability and portfolio balance)"] = 0.20

    elif risk_profile == "high":
        allocations = {
            "Equity MFs (Aggressive Growth - Mid/Small Cap, Thematic SIPs, with research)": 0.60,
            "Equity MFs (International - Global growth opportunities)": 0.15,
            "Direct Stocks (If experienced & well-researched, otherwise add to Equity MFs)": 0.10, # User needs to self-assess this.
            "Debt Mutual Funds (Strategic, for some diversification)": 0.05,
            "Gold (SGBs/ETFs - Tactical Diversification)": 0.05,
            "Alternative Inv. (REITs/InvITs - very small, if understood & suitable, else to Equity)": 0.05
        }
        justification_points.append("- Focuses on maximizing long-term growth potential, accepting higher volatility.")
        justification_points.append("- Best suited for long-term goals and investors comfortable with significant market swings.")
        if lifecycle not in ["Early Career", "Mid-Career"] and horizon == "long-term":
             justification_points.append(f"- CAUTION: High risk at {lifecycle} stage needs careful consideration of your overall financial stability and nearness to needing funds.")
        if horizon != "long-term":
            justification_points.append(f"- CAUTION: High risk for a {horizon} horizon is generally not advisable. Ensure goals truly allow for this risk.")


    # Normalize percentages to ensure they sum to 100%
    current_total_percentage = sum(allocations.values())
    if abs(current_total_percentage - 1.0) > 0.001: # If not already 100%
        factor = 1.0 / current_total_percentage
        normalized_allocations = {k: v * factor for k, v in allocations.items()}
        # Small check to ensure the largest component doesn't become negative if factor is weird (shouldn't happen with positive inputs)
        # And ensure no tiny values are left that make no sense, e.g. less than 0.5% could be merged.
        # For simplicity, we'll assume initial definitions are close enough.
        final_allocations = {}
        temp_sum = 0
        for asset, perc in normalized_allocations.items():
            # Round to sensible points e.g. 1 decimal for percentage display
            # but use more precision for calculation
            final_allocations[asset] = perc
            temp_sum += perc

        # Final check and adjustment of the largest item if sum isn't perfect due to rounding during normalization.
        if abs(temp_sum - 1.0) > 0.0001:
            diff = 1.0 - temp_sum
            if final_allocations: # Check if dict is not empty
                 # Find largest item to adjust
                largest_item_key = max(final_allocations, key=final_allocations.get)
                final_allocations[largest_item_key] += diff
        allocations = final_allocations


    return allocations, justification_points

def display_investment_plan(monthly_savings, allocations, justification):
    """Displays the final investment plan and justification."""
    print("\n\n--- Your Personalized Investment Allocation Plan ---")
    print(f"Based on your monthly savings of \u20B9 {monthly_savings:.2f}:\n")

    print("Suggested Allocation:")
    print("---------------------------------------------------------------------------")
    print(f"{'Asset Class/Instrument':<50} | {'Percentage':>12} | {'Amount (₹)':>12}")
    print("---------------------------------------------------------------------------")
    if not allocations: # Should not happen if logic is correct
        print("No specific allocation generated. Please review inputs or consult an advisor.")
        return

    total_allocated_amount_check = 0
    for asset, percentage in allocations.items():
        amount = monthly_savings * percentage
        total_allocated_amount_check += amount
        print(f"{asset:<50} | {percentage*100:>11.1f}% | {amount:>11.2f}")
    print("---------------------------------------------------------------------------")
    print(f"{'TOTAL':<50} | {'100.0%':>12} | {total_allocated_amount_check:>11.2f}")


    print("\nWhy these allocations?")
    for point in justification:
        print(f"- {point}")
    print("\n- Learn more about general investing principles at: https://www.investopedia.com/financial-advisor/asset-allocation/\n"
          "  and for Indian context: https://www.amfiindia.com (Investor Education section)")


def provide_general_financial_tips(lifecycle_stage, monthly_savings, original_salary):
    """Provides general financial tips."""
    print("\n--- General Financial Tips ---")
    tips = []
    if monthly_savings <= 0 and original_salary > 0 :
        tips.append("- Your expenses currently meet or exceed your income. Focus on creating a budget to identify areas to cut back or explore ways to increase your income.")
    elif original_salary > 0:
        savings_rate = (monthly_savings / original_salary) * 100
        tips.append(f"- Your current savings rate is approximately {savings_rate:.1f}%. Aim for at least 20-30% if possible, especially in accumulation stages.")
        if savings_rate < 15:
             tips.append("- Consider reviewing discretionary spending to boost your savings rate.")

    tips.append("- Build & Maintain an Emergency Fund: Aim for 3-6 months of essential living expenses in a safe, liquid account (e.g., savings account, liquid mutual fund). This is your top priority before aggressive investing.")
    tips.append("- Get Adequately Insured: Ensure you have sufficient health insurance for yourself and your family. If you have dependents, a term life insurance policy is crucial.")
    tips.append("- Invest Regularly & Be Disciplined: Consistency through SIPs (Systematic Investment Plans) is key, especially for long-term goals. Don't try to time the market.")
    tips.append("- Review Periodically: Revisit your financial plan and investments at least annually, or when major life events occur (marriage, new job, child, etc.).")
    tips.append("- Understand Your Investments: Before investing in any product, understand its risks, costs (like expense ratios for MFs), and how it fits your goals.")

    if lifecycle_stage == "Student" or lifecycle_stage == "Early Career":
        tips.append("- Focus on upskilling and career growth to increase your earning potential. Your human capital is your biggest asset at this stage.")
    if lifecycle_stage == "Late Career/Pre-Retirement" or lifecycle_stage == "Retired":
        tips.append("- Plan for healthcare expenses in retirement. Consider if your current investments align with generating regular income if needed.")

    for tip in tips:
        print(f"* {tip}")

# --- Main Program Flow (Simplified) ---
def main_simplified():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║          Simplified Monthly Savings Allocator                ║")
    print(f"║                 Today's Date: {datetime.date.today().strftime('%Y-%m-%d')}                  ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("\nWelcome! This tool will help you allocate your monthly savings.")
    print("This is for educational purposes and NOT financial advice.\n")

    # 1. Get User Profile
    lifecycle, risk, horizon = get_user_profile()
    print(f"\nYour Profile Summary: Lifecycle: {lifecycle}, Risk: {risk.capitalize()}, Horizon: {horizon.capitalize()}")

    # 2. Get Financial Details
    salary, expenses, savings = get_financial_details()

    if savings <= 0:
        print("\nSince you don't have a monthly surplus, investment allocation is not applicable now.")
        print("Focus on budgeting and increasing savings first.")
    else:
        # 3. Allocate Savings
        allocations_dict, justification_list = allocate_savings_simplified(savings, risk, horizon, lifecycle)

        # 4. Display Plan
        display_investment_plan(savings, allocations_dict, justification_list)

    # 5. Provide General Tips
    provide_general_financial_tips(lifecycle, savings, salary)

    # 6. Disclaimer
    print("\n\n--- Disclaimer ---")
    print("The information and suggestions provided by this script are for general guidance and educational purposes ONLY.")
    print("This does NOT constitute financial, investment, tax, or legal advice.")
    print("Investment decisions involve risks. Past performance is not indicative of future results.")
    print("Asset allocation models are generalized and may not be suitable for your individual circumstances.")
    print("It is strongly recommended to consult with a SEBI-registered Investment Adviser or a qualified financial professional for personalized advice.")

    print("\nBudget calculation and investment suggestions complete. Plan wisely!\n")

if __name__ == "__main__":
    main_simplified()