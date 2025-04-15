import io
import re

def extractFastAPIFunctions(code):
    api_functions = []
    routes = []

    lines = io.StringIO(code)

    inside_function = False
    indentation_level = None
    current_function = []

    for line in lines:
        stripped_line = line.rstrip("\n")

        # Detect FastAPI route decorators (e.g., @app.get("/path"))
        if re.match(r'\s*@app\.(get|post|put|delete|patch)\s*\(\s*["\']', stripped_line):
            route_match = re.search(r'@app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', stripped_line)
            if route_match:
                route = route_match.group(2)
                routes.append(route.lstrip('/'))

            if inside_function and current_function:
                api_functions.append("".join(current_function))
                current_function = []

            inside_function = True
            indentation_level = None
            current_function = [line]
            continue

        if inside_function:
            if indentation_level is None and re.match(r"\s*async\s+def\s+\w+\s*\(", line) or re.match(r"\s*def\s+\w+\s*\(", line):
                indentation_level = len(line) - len(line.lstrip())
                current_function.append(line)
                continue

            if indentation_level is not None:
                current_indent = len(line) - len(line.lstrip())
                if line.strip() != "" and current_indent < indentation_level:
                    inside_function = False
                    api_functions.append("".join(current_function))
                    continue
                else:
                    current_function.append(line)
            else:
                current_function.append(line)

    if inside_function and current_function:
        api_functions.append("".join(current_function))

    return api_functions, routes
