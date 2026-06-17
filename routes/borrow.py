from flask import Blueprint, render_template, request, redirect, session
from database.mongo import borrow_collection
from bson.objectid import ObjectId
from datetime import datetime

borrow_bp = Blueprint("borrow", __name__)


# Add Borrow Entry
@borrow_bp.route("/add-borrow", methods=["GET", "POST"])
def add_borrow():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        person_name = request.form["person_name"]
        amount = float(request.form["amount"])
        reason = request.form["reason"]

        borrow_collection.insert_one({
            "user_id": session["user_id"],
            "person_name": person_name,
            "amount": amount,
            "reason": reason,
            "status": "Pending",
            "date": datetime.now().strftime("%Y-%m-%d")
        })

        return redirect("/dashboard")

    return render_template("add_borrow.html")


# View Borrow Records
@borrow_bp.route("/borrow-records")
def borrow_records():
    if "user_id" not in session:
        return redirect("/login")

    records = list(borrow_collection.find({
        "user_id": session["user_id"]
    }))

    for record in records:
        record["_id"] = str(record["_id"])

    return render_template(
        "borrow_records.html",
        records=records
    )


# Mark as Paid
@borrow_bp.route("/mark-paid/<id>")
def mark_paid(id):
    if "user_id" not in session:
        return redirect("/login")

    borrow_collection.update_one(
        {
            "_id": ObjectId(id),
            "user_id": session["user_id"]
        },
        {
            "$set": {
                "status": "Paid"
            }
        }
    )

    return redirect("/borrow-records")