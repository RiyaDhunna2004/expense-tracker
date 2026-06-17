from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["expense_tracker"]

users_collection = db["users"]
expenses_collection = db["expenses"]
budget_collection = db["budgets"]
recurring_collection = db["recurring_expenses"]
savings_collection = db["savings_goals"]
income_collection = db["income"]
borrow_collection = db["borrow"]
lent_collection = db["lent"]