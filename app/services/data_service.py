import csv
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the path for the CSV file
# Ensure this path is correct relative to where the application runs
# For example, if main.py is in app/, and this service is called from there.
CSV_FILE_PATH = "user_financial_data.csv" 
# This will create the file in the same directory as main.py if it's in the root,
# or in the 'app' directory if main.py is in 'app' and this path is used as is.
# For consistency with the sqlite DB being in the root, let's adjust:
CSV_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_financial_data.csv")
# This places it in the project root directory (financial_advisor/)

# Define the headers for the CSV file based on 'aboutdata.txt' and additional fields
# Ensure all possible fields from all models are covered.
CSV_HEADERS = [
    'UserID', 'UserEmail', 'ModelType', 'Timestamp',
    'Name', 'Age', 'City', 'Profession', 'Salary', 'Expenses', 'Savings',
    'Lifecycle Stage', 'Risk Appetite', 'Investment Horizon',
    'Annual Salary Package', 'Monthly In-hand Salary', 'Total Monthly Expenses', # For Rule-based
    # Output fields from models (optional, but good for record keeping)
    'Equity (%)', 'Debt (%)', 'Gold (%)', 'FD/Cash (%)'
]


def initialize_csv():
    """Initializes the CSV file with headers if it doesn't exist."""
    # Ensure the directory for the CSV file exists
    os.makedirs(os.path.dirname(CSV_FILE_PATH), exist_ok=True)
    
    if not os.path.exists(CSV_FILE_PATH):
        try:
            with open(CSV_FILE_PATH, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(CSV_HEADERS)
            logger.info(f"CSV file initialized at {CSV_FILE_PATH}")
        except IOError as e:
            logger.error(f"Error initializing CSV file: {e}")

def append_data_to_csv(user_id: int, user_email: str, model_type: str, input_data: Dict[str, Any], output_data: Optional[Dict[str, Any]] = None):
    """
    Appends a new row of data to the CSV file.
    input_data should be a flat dictionary.
    output_data is the portfolio allocation.
    """
    if not os.path.exists(CSV_FILE_PATH):
        initialize_csv()

    row_data = {header: '' for header in CSV_HEADERS} # Initialize with empty strings

    # Populate common fields
    row_data['UserID'] = user_id
    row_data['UserEmail'] = user_email
    row_data['ModelType'] = model_type
    row_data['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Populate fields from input_data
    # Normalize keys from input_data (e.g., 'Lifecycle_Stage' to 'Lifecycle Stage')
    normalized_input_data = {key.replace('_', ' '): value for key, value in input_data.items()}

    for key, value in normalized_input_data.items():
        if key in row_data:
            row_data[key] = value
        # Handle specific keys that might have different names in input_data
        elif key == "Annual Salary Package" and "Annual_Salary_Package" in normalized_input_data: # from RuleBasedModelInputSchema
             row_data["Annual Salary Package"] = normalized_input_data["Annual_Salary_Package"]
        # Add more specific mappings if needed

    # Populate fields from output_data (portfolio allocation)
    if output_data:
        for key, value in output_data.items():
            # Ensure the key from output_data matches a header like "Equity (%)"
            header_key = f"{key} (%)" 
            if header_key in row_data:
                row_data[header_key] = value
            elif key in row_data: # For keys like 'Equity', 'Debt' if not with '(%)'
                 row_data[key] = value


    # Ensure the order of data matches CSV_HEADERS
    ordered_row_values = [row_data.get(header, '') for header in CSV_HEADERS]

    try:
        with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(ordered_row_values)
        logger.info(f"Data appended to CSV for user {user_email}, model {model_type}")
    except IOError as e:
        logger.error(f"Error appending data to CSV: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while writing to CSV: {e}")

# Example usage (for testing this module independently):
if __name__ == "__main__":
    initialize_csv()
    
    # Test data
    sample_input_base = {
        'Salary': 60000, 'Expenses': 40000, 'Savings': 20000,
        'Lifecycle_Stage': 'Early Career', 'Risk_Appetite': 'Medium', 'Investment_Horizon': 'Long-term'
    }
    sample_output = {'Equity': 50, 'Debt': 30, 'Gold': 10, 'FD/Cash': 10}
    append_data_to_csv(1, "test@example.com", "base", sample_input_base, sample_output)

    sample_input_enhanced = {
        'Profession': 'Engineer', 'City': 'Metropolis',
        'Salary': 120000, 'Expenses': 70000, 'Savings': 50000,
        'Lifecycle_Stage': 'Mid-Career', 'Risk_Appetite': 'High', 'Investment_Horizon': 'Long-term'
    }
    append_data_to_csv(2, "another@example.com", "enhanced", sample_input_enhanced, sample_output)

    sample_input_rule = {
        'Lifecycle_Stage': 'Late Career', 
        'Risk_Appetite': 'Low', 
        'Investment_Horizon': 'Short-term',
        'Annual_Salary_Package': 1000000, 
        'Monthly_In_hand_Salary': 60000, 
        'Total_Monthly_Expenses': 40000
    }
    append_data_to_csv(3, "ruleuser@example.com", "rule_based", sample_input_rule, sample_output)
    
    logger.info(f"Test data written to {CSV_FILE_PATH}")
