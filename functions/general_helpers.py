import streamlit as st
from io import BytesIO
from git import Repo
import requests
import tempfile
import base64
import io
import os
import re

def update_local_with_api_doc(path, documentation, component_name):

  target_dir = os.path.join(path, "src", "app", "api-docs", component_name.lower())
  st.write(f"Target directory: {target_dir}")
  os.makedirs(target_dir, exist_ok=True)
  
  file_path = os.path.join(target_dir, "page.tsx")
  with open(file_path, "w", encoding="utf-8") as f:
      f.write(documentation)
  st.write(f"API documentation written to {file_path}")

  addSidebarLink(path, component_name, 1)
  st.write("Local files updated.")


# check if route already exists also
def addSkeletonRouting(repo_path, component_name):

  app_tsx_path = os.path.join(repo_path, "src", "App.tsx")
  import_line = f'import {component_name} from "./pages/api-docs/{component_name}";\n'
  new_route_line = f'     <Route path="/api-docs/{component_name.lower()}" element={{<{component_name} />}} />\n'

  with open(app_tsx_path, "r", encoding="utf-8") as file:
      content = file.read()

  if import_line in content:
      print(f"Import for {component_name} already exists in {app_tsx_path}")
      return

  index = content.rfind("</Routes>")
  new_content = import_line + content[:index] + new_route_line + content[index:]

  with open(app_tsx_path, "w", encoding="utf-8") as file:
      file.write(new_content)

  st.write(f"Added import and routing for {component_name} to {app_tsx_path}")


def addSidebarLink(repo_path, component_name, local):

    sidebar_path = os.path.join(repo_path, "src", "components", "layout", "Sidebar.tsx")
    route = component_name.lower()

    if local: 
      new_link = (
          f'            <li>\n'
          f'              <a href="/api-docs/{route}" className="block px-4 py-2 text-codium-foreground hover:bg-codium-border">\n'
          f'                /{component_name}\n'
          f'              </a>\n'
          f'            </li>\n\t\t'
      )

    # if not local: 
    #   new_link = (
    #       f'            <li>\n'
    #       f'              <Link to="/api-docs/{route}" className="block px-4 py-2 text-codium-foreground hover:bg-codium-border">\n'
    #       f'                /{component_name}\n'
    #       f'              </Link>\n'
    #       f'            </li>\n'
    #   )
    
    with open(sidebar_path, "r", encoding="utf-8") as file:
        content = file.read()


    index = content.rfind("</ul>")
    new_content = content[:index] + new_link + content[index:]
    
    # Write the updated content back to the file.
    with open(sidebar_path, "w", encoding="utf-8") as file:
        file.write(new_content)


def update_git_skeleton_with_api_doc(skeleton_git_url, api_doc_content, filename, component_name, commit_message):
    """
    Clone the skeleton git repository, create or update the file in src/pages/api-docs,
    commit the changes, and push them to the remote.
    
    Parameters:
      - skeleton_git_url: The Git URL for the skeleton project.
      - api_doc_content: The generated API documentation content (HTML/JSX string).
      - filename: The name for the file in src/pages/api-docs.
      - commit_message: The commit message to use.
    """
    # Clone the repository into a temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_path = os.path.join(tmp_dir, "skeleton")
        st.write(f"Cloning skeleton repository into {repo_path}...")
        repo = Repo.clone_from(skeleton_git_url, repo_path)
        
        # Define the target directory within the cloned repository
        target_dir = os.path.join(repo_path, "src", "pages", "api-docs")
        st.write(target_dir)
        os.makedirs(target_dir, exist_ok=True)
        
        # Define the file path and write the API documentation content to the file
        file_path = os.path.join(target_dir, filename)
        st.write(file_path)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(api_doc_content)
        st.write(f"API documentation written to {file_path}")

        # Add import and route to App.tsx
        addSkeletonRouting(repo_path, component_name)

        # Add link into sidebar
        addSidebarLink(repo_path, component_name)
        
        # Stage the file and commit the changes
        repo.git.add('.')
        repo.index.commit(commit_message)
        st.write("Committed changes.")
        
        # Push the changes to the remote repository
        try:
            origin = repo.remote(name="origin")
            origin.push()
            st.write("Changes pushed to remote.")
        except Exception as e:
            st.write(f"Failed to push changes: {e}")



def extract_github_file(owner, repo, file_path, token=None):
    """
    Fetches a specific file from a GitHub repository.
    
    Args:
        owner (str): The owner of the repository (e.g., 'octocat').
        repo (str): The name of the repository (e.g., 'Hello-World').
        file_path (str): The path to the file in the repo (e.g., 'src/main.py').
        token (str, optional): GitHub personal access token for authentication.

    Returns:
        BytesIO: File-like object containing the file's content.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        file_data = response.json()
        return file_data
        # file_content = base64.b64decode(file_data["content"])  # Decode base64 content
        # return BytesIO(file_content)  # Return file-like object

    else:
        raise Exception(f"Error fetching file: {response.status_code} {response.text}")


# Function for finding all file paths of a specific file type in a git repo
#   root_directory is a list
def findAllFilePaths(paths, current_path, root_directory, file_types, owner, repo, github_token):

  for file in root_directory:
    name = file['name']
    # st.write(file, "currPath: ", current_path, "actual string:", f"{current_path}/{name}") #################################
    if file['type'] == 'dir':
      subdirectory = extract_github_file(owner, repo, f"{current_path}/{name}", github_token)
      findAllFilePaths(paths, f"{current_path}/{name}", subdirectory, file_types, owner, repo, github_token)
    
    elif file['type'] == 'file':
      for file_type in file_types:
        if name.endswith(file_type):
          paths.append(f"{current_path}/{name}")
          break


# Function for getting all python flask api code into a single list
def extractAPIFunctions(code):
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

