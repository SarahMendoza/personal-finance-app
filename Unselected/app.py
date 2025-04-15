# created by Kirk Ogunrinde on April 6th, 2025

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "113-894-795"
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # or 'None' if HTTPS
app.config['SESSION_COOKIE_SECURE'] = False    # Only True if using HTTPS

users = {}
user_data = {}




# used to connect to database
import mysql.connector
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:databases2024@localhost/arch-app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import db, User, Settings, Budget, Goal, Category, Expense
# db = SQLAlchemy(app)
db.init_app(app)  # 🔥 registers the app context with db

with app.app_context():
    #db.drop_all()
    db.create_all()  

# initialises list where we’ll store expense items 
# REPLACE
expenses = []


@app.route('/whoami')
def whoami():
    return jsonify({"user": session.get("username", "Not logged in")})


# @app.route('/signup', methods=['POST'])
# def signup():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')

#     if not username or not password:
#         return jsonify({"error": "Username and password required"}), 400

#     if username in users:
#         return jsonify({"error": "Username already exists"}), 400

#     users[username] = generate_password_hash(password)
#     user_data[username] = {
#         "budget": 0,
#         "expenses": [],
#         "next_id": 1,
#         "savings_goal": {
#             "goalAmount": 0,
#             "savedAmount": 0
#         }
#     }
#     return jsonify({"message": "Signup successful"}), 201

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')

#     if not username or not password:
#         return jsonify({"error": "Username and password required"}), 400

#     if username in users and check_password_hash(users[username], password):
#         session['username'] = username
#         return jsonify({"message": "Login successful"}), 200
#     return jsonify({"error": "Invalid credentials"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({"message": "Logged out successfully"})

@app.route('/savings-goal', methods=['GET'])
def get_savings_goal():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 403
    return jsonify(user_data[username].get("savings_goal", {}))

@app.route('/savings-goal', methods=['POST'])
def set_savings_goal():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 403

    data = request.get_json()
    user_data[username]["savings_goal"] = {
        "goalAmount": data.get("goalAmount", 0),
        "savedAmount": data.get("savedAmount", 0)
    }
    return jsonify({"message": "Savings goal set", "goal": user_data[username]["savings_goal"]}), 201

@app.route('/savings-goal', methods=['PUT'])
def update_savings_goal():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 403

    data = request.get_json()
    user_data[username]["savings_goal"]["savedAmount"] = data.get("savedAmount", 0)
    return jsonify({"message": "Savings goal updated", "goal": user_data[username]["savings_goal"]})




@app.route('/budget', methods=['POST'])
def set_budget():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 403

    data = request.get_json()
    if 'amount' not in data:
        return jsonify({"error": "Missing budget amount"}), 400
    
    # check if budget already exists for user
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    existing_budget = Budget.query.filter_by(user_id=user.user_id).first()
    if existing_budget:
        #update existing budget
        existing_budget.monthly_income = data['amount']
        db.session.commit()
        return jsonify({"message": "Budget updated", "budget": data['amount']}), 200
    else:
        # create new budget
        new_budget = Budget(user_id=user.user_id, monthly_income=data['amount'])
        db.session.add(new_budget)
        db.session.commit()
        return jsonify({"message": "Budget created", "budget": data['amount']}), 201

@app.route('/budget', methods=['GET'])
def get_budget():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 403

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    budget = Budget.query.filter_by(user_id=user.user_id).first()
    if not budget:
        return jsonify({"error": "Budget not found"}), 404

    return jsonify({"budget": budget.monthly_income}), 200




# # get list of all expenses for current user
# @app.route('/expenses', methods=['GET'])
# def get_expenses():
#     username = session.get('username')
#     if not username:
#         return jsonify({"error": "Not logged in"}), 403

#     category = request.args.get('category')
#     importance = request.args.get('importance')
#     results = user_data[username].get('expenses', [])
    

#     if category:
#         results = [e for e in results if e.get('category') == category]
#     if importance:
#         results = [e for e in results if e.get('importance') == importance]
#     return jsonify(results)

@app.route('/expenses', methods=['GET'])
def get_all_expenses():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 403

    category = request.args.get('category')
    importance = request.args.get('importance')

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    budget = Budget.query.filter_by(user_id=user.user_id).first()
    if not budget:
        return jsonify({"error": "No budget found"}), 400

    query = Expense.query.filter_by(budget_id=budget.budget_id)
    
    if category:
        query = query.filter_by(category_name=category)
    if importance:
        query = query.filter_by(importance=importance)

    expenses = query.all()

    result = [
        {
            "id": e.expense_id,
            "item": e.expense_label,
            "amount": float(e.expense_amount),
            "category": e.category_name,
            "importance": e.importance
        } for e in expenses
    ]
    return jsonify(result)

# # get list of all expenses for current user in a given category
# @app.route('/expenses-category', methods=['GET'])
# def get_expenses_category():
#     username = session.get('username')
#     if not username:
#         return jsonify({"error": "Not logged in"}), 403

#     category = request.args.get('category')
#     importance = request.args.get('importance')
#     results = user_data[username].get('expenses', [])
    

#     if category:
#         results = [e for e in results if e.get('category') == category]
#     if importance:
#         results = [e for e in results if e.get('importance') == importance]
#     return jsonify(results)

# # get list of all expenses for current user based on importance
# @app.route('/expenses-importance', methods=['GET'])
# def get_expenses_importance():
#     username = session.get('username')
#     if not username:
#         return jsonify({"error": "Not logged in"}), 403

#     category = request.args.get('category')
#     importance = request.args.get('importance')
#     results = user_data[username].get('expenses', [])
    

#     if category:
#         results = [e for e in results if e.get('category') == category]
#     if importance:
#         results = [e for e in results if e.get('importance') == importance]
#     return jsonify(results)


# insert an expense for currently logged in user
@app.route('/expenses', methods=['POST'])
def add_expense():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 403

    data = request.get_json()
    required_fields = ("item", "amount", "category", "importance")
    for k in required_fields:
        it = data[k]
        if not it:
            return jsonify({"error": f"Missing fields"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    budget = Budget.query.filter_by(user_id=user.user_id).first()
    if not budget:
        return jsonify({"error": "No budget found"}), 400

    # Check total expenses
    # total_spent = sum([e.expense_amount for e in budget.expenses])
    # if total_spent + data['amount'] > budget.monthly_income:
    #     return jsonify({"error": "Expense exceeds budget"}), 400

    # reate category if needed
    category = Category.query.filter_by(budget_id=budget.budget_id, category_name=data['category']).first()
    if not category:
        category = Category(
            budget_id=budget.budget_id,
            category_name=data['category'],
            #category_amount=data['amount']
        )
        db.session.add(category)

    # add expense
    expense = Expense(
        budget_id=budget.budget_id,
        category_name=category.category_name,
        importance=data['importance'],
        expense_label=data['item'],
        expense_amount=data['amount']
    )
    db.session.add(expense)
    db.session.commit()

    return jsonify({"message": "Expense added", "expense_id": expense.expense_id}), 201





@app.route('/expenses/<int:id>', methods=['PUT'])
def update_expense(id):
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 403

    data = request.get_json()
    for i, expense in enumerate(user_data[username].get('expenses', [])):
        if expense['id'] == id:
            user_data[username]['expenses'][i].update(data)
            return jsonify({"message": "Expense updated", "expense": user_data[username]['expenses'][i]})
    return jsonify({"error": "Not found"}), 404

@app.route('/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 403

    for i, expense in enumerate(user_data[username].get('expenses', [])):
        if expense['id'] == id:
            deleted = user_data[username]['expenses'].pop(i)
            return jsonify({"message": "Deleted", "expense": deleted})
    return jsonify({"error": "Not found"}), 404





@app.route('/summary', methods=['GET'])
def get_summary():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 403

    expenses = user_data[username].get('expenses', [])
    budget = user_data[username].get('budget', 0)
    total_spent = sum(e['amount'] for e in expenses)
    remaining = budget - total_spent

    breakdown = {}
    for e in expenses:
        key = f"{e['category']} - {e['importance']}"
        breakdown[key] = breakdown.get(key, 0) + e['amount']

    return jsonify({
        "budget": budget,
        "total_spent": total_spent,
        "remaining": remaining,
        "breakdown": breakdown
    })

@app.route('/reset', methods=['POST'])
def reset_all():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 403

    user_data[username] = {
        "budget": 0,
        "expenses": [],
        "next_id": 1,
        "savings_goal": {
            "goalAmount": 0,
            "savedAmount": 0
        }
    }
    return jsonify({"message": "Reset successful"})
  

##############################################################################################################

# User login, creation, deletion routes

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        session['username'] = username
        return jsonify({"message": "Login successful", "user_id": user.user_id})
    else:
        return jsonify({"message": "Invalid credentials"}), 401
    

@app.route('/create-user', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    #email = data.get('email')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if username or email already exists
    existing_user = User.query.filter((User.username == username)).first()

    if existing_user:
        return jsonify({'error': 'Username or email already exists'}), 409

    hashed_password = generate_password_hash(password)

    new_user = User(username=username, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': f'User {username} created successfully'}), 201


##############################################################################################################






# run file
if __name__ == '__main__':
    app.run(debug=True)
