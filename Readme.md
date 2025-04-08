## Hi Devscribe if you want to start working on the backend start with these things so you can start working

- In main.py on line 93, update the path to your local frontend project you want to test with (ideally a second frontend local project that is not connected to a git repo)

- Add a file called ".env" to your root directory, in the file add this "GEMMA_KEY=" (without the quotes)

- Go to google gemini api and get an api key and put it in to the .env so it will look like "GEMMA_KEY=1234abcd"



python3 -m streamlit run main.py to run