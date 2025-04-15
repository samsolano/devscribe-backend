from functions.general_helpers import findAllFilePaths, update_local_with_api_doc, extract_github_file, update_git_skeleton_with_api_doc
from parsers.python_flask import extractFlaskAPIFunctions
from parsers.js_express import extractExpressAPIFunctions
from parsers.python_fast import extractFastAPIFunctions
from functions.llm_functions import gemma_send
from collections import defaultdict
from dotenv import load_dotenv
from io import BytesIO
import streamlit as st
import base64
import json
import os

# Caching returned data
# paths = ["./example_APIs/flask_api.py","./functions/flask_parser.py","./functions/git_helpers.py","./functions/langchain_helpers.py","./main.py"]
# all_apis = {"flask_api.py":["@app.route(\"/users\", methods=[\"GET\"])\ndef get_users():\n    \"\"\"\n    GET /users\n    Returns a list of all users.\n    \"\"\"\n    return jsonify({\"users\": users})\n\n","@app.route(\"/products\", methods=[\"GET\"])\ndef get_products():\n    \"\"\"\n    GET /products\n    Returns a list of all available products.\n    \"\"\"\n    return jsonify({\"products\": products})\n\n","@app.route(\"/transactions\", methods=[\"GET\"])\ndef get_transactions():\n    \"\"\"\n    GET /transactions\n    Optionally filters transactions by user_id if provided as a query parameter.\n    \"\"\"\n    user_id = request.args.get(\"user_id\", type=int)\n    if user_id:\n        filtered_transactions = [t for t in transactions if t[\"user_id\"] == user_id]\n        return jsonify({\"transactions\": filtered_transactions})\n    return jsonify({\"transactions\": transactions})\n\n","@app.route(\"/purchase\", methods=[\"POST\"])\ndef purchase_product():\n    \"\"\"\n    POST /purchase\n    Expects a JSON payload with the following keys:\n      - user_id: int\n      - product_id: int\n      - quantity: int (default is 1)\n      - discount_rate: float (optional, default is 0)\n    \n    Handles product purchase, applies discount if provided, deducts balance from the user,\n    and records the transaction.\n    \"\"\"\n    data = request.get_json()\n    if not data:\n        return jsonify({\"error\": \"Invalid JSON payload\"}), 400\n\n    user_id = data.get(\"user_id\")\n    product_id = data.get(\"product_id\")\n    quantity = data.get(\"quantity\", 1)\n    discount_rate = data.get(\"discount_rate\", 0)\n\n    # Locate the user\n    user = next((u for u in users if u[\"id\"] == user_id), None)\n    if user is None:\n        return jsonify({\"error\": \"User not found\"}), 404\n\n    # Locate the product\n    product = next((p for p in products if p[\"id\"] == product_id), None)\n    if product is None:\n        return jsonify({\"error\": \"Product not found\"}), 404\n\n    # Calculate the total price after discount\n    discounted_price = calculate_discounted_price(product[\"price\"], discount_rate)\n    total_price = discounted_price * quantity\n\n    # Verify sufficient balance\n    if user[\"balance\"] < total_price:\n        return jsonify({\"error\": \"Insufficient balance\"}), 400\n\n    # Deduct the balance and record the transaction\n    user[\"balance\"] -= total_price\n    transaction = record_transaction(user_id, product_id, quantity, total_price)\n\n    return jsonify({\n        \"message\": \"Purchase successful\",\n        \"transaction\": transaction,\n        \"new_balance\": user[\"balance\"]\n    }), 200\n\n","@app.route(\"/recharge\", methods=[\"POST\"])\ndef recharge_account():\n    \"\"\"\n    POST /recharge\n    Expects a JSON payload:\n      - user_id: int\n      - amount: float\n    Adds the specified amount to the user's balance.\n    \"\"\"\n    data = request.get_json()\n    if not data:\n        return jsonify({\"error\": \"Invalid JSON payload\"}), 400\n\n    user_id = data.get(\"user_id\")\n    amount = data.get(\"amount\", 0)\n\n    # Locate the user\n    user = next((u for u in users if u[\"id\"] == user_id), None)\n    if user is None:\n        return jsonify({\"error\": \"User not found\"}), 404\n\n    user[\"balance\"] += amount\n    return jsonify({\n        \"message\": \"Recharge successful\",\n        \"new_balance\": user[\"balance\"]\n    }), 200\n\n# --- Additional Business Logic Endpoint ---\n\n","@app.route(\"/summary\", methods=[\"GET\"])\ndef summary():\n    \"\"\"\n    GET /summary\n    Provides a summary report that includes:\n      - Total number of users\n      - Total number of transactions\n      - Total revenue from transactions\n    \"\"\"\n    total_users = len(users)\n    total_transactions = len(transactions)\n    total_revenue = sum(t[\"total_price\"] for t in transactions)\n    report = {\n        \"total_users\": total_users,\n        \"total_transactions\": total_transactions,\n        \"total_revenue\": round(total_revenue, 2)\n    }\n    return jsonify(report)\n\nif __name__ == \"__main__\":\n    app.run(debug=True)\n"],"flask_parser.py":[],"git_helpers.py":[],"langchain_helpers.py":[],"main.py":[]}
# route_names = {"flask_api.py":["users","products","transactions","purchase","recharge","summary"],"flask_parser.py":[],"git_helpers.py":[],"langchain_helpers.py":[],"main.py":[]}
# api_documentation = 

st.set_page_config(layout="wide")
st.image("design_resources/logo-white.svg", width=200)
load_dotenv()
github_token = os.getenv("GITHUB_TOKEN")

owner = st.text_input("Repository owner", value="tkim516")
repo = st.text_input("Repository name", value="devscribe-example-apis")
file_path = st.text_input("File path", value=".")
submit = st.button("Generate")

if submit:

#---------------------------------------------------------------Find All File Paths----------------------------------------------------------------------------------------------
  
  # Stores the paths of all files in repo of correct file type (as defined in "file_types") into "paths" variable 
  st.write("1")
  root_directory = extract_github_file(owner, repo, file_path, github_token)
  st.write("2")
  paths = []
  file_types = [".js", ".py"]
  current_path = "."
  findAllFilePaths(paths, current_path, root_directory, file_types, owner, repo, github_token)
  st.write(paths)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------Get All API Source Code-----------------------------------------------------------------------------------------

  # Get all source code from all file paths in "paths" and store into "all_source_code"
  all_source_code = {}

  for path in paths:
    file_data = extract_github_file(owner, repo, path, github_token)
    file_content = base64.b64decode(file_data["content"])  # Decode base64 content
    file_content = BytesIO(file_content).read().decode()
    # all_source_code += f"file {file_counter}, {file_data['name']}:\n{file_content}\n\n"
    all_source_code[file_data['name']] = file_content



  # Get just the API code
  all_apis = {}
  route_names = {}    # dictionary with keys being the file names and the value is a list of the api routes (  {"file.py": ["route1", "route2"]}  )

  for file in all_source_code:
    
    if file.endswith(".py") and "flask" in file:
      all_apis[file], route_names[file] = extractFlaskAPIFunctions(all_source_code[file])

    elif file.endswith(".py") and "fast" in file:
      all_apis[file], route_names[file] = extractFastAPIFunctions(all_source_code[file])

    elif file.endswith(".js"):
      all_apis[file], route_names[file] = extractExpressAPIFunctions(all_source_code[file])


  st.write(all_apis)  # will print out just the code for all the apis if extractingAPIFunctions() is succesful
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#-----------------------------------------------------Create Docs For All APIs---------------------------------------------------------------------------------------------------------------------

  # # Send all created API code with names one at a time to llm and have it create formatted html page for API doc
  # api_documentation = {}

  # for file in all_apis:
  #   if len(all_apis[file]) == 0:
  #       continue
  #   for i in range(len(all_apis[file])):
  #     api = all_apis[file][i]
  #     route = route_names[file][i]

  #     response = gemma_send(api, route.capitalize())
  #     response = response["candidates"][0]["content"]["parts"][0]["text"]
  #     api_documentation[route] = response
  # st.write(api_documentation)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------Update Frontend---------------------------------------------------------------------------------------------------------------------
  # for route in api_documentation:
    
  #   filename = f"{route.capitalize()}.tsx"

  #   # FOR GIT REPO UPDATE
  #   # commit_message = f"added {route.capitalize()} doc"
  #   # skeleton_git_url = "https://github.com/samsolano/v1_doc_skeleton_4-5"
  #   # update_git_skeleton_with_api_doc(skeleton_git_url, api_documentation[route], filename, route.capitalize(), commit_message)


  #   # FOR LOCAL TESTING UPDATE
  #   path = "/Users/samsolano/Documents/WorkFolder/dev-scribe/devscribe-testing"
  #   update_local_with_api_doc(path, api_documentation[route], route.capitalize())

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------



