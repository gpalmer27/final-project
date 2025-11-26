
# 1. Creating and running the project
- Download the zip file and open a terminal and cd into wherever you downloaded the folder (no specific directory needed)
- In a separate application, open MySQLWorkbench (https://dev.mysql.com/downloads/workbench/) and open the sql file provided
- Run all of the commands in the MySQLWorkbench so that you have all of the tables needed.
- Make sure you have pymysql and cryptography installed (pip install pymysql and pip install cryptography). To use
  pip, make sure you also have python3 installed (https://www.python.org/downloads/).
- In whatever terminal you're using, make sure you're in the final project folder then run python3 final_project.py
- The program should run correctly from there!

# 2. Technical specifications
We used MySQL Workbench to make all of the tables for our project. For the frontend, we used Python, specifically pymysql.
No other technologies or frameworks were used.

# 3. UML diagram

# 4. Logical design
![Design](ERD.png)

# 5. Final user flow
The user starts by providing their MySQL credentials and logging into the workbench. If they enter any incorrect information, they are prompted
to re-enter their information until they log in successfully. From there, they can either access the fighter portal or disconnect from the database.
If they choose to access the fighter portal, they are prompted to enter their email to log in. 
If their email is already registered in the database, they are given a list of actions that they can preform that are as follow:
1: Update user info (user can update their email, phone number, or weight)
2: Sign up for a membership (user can sign up for a membership that already exists in the database)
3: Transfer membership to a different gym (user can switch their membership to a different gym)
4: Cancel membership (user can cancel their existing membership)
5: Join a fight (user can join a fight simulation where they gain or lose money based on if they answer trivia questions correctly)
6: Check into training session (user can check into training session that keeps track of their attendance)
7: Purchase equipment (user can spend money to purchase equipment)
8: View user stats (user can view their wins and losses and win percentage)
9: Quit (user can quit the application)

If the user is not registered yet, they are prompted for their information so that they can register. If the gym they enter does not
exist in the database yet, they are also prompted to enter their gym information

# 6. Lessons learned
Through this project, we gained a lot more experience with using pymysql. Prior to this course, neither of us had used this framework before,
and through creating the frontend portion, we gained more experience with making calls to procedures and with accepting user input.
We also gained a lot of experience with creating procedures in general, as we had to spend a lot of time figuring out how everything should be connected
and debugging the procedures that weren't working.
One insight that we gained from this experience was how to best structure our code to make it the most efficient. We split our code into several
helper functions, and that made it much easier for us to debug what we were writing and made it easier to parse in general.
We briefly considered implementing a GUI for this project but decided that a text-based interface would be easier to implement for the sake of time.
However, if we'd had more time, we could have implemented a GUI that could have incorporated the same logic that we already have but made the 
application more engaging for the user.

# 7. Future work
With this database, we plan on using it when keeping track of MMA data in our own free time. We have learned a lot more about
MMA fighting through this project, and if we ever want to keep track of matches by ourself or simulate competing in matches against friends,
we can use this application.
Some functionality that we can add in the future includes allowing multiple users to log into the platform at the same time and compete against
each other, finding a way to better simulate matches other than just asking trivia, and coming up with more comprehensive ways to display 
data such as performance over time in a graph or through more detailed statistics.

