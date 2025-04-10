# created by Kirk Ogunrinde on April 6th, 2025

# import Flask (the main code framework)
from flask import Flask

# request is used to get data from the user's request (e.g., when they submit a new expense).
from flask import request

# jsonify is used to transform python data (like lists or dictionaries) into JSON (a format the frontend or user understands).
from flask import jsonify

# cors is used to accept requests from the frontend
from flask_cors import CORS

# initialises the app
app = Flask(__name__)

# allow all frontend origins
CORS(app)

# initialises list where we’ll store expense items 
# REPLACE
expenses = []

# initialises budget value
# REPLACE
budget = 0

# initialises goals list
# REPLACE
goals = []

# kep track of ids to assign to expenses
next_id = 1

##############################################################################################################

# function inserts new expense from the user
def insert_expense_to_db(data):
    
    # replace this with SQL INSERT logic
    pass

    # allows access to the global variables "expenses" and "next_id" 
    global expenses, next_id
    
    # assigns a new id to the new expense
    data['id'] = next_id
    
    # increment next_id so the next expense would be saved with the right index
    next_id += 1
    
    # add to the in-memory list
    expenses.append(data)
    
    # return the newly added expense so it can be sent in the API response
    return data


# function returns full list of expenses
def get_all_expenses():
    
    # replace this with SQL SELECT * logic
    pass

    # REPLACE     
    return expenses


# function returns expenses filtered by category (like “Food” or “Transport”)
def get_expenses_by_category(category):
    
    # replace this with SQL SELECT WHERE category= logic
    pass

    # REPLACE
    return [e for e in expenses if e.get('category') == category]


# updates an existing expense, matched by its unique id
def update_expense_in_db(id, data):
    
    # replace this with SQL UPDATE logic
    pass

    # loop through expenses to find the matching id
    for i, expense in enumerate(expenses):
        if expense['id'] == id:
            
            # update dict with the new data
            expenses[i].update(data)
            
            # ensure id remains the same
            expenses[i]['id'] = id
            
            # return the new updated expense
            return expenses[i]
        
    # if id is not found, return none
    return None


# deletes an expense based on its id
def delete_expense_from_db(id):
    
    # replace this with SQL DELETE logic
    pass

    # loop through expenses to find the matching id
    for i, expense in enumerate(expenses):
        if expense['id'] == id:
            
            # remove expense from the list using pop(i)
            return expenses.pop(i)
        
    # if id is not found, return none
    return None

##############################################################################################################

# listens for the "/goals" endpoint
@app.route('/goals', methods=['GET'])

# GET -- retrieve goals
def get_goals():
    return jsonify(goals)

##############################################################################################################

# listens for the "/goals" endpoint
@app.route('/goals', methods=['POST'])

# ADD -- adds a goal
def add_goal():
    
    # get the goal value from the frontend
    data = request.get_json()
    
    # require a title of the goal, and the targeted amount
    required = ['title', 'target']
    
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400
    
    data['current'] = data.get('current', 0)
    
    # add to goals list
    goals.append(data)
    
    # return success message
    return jsonify({"message": "Goal added", "goal": data}), 201


##############################################################################################################

# listens for the "/goals" endpoint
@app.route('/goals/<int:index>', methods=['PUT'])

# UPDATE -- update goal 
def update_goal(index):
    
    # get the goal value from the frontend
    data = request.get_json()
    
    # make sure it is a valid goal
    if 0 <= index < len(goals):
        
        goals[index].update(data)    
        return jsonify({"message": "Goal updated", "goal": goals[index]})
    
    # return success message
    return jsonify({"error": "Goal not found"}), 404


##############################################################################################################

# listens for the "/budget" endpoint
@app.route('/budget', methods=['POST'])

# SETTER -- set the amount of the budget
def set_budget():
    
    # allows access to global variable budget
    global budget
    
    # get the budget value from the frontend
    data = request.get_json()

    # if the budget value is not inputted, return error message
    if 'amount' not in data:
        return jsonify({"error": "Missing budget amount"}), 400

    # if the budget value, exists, assign the value returned to "budget" 
    budget = data['amount']
    
    # return success message
    return jsonify({"message": "Budget set", "budget": budget}), 201

##############################################################################################################

# listens for the "/expenses" endpoint
@app.route('/expenses', methods=['GET'])

# GETTER -- get data from the expenses list 
def get_expenses():
    
    # initialise category variable to be able to filter by category
    category = request.args.get('category')
    
    # initialise importance variable to be able to filter by importance
    importance = request.args.get('importance')
    
    # results gotten from filtering would be stored here
    results = get_all_expenses()

    # if category is specified, then get all expenses in that category based on category variable
    if category:
        results = [e for e in results if e.get('category') == category]
    
    # if importance is specified, then get all expenses in that importance based on importance variable
    if importance:
        results = [e for e in results if e.get('importance') == importance]
    
    # returns list of expenses in JSON format
    return jsonify(results)

##############################################################################################################

# listens for the "/expenses" endpoint
@app.route('/expenses', methods=['POST'])

# POST -- add expense to expense list in the form {"item": "Coffee", "amount": 5, "category": "Food and Drink"}
def add_expense():
    
    # allows possible editing of global variable next_id
    global next_id
    
    # get the data (which would be received in json format)
    data = request.get_json()
    
    # make sure the expenses format is being matched correctly
    if not all(k in data for k in ("item", "amount", "category", "importance")):
        return jsonify({"error": "Missing required fields"}), 400
    
    # prevent users from spending over budget
    if budget is not None:
        
        # sum up all the expenses
        total_spent = sum(e['amount'] for e in expenses)
        
        # if the new expense is going to go over budget, then return error message
        if total_spent + data['amount'] > budget:
            return jsonify({"error": "Expense exceeds budget"}), 400

    # create new expense
    new_expense = insert_expense_to_db(data)
    
    # returns a success message
    return jsonify({"message": "Expense added", "expense": new_expense}), 201

##############################################################################################################

# listens for the "/expenses/ID" endpoint
@app.route('/expenses/<int:id>', methods=['PUT'])

# PUT -- used to edit expenses in the expenses list
def update_expense(id):
    
    # REPLACE
    # checks if the index exists using len(expenses)
    # if 0 <= id < len(expenses):
        
        # get the data (which would be received in json format)
        data = request.get_json()
        
        # update expense based on id
        updated = update_expense_in_db(id, data)
        
        # if successful, return success message
        if updated:
            return jsonify({"message": "Expense updated", "expense": updated})
        
        # if not, return error message
        return jsonify({"error": "Not found"}), 404

##############################################################################################################

# listens for the "/expenses/ID" endpoint
@app.route('/expenses/<int:id>', methods=['DELETE'])

# DELETE -- used to delete data from the expenses list
def delete_expense(id):
    
    # delete expense from database 
    deleted = delete_expense_from_db(id)
    
    # if successful, return success message
    if deleted:
        return jsonify({"message": "Deleted", "expense": deleted})
    
    # if not, return error message
    return jsonify({"error": "Not found"}), 404

##############################################################################################################

# listens for the "/summary" endpoint
@app.route('/summary', methods=['GET'])

# GET -- gets a summary of the entire budget including all expenses
def get_summary():
    
    # sum up all the expenses
    total_spent = sum(e['amount'] for e in expenses)
    
    # subtract all expenses from the budget
    remaining = (budget or 0) - total_spent

    # breakdown by category and/or importance
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


##############################################################################################################

# listens for the "/reset" endpoint
@app.route('/reset', methods=['POST'])

# RESET -- reset the list of expenses
def reset_all():
    
    # allows access to global variables
    global expenses, budget, next_id
    
    # reset expenses
    expenses = []
    
    # reset budget
    budget = 0
    
    # reset next_id
    next_id = 1
    
    return jsonify({"message": "Reset successful"})


##############################################################################################################

# run file
if __name__ == '__main__':
    
    # helps during development — if code crashes, shows a nice error page
    app.run(debug=True)
