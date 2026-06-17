from datetime import datetime


# Format date
def format_date(date_string):
    try:
        date_obj = datetime.strptime(date_string, "%Y-%m-%d")
        return date_obj.strftime("%d %B %Y")
    except:
        return date_string


# Calculate total expenses
def calculate_total(expenses):
    return sum(exp["amount"] for exp in expenses)


# Calculate remaining budget
def calculate_remaining_budget(monthly_budget, total_expense):
    return monthly_budget - total_expense


# Budget percentage
def budget_usage_percentage(monthly_budget, total_expense):
    if monthly_budget == 0:
        return 0
    return round((total_expense / monthly_budget) * 100, 2)