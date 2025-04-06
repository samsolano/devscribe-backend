from flask import Flask, request, jsonify
import random
import datetime

app = Flask(__name__)

# In-memory data storage
users = [
    {"id": 1, "name": "Alice", "balance": 1000.0},
    {"id": 2, "name": "Bob", "balance": 750.0},
    {"id": 3, "name": "Charlie", "balance": 500.0}
]

products = [
    {"id": 1, "name": "Widget", "price": 19.99},
    {"id": 2, "name": "Gadget", "price": 29.99},
    {"id": 3, "name": "Doohickey", "price": 9.99}
]

transactions = []

# --- Logic and Helper Functions ---

def calculate_discounted_price(price, discount_rate):
    """
    Calculate the price after applying a discount.
    discount_rate should be provided as a percentage (0-100).
    """
    return price * (1 - discount_rate / 100)

def generate_transaction_id():
    """Generate a random transaction ID."""
    return random.randint(100000, 999999)

def record_transaction(user_id, product_id, quantity, total_price):
    """
    Create a new transaction record and append it to the transactions list.
    """
    transaction = {
        "transaction_id": generate_transaction_id(),
        "user_id": user_id,
        "product_id": product_id,
        "quantity": quantity,
        "total_price": total_price,
        "timestamp": datetime.datetime.now().isoformat()
    }
    transactions.append(transaction)
    return transaction

# --- Flask API Endpoints ---

@app.route("/users", methods=["GET"])
def get_users():
    """
    GET /users
    Returns a list of all users.
    """
    return jsonify({"users": users})

@app.route("/products", methods=["GET"])
def get_products():
    """
    GET /products
    Returns a list of all available products.
    """
    return jsonify({"products": products})

@app.route("/transactions", methods=["GET"])
def get_transactions():
    """
    GET /transactions
    Optionally filters transactions by user_id if provided as a query parameter.
    """
    user_id = request.args.get("user_id", type=int)
    if user_id:
        filtered_transactions = [t for t in transactions if t["user_id"] == user_id]
        return jsonify({"transactions": filtered_transactions})
    return jsonify({"transactions": transactions})

@app.route("/purchase", methods=["POST"])
def purchase_product():
    """
    POST /purchase
    Expects a JSON payload with the following keys:
      - user_id: int
      - product_id: int
      - quantity: int (default is 1)
      - discount_rate: float (optional, default is 0)
    
    Handles product purchase, applies discount if provided, deducts balance from the user,
    and records the transaction.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    user_id = data.get("user_id")
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)
    discount_rate = data.get("discount_rate", 0)

    # Locate the user
    user = next((u for u in users if u["id"] == user_id), None)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    # Locate the product
    product = next((p for p in products if p["id"] == product_id), None)
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    # Calculate the total price after discount
    discounted_price = calculate_discounted_price(product["price"], discount_rate)
    total_price = discounted_price * quantity

    # Verify sufficient balance
    if user["balance"] < total_price:
        return jsonify({"error": "Insufficient balance"}), 400

    # Deduct the balance and record the transaction
    user["balance"] -= total_price
    transaction = record_transaction(user_id, product_id, quantity, total_price)

    return jsonify({
        "message": "Purchase successful",
        "transaction": transaction,
        "new_balance": user["balance"]
    }), 200

@app.route("/recharge", methods=["POST"])
def recharge_account():
    """
    POST /recharge
    Expects a JSON payload:
      - user_id: int
      - amount: float
    Adds the specified amount to the user's balance.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    user_id = data.get("user_id")
    amount = data.get("amount", 0)

    # Locate the user
    user = next((u for u in users if u["id"] == user_id), None)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    user["balance"] += amount
    return jsonify({
        "message": "Recharge successful",
        "new_balance": user["balance"]
    }), 200

# --- Additional Business Logic Endpoint ---

@app.route("/summary", methods=["GET"])
def summary():
    """
    GET /summary
    Provides a summary report that includes:
      - Total number of users
      - Total number of transactions
      - Total revenue from transactions
    """
    total_users = len(users)
    total_transactions = len(transactions)
    total_revenue = sum(t["total_price"] for t in transactions)
    report = {
        "total_users": total_users,
        "total_transactions": total_transactions,
        "total_revenue": round(total_revenue, 2)
    }
    return jsonify(report)

if __name__ == "__main__":
    app.run(debug=True)