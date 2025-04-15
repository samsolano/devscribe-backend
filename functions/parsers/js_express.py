# Here's where to add the new javascript parsers. Use the python flask parser as inspiration 
#
# To easily test the parser I would:
#   1. Make a repo with fake apis and feed it to the streamlit page,
#   2. Run the "Find All File Paths" chunk of code and update the file_types variable to which file types to include,
#   3. Run the "Get All Source Code chunk of code and put "st.write(all_apis)" at the bottom to verify the output, and leave all the following code commented out

import io
import re

# Function to extract API functions and routes from Express.js code
def extractExpressAPIFunctions(code):
    api_functions = []
    routes = []

    lines = io.StringIO(code)

    inside_function = False
    current_function = []
    bracket_count = 0

    for line in lines:
        stripped_line = line.strip()

        # Detect Express.js route handlers (allow for both app and router)
        match = re.match(r'(app|router)\.(get|post|put|delete|patch|options|head)\(["\'](.*?)["\']', stripped_line)

        if match:
            route = match.group(3).lstrip('/')
            routes.append(route)

            # If already inside a function, store the previous one
            if inside_function and current_function:
                api_functions.append("".join(current_function))
                current_function = []

            inside_function = True
            current_function = [line]

            # Count opening parentheses and braces for scope tracking
            bracket_count = line.count('{') - line.count('}')
            continue

        if inside_function:
            current_function.append(line)

            # Update bracket count to track function body
            bracket_count += line.count('{') - line.count('}')

            # If brackets are balanced, function definition likely ends
            if bracket_count <= 0:
                inside_function = False
                api_functions.append("".join(current_function))
                current_function = []

    # In case the file ends while still inside a function block
    if inside_function and current_function:
        api_functions.append("".join(current_function))

    return api_functions, routes
