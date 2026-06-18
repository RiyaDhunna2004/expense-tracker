from flask import Blueprint, render_template, request, redirect, session
from database.mongo import expenses_collection, budget_collection, recurring_collection, savings_collection, income_collection, borrow_collection, lent_collection
from bson.objectid import ObjectId
from datetime import datetime
from collections import defaultdict
from flask import jsonify
from utils.helpers import (calculate_total, calculate_remaining_budget, budget_usage_percentage)

expense_bp = Blueprint("expense", __name__)

# Dashboard
@expense_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    expenses = list(expenses_collection.find({"user_id": user_id}))
    
    income = list(income_collection.find({"user_id": user_id}))
    
    borrow_records = list(borrow_collection.find({
        "user_id": user_id,
        "status": "Pending"
    }))

    total_expense = calculate_total(expenses)
    
    total_income = calculate_total(income)
    
    pending_borrow = calculate_total(borrow_records)

    current_date = datetime.now()
    current_month = current_date.strftime("%Y-%m")

    if current_date.month == 1:
        previous_month = f"{current_date.year - 1}-12"
    else:
        previous_month = f"{current_date.year}-{str(current_date.month - 1).zfill(2)}"

    budget_data = budget_collection.find_one({
        "user_id": user_id,
        "month": current_month
    })
    
    previous_budget_data = budget_collection.find_one({
        "user_id": user_id,
        "month": previous_month
    })
    
    previous_expenses = list(expenses_collection.find({
        "user_id": user_id,
        "date": {
            "$regex": f"^{previous_month}"
        }
    }))

    previous_income = list(income_collection.find({
        "user_id": user_id,
        "date": {
            "$regex": f"^{previous_month}"
        }
    }))
    
    carry_forward = 0

    if previous_budget_data:
        previous_budget = previous_budget_data["monthly_budget"]

        previous_total_expense = calculate_total(previous_expenses)
        previous_total_income = calculate_total(previous_income)

        carry_forward = (
            previous_budget +
            previous_total_income -
            previous_total_expense
        )

        if carry_forward < 0:
            carry_forward = 0

    monthly_budget = (
        budget_data["monthly_budget"] + carry_forward
    ) if budget_data else carry_forward

    remaining_budget = calculate_remaining_budget(monthly_budget, total_expense)
    
    alert_message = None

    if monthly_budget > 0:
        usage_percentage = budget_usage_percentage(monthly_budget, total_expense)

        if usage_percentage >= 100:
            alert_message = "Warning: You have exceeded your monthly budget!"
        elif usage_percentage >= 80:
            alert_message = "Alert: You have used 80% of your monthly budget."
        else:
            alert_message = "Good: Your spending is under control."

    return render_template(
        "dashboard.html",
        expenses=expenses,
        total_expense=total_expense,
        total_income=total_income,
        monthly_budget=monthly_budget,
        carry_forward=carry_forward,
        remaining_budget=remaining_budget,
        alert_message=alert_message,
        pending_borrow=pending_borrow,
    )

# Set Monthly Budget
@expense_bp.route("/set-budget", methods=["POST"])
def set_budget():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    monthly_budget = float(request.form["monthly_budget"])

    current_date = datetime.now()
    current_month = current_date.strftime("%Y-%m")
    
    existing_budget = budget_collection.find_one({
        "user_id": user_id,
        "month": current_month
    })

    if existing_budget:
        budget_collection.update_one(
            {
                "user_id": user_id,
                "month": current_month
            },
            {
                "$set": {
                    "monthly_budget": monthly_budget
                }
            }
        )
    else:
        budget_collection.insert_one({
            "user_id": user_id,
            "month": current_month,
            "monthly_budget": monthly_budget
        })

    return redirect("/dashboard")

# Add Expense
@expense_bp.route("/add-expense", methods=["GET", "POST"])
def add_expense():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        amount = float(request.form["amount"])
        category = request.form["category"]
        description = request.form["description"]
        date = request.form["date"]

        expenses_collection.insert_one({
            "user_id": session["user_id"],
            "amount": amount,
            "category": category,
            "description": description,
            "date": date,
            "created_at": datetime.now()
        })

        return redirect("/dashboard")

    return render_template("add_expense.html")


# Delete Expense
@expense_bp.route("/delete-expense/<id>")
def delete_expense(id):
    expenses_collection.delete_one({"_id": ObjectId(id)})
    return redirect("/dashboard")

# Edit Expense
@expense_bp.route("/edit-expense/<id>", methods=["GET", "POST"])
def edit_expense(id):
    if "user_id" not in session:
        return redirect("/login")

    expense = expenses_collection.find_one({"_id": ObjectId(id)})

    if request.method == "POST":
        amount = float(request.form["amount"])
        category = request.form["category"]
        description = request.form["description"]
        date = request.form["date"]

        expenses_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "amount": amount,
                    "category": category,
                    "description": description,
                    "date": date
                }
            }
        )

        return redirect("/dashboard")
    
    return render_template("edit_expense.html", expense=expense)

# Category-wise Analytics
@expense_bp.route("/analytics/category")
def category_analytics():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    expenses = list(expenses_collection.find({"user_id": user_id}))

    category_data = defaultdict(float)

    for expense in expenses:
        category_data[expense["category"]] += expense["amount"]

    return jsonify(category_data)

# Monthly Trend Analytics
@expense_bp.route("/analytics/monthly")
def monthly_analytics():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    expenses = list(expenses_collection.find({"user_id": user_id}))

    monthly_data = defaultdict(float)

    for expense in expenses:
        month = expense["date"][:7]
        monthly_data[month] += expense["amount"]

    return jsonify(monthly_data)

# Search and Filter Expenses
@expense_bp.route("/filter-expenses", methods=["GET"])
def filter_expenses():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    category = request.args.get("category")
    date = request.args.get("date")
    min_amount = request.args.get("min_amount")
    max_amount = request.args.get("max_amount")

    query = {"user_id": user_id}

    if category:
        query["category"] = category

    if date:
        query["date"] = date

    if min_amount and max_amount:
        query["amount"] = {
            "$gte": float(min_amount),
            "$lte": float(max_amount)
        }

    filtered_expenses = list(expenses_collection.find(query))

    for expense in filtered_expenses:
        expense["_id"] = str(expense["_id"])

    return jsonify(filtered_expenses)

# Add Recurring Expense
@expense_bp.route("/add-recurring", methods=["POST"])
def add_recurring():
    if "user_id" not in session:
        return redirect("/login")

    recurring_collection.insert_one({
        "user_id": session["user_id"],
        "amount": float(request.form["amount"]),
        "category": request.form["category"],
        "description": request.form["description"],
        "frequency": request.form["frequency"]   # monthly/yearly
    })

    return redirect("/dashboard")

# View Recurring Expenses
@expense_bp.route("/recurring-expenses")
def recurring_expenses():
    if "user_id" not in session:
        return redirect("/login")

    data = list(recurring_collection.find({
        "user_id": session["user_id"]
    }))

    for item in data:
        item["_id"] = str(item["_id"])

    return render_template(
        "recurring_expenses.html",
        data=data
    )

# Delete Recurring Expense
@expense_bp.route("/delete-recurring/<id>")
def delete_recurring(id):
    recurring_collection.delete_one({
        "_id": ObjectId(id)
    })

    return redirect("/dashboard")

# Add Savings Goal
@expense_bp.route("/add-savings-goal", methods=["POST"])
def add_savings_goal():
    if "user_id" not in session:
        return redirect("/login")

    goal_name = request.form["goal_name"]
    target_amount = float(request.form["target_amount"])

    savings_collection.insert_one({
        "user_id": session["user_id"],
        "goal_name": goal_name,
        "target_amount": target_amount,
        "saved_amount": 0
    })

    return redirect("/savings-goals")

# Update Savings Progress
@expense_bp.route("/update-savings/<id>", methods=["POST"])
def update_savings(id):
    if "user_id" not in session:
        return redirect("/login")

    amount = float(request.form["amount"])

    savings_collection.update_one(
        {"_id": ObjectId(id)},
        {
            "$inc": {
                "saved_amount": amount
            }
        }
    )

    return redirect("/savings-goals")

# View Savings Goals
@expense_bp.route("/savings-goals")
def savings_goals():
    if "user_id" not in session:
        return redirect("/login")

    goals = list(savings_collection.find({
        "user_id": session["user_id"]
    }))

    for goal in goals:
        goal["_id"] = str(goal["_id"])
        goal["remaining_amount"] = max(0, goal["target_amount"] - goal["saved_amount"])

    return render_template(
        "savings_goals.html",
        goals=goals
    )
    
@expense_bp.route("/edit-goal/<id>", methods=["GET", "POST"])
def edit_goal(id):
    goal = savings_collection.find_one({"_id": ObjectId(id)})

    if request.method == "POST":
        savings_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "goal_name": request.form["goal_name"],
                    "target_amount": float(request.form["target_amount"])
                }
            }
        )
        return redirect("/savings-goals")

    return render_template("edit_goal.html", goal=goal)


@expense_bp.route("/delete-goal/<id>")
def delete_goal(id):
    savings_collection.delete_one(
        {"_id": ObjectId(id)}
    )
    return redirect("/savings-goals")
    
# Monthly History
@expense_bp.route("/monthly-history")
def monthly_history():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    budgets = list(budget_collection.find({
        "user_id": user_id
    }))

    history = []

    for budget in budgets:
        month = budget.get("month")
        if not month:
            continue

        month_expenses = list(expenses_collection.find({
            "user_id": user_id
        }))
 
        month_expenses = [
            exp for exp in month_expenses
            if exp.get("date", "").startswith(month)
        ]
 
        month_income = list(income_collection.find({
            "user_id": user_id
        }))

        month_income = [
            inc for inc in month_income
            if inc.get("date", "").startswith(month)
        ]

        month_borrow = list(borrow_collection.find({
            "user_id": user_id
        }))

        month_borrow = [
            bor for bor in month_borrow
            if bor.get("date", "").startswith(month)
        ]

        total_expense = calculate_total(month_expenses)
        total_income = calculate_total(month_income)
        total_borrow = calculate_total(month_borrow)

        carry_forward = budget.get("carry_forward") or 0

        final_balance = (carry_forward + total_income - total_expense - total_borrow)

        history.append({
            "month": month,
            "budget": budget["monthly_budget"],
            "income": total_income,
            "expenses": total_expense,
            "borrow": total_borrow,
            "final_balance": final_balance
        })

    return render_template(
        "monthly_history.html",
        history=history
    )

# AI Spending Insights
@expense_bp.route("/ai-insights")
def ai_insights():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    expenses = list(expenses_collection.find({"user_id": user_id}))

    if not expenses:
        return jsonify({"message": "No expenses found"})

    total_expense = calculate_total(expenses)
    average_expense = total_expense / len(expenses)

    category_data = defaultdict(float)

    for expense in expenses:
        category_data[expense["category"]] += expense["amount"]

    highest_category = max(category_data, key=category_data.get)

    suggestions = []

    if category_data[highest_category] > average_expense:
        suggestions.append(
            f"Your highest spending is on {highest_category}. Consider reducing it."
        )

    budget_data = budget_collection.find_one({"user_id": user_id, "month" : datetime.now().strftime("%Y-%m")})

    if budget_data:
        monthly_budget = budget_data["monthly_budget"]

        if total_expense > monthly_budget:
            suggestions.append(
                "You have exceeded your budget. Try reducing unnecessary expenses."
            )

    return jsonify({
        "total_expense": total_expense,
        "average_expense": average_expense,
        "highest_spending_category": highest_category,
        "suggestions": suggestions
    })
    
@expense_bp.route("/add-lent", methods=["GET", "POST"])
def add_lent():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        lent_collection.insert_one({
            "user_id": session["user_id"],
            "person_name": request.form["person_name"],
            "amount": float(request.form["amount"]),
            "description": request.form["description"],
            "date": request.form["date"],
            "status": "Pending"
        })

        return redirect("/dashboard")

    return render_template("add_lent.html")

# View Lent Records
@expense_bp.route("/lent-records")
def lent_records():
    if "user_id" not in session:
        return redirect("/login")

    records = list(lent_collection.find({
        "user_id": session["user_id"]
    }))

    return render_template(
        "lent_records.html",
        records=records
    )
    
@expense_bp.route("/mark-received/<id>")
def mark_received(id):
    if "user_id" not in session:
        return redirect("/login")

    lent_collection.update_one(
        {
            "_id": ObjectId(id),
            "user_id": session["user_id"]
        },
        {
            "$set": {
                "status": "Received"
            }
        }
    )

    return redirect("/lent-records")