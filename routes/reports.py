from flask import Blueprint, session, redirect, send_file, render_template
from database.mongo import (expenses_collection, budget_collection, income_collection, borrow_collection, lent_collection)
from reportlab.pdfgen import canvas
import csv
import os

reports_bp = Blueprint("reports", __name__)


# Reports Data
@reports_bp.route("/reports")
def reports():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    expenses = list(expenses_collection.find({"user_id": user_id}))

    total_expense = sum(exp["amount"] for exp in expenses)

    budget_data = budget_collection.find_one({"user_id": user_id})
    monthly_budget = budget_data["monthly_budget"] if budget_data else 0

    remaining_budget = monthly_budget - total_expense

    return render_template(
        "reports.html",
        total_expense=total_expense,
        monthly_budget=monthly_budget,
        remaining_budget=remaining_budget,
        expenses=expenses
    )


# PDF Export
@reports_bp.route("/download-pdf")
def download_pdf():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    expenses = list(expenses_collection.find({"user_id": user_id}))
    income = list(income_collection.find({"user_id": user_id}))
    borrow = list(borrow_collection.find({"user_id": user_id}))
    lent = list(lent_collection.find({"user_id": user_id}))

    total_expense = sum(exp["amount"] for exp in expenses)
    total_income = sum(inc["amount"] for inc in income)
    total_borrow = sum(bor["amount"] for bor in borrow)
    total_lent = sum(ln["amount"] for ln in lent)

    net_balance = total_income - total_expense - total_borrow + total_lent

    file_path = "financial_report.pdf"

    pdf = canvas.Canvas(file_path)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(180, 800, "Financial Report")

    pdf.setFont("Helvetica", 12)

    pdf.drawString(50, 760, f"Total Income: ₹ {total_income}")
    pdf.drawString(50, 740, f"Total Expenses: ₹ {total_expense}")
    pdf.drawString(50, 720, f"Total Borrowed: ₹ {total_borrow}")
    pdf.drawString(50, 700, f"Total Lent: ₹ {total_lent}")
    pdf.drawString(50, 680, f"Net Balance: ₹ {net_balance}")

    pdf.drawString(50, 640, "Expense History:")

    y = 610

    for expense in expenses:
        line = (
            f"{expense['date']} | "
            f"{expense['category']} | "
            f"{expense.get('payment_mode', 'N/A')} | "
            f"₹{expense['amount']}"
        )

        pdf.drawString(50, y, line)
        y -= 20

        if y < 50:
            pdf.showPage()
            y = 800

    pdf.save()

    return send_file(file_path, as_attachment=True)

# CSV Export
@reports_bp.route("/download-csv")
def download_csv():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    expenses = list(expenses_collection.find({"user_id": user_id}))

    file_path = "expense_report.csv"

    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["Amount", "Category", "Description", "Date"])

        for expense in expenses:
            writer.writerow([
                expense["amount"],
                expense["category"],
                expense["description"],
                expense["date"]
            ])

    return send_file(file_path, as_attachment=True)