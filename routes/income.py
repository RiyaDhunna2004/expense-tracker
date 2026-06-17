from flask import Blueprint, render_template, request, redirect, session
from database.mongo import income_collection
from collections import defaultdict
from flask import jsonify
from datetime import datetime

income_bp = Blueprint("income", __name__)


# Add Income
@income_bp.route("/add-income", methods=["GET", "POST"])
def add_income():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        amount = float(request.form["amount"])
        source = request.form["source"]
        income_type = request.form["income_type"]
        date = request.form["date"]

        income_collection.insert_one({
            "user_id": session["user_id"],
            "amount": amount,
            "source": source,
            "income_type": income_type,
            "payment_mode": request.form["payment_mode"],
            "date": date,
            "created_at": datetime.now()
        })

        return redirect("/dashboard")

    return render_template("add_income.html")

# Monthly Income Analytics
@income_bp.route("/analytics/income")
def income_analytics():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    income = list(income_collection.find({
        "user_id": user_id
    }))

    monthly_income = defaultdict(float)

    for item in income:
        month = item["date"][:7]
        monthly_income[month] += item["amount"]

    return jsonify(monthly_income)