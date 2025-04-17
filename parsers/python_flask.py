import streamlit as st
from io import BytesIO
from git import Repo
import requests
import tempfile
import base64
import io
import os
import re


# Function for getting all python flask api code into a single list
def extractFlaskAPIFunctions(code):
  api_functions = []
  routes = []

  lines = io.StringIO(code)

  inside_function = False
  indentation_level = None
  current_function = []

  for line in lines:
      # Remove trailing newline for cleaner processing
      stripped_line = line.rstrip("\n")
      
      # Detect API route decorator (allow for leading whitespace)
      if stripped_line.lstrip().startswith("@app.route("):
          route = stripped_line.lstrip().split('("')[1].split('"')[0]
          # Remove the leading slash if it exists
          routes.append(route.lstrip('/'))
          # If already inside a function, store the previous one
          if inside_function and current_function:
              api_functions.append("".join(current_function))
              current_function = []
          inside_function = True
          indentation_level = None  # Reset the indentation tracking
          current_function = [line]  # Start a new function block with the decorator
          continue

      if inside_function:
          # Check if we're now at the function definition
          if indentation_level is None and re.match(r"\s*def\s+\w+\s*\(", line):
              # Set the base indentation level for the function definition line.
              indentation_level = len(line) - len(line.lstrip())
              current_function.append(line)
              continue

          # Once the function definition has been identified,
          # any nonblank line with less indentation signals the end of the function.
          if indentation_level is not None:
              current_indent = len(line) - len(line.lstrip())
              if line.strip() != "" and current_indent < indentation_level:
                  # Function block ended; do not include this line in the function.
                  inside_function = False
                  api_functions.append("".join(current_function))
                  # This line likely belongs to code outside the function.
                  continue
              else:
                  current_function.append(line)
          else:
              # Before reaching the function definition, just store the line.
              current_function.append(line)

  # In case the file ends while still inside a function block
  if inside_function and current_function:
      api_functions.append("".join(current_function))

  return api_functions, routes
