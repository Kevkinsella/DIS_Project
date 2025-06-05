# DIS_Project

- Download the requirements: pip install -r requirements.txt

- Run postgres server. Put information about servername/database in app.py

- "Database.sql" file in the folder, you should change the file paths inside to wherever your csv files (Countries.csv, Employers.csv, People.csv) are located on your pc.

- Then Load "Database.sql" in pgadmin4

- In terminal go to the directory where app.py is located and run: python app.py

The server is now up running
Now access the server on the url: http://127.0.0.1:5000/

You can freely register people, search employers, check pensions, and save highscores on our webapp.


(Just so you know, when you register a new dane abroad try to restart app.py, then you'll be able to see it under Employer)
