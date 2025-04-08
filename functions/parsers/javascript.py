# Here's where to add the new javascript parsers. Use the python flask parser as inspiration 
#
# To easily test the parser I would:
#   1. Make a repo with fake apis and feed it to the streamlit page,
#   2. Run the "Find All File Paths" chunk of code and update the file_types variable to which file types to include,
#   3. Run the "Get All Source Code chunk of code and put "st.write(all_apis)" at the bottom to verify the output, and leave all the following code commented out