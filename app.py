from flask import Flask, render_template, redirect, url_for, request, session
from routes.income import income_bp
from routes.borrow import borrow_bp
from datetime import timedelta
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.permanent_session_lifetime = timedelta(days=7)

@app.route("/")
def home():
    return redirect("/login")

# Import Blueprints
from routes.auth import auth_bp
from routes.expense import expense_bp
from routes.budget import budget_bp
from routes.reports import reports_bp

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(expense_bp)
app.register_blueprint(income_bp)
app.register_blueprint(borrow_bp)
app.register_blueprint(budget_bp)
app.register_blueprint(reports_bp)

if __name__ == "__main__":
    app.run(debug=True)