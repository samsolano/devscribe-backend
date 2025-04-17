import io
import re
import streamlit as st

def extractDRFAPIFunctions(code):
    api_functions = []
    routes = []

    lines = io.StringIO(code)

    inside_function = False
    inside_decorator = False
    current_function = []

    for line in lines:
        stripped = line.strip()
        leading_spaces = len(line) - len(line.lstrip())

        # Start of decorator
        if re.match(r'@api_view\(\[.*\]\)', stripped):
            inside_function = True
            inside_decorator = True
            current_function = [line]
            continue

        # Function def after decorator
        if inside_function and re.match(r'def\s+\w+\s*\(', stripped):
            current_function.append(line)
            inside_decorator = False
            continue

        # Accumulate function body
        if inside_function and not inside_decorator:
            if stripped and leading_spaces > 0:
                current_function.append(line)
                continue
            else:
                # End of function
                api_functions.append("".join(current_function))
                func_name = re.search(r'def\s+(\w+)\s*\(', "".join(current_function))
                if func_name:
                    routes.append(func_name.group(1))
                inside_function = False
                current_function = []

    # Final function if file ends with one
    if inside_function and current_function:
        api_functions.append("".join(current_function))
        func_name = re.search(r'def\s+(\w+)\s*\(', "".join(current_function))
        if func_name:
            routes.append(func_name.group(1))

    return api_functions, routes
