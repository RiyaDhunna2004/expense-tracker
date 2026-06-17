from flask import Blueprint, request, redirect, session
from database.mongo import budget_collection

budget_bp = Blueprint("budget", __name__)

@budget_bp.route("/set-budget", methods=["POST"])
def set_budget():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    monthly_budget = float(request.form["monthly_budget"])

    existing_budget = budget_collection.find_one({"user_id": user_id})

    if existing_budget:
        budget_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "monthly_budget": monthly_budget
                }
            }
        )
    else:
        budget_collection.insert_one({
            "user_id": user_id,
            "monthly_budget": monthly_budget
        })

    return redirect("/dashboard")