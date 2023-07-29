Firstly, you have to install Python on your system based on your operating system.
After that, you have to install the "pip install -r requirements.txt" file.
After that, you have to run the flask on your terminal. I'm sharing the Flask. Run the command below.

a. set flask_app=app.py
b. set flask_debug=1
c. flask run

1. def home(): It's showing the dashboard and showing the count of active calls, live call counts, queued call counts, and all recordings coming from the database history table.

2. def Calling(): It's only rendering the calling HTML templates.

3. def admin(): It shows the admin dashboard so that we can call another number, record the call, etc.

4. def Get_Call() = It's only calling to users.

5. def Capture_Active_Calls(): It shows the active call and how many calls are active right now and stores the active call in the history table.

6. def Capture_Dnd_Calls(): It's a function that only captures the DND calls.

7. def Capture_Busy_Calls(): It's showing all busy calls.

8 def Capture_Queued_Calls(): It's only showing the queued call to show how many active callers are waiting to be answered.

9. Capture_All_Recordings(): It's capturing all recordings and stores them into an S3 git bucket, checking if the file exists or not, and shows all API recordings into the capture Recording dashboard.

10. def start_recording(): It's only recorded when we're calling the user, and if the user is connected, then we'll record the call.

11. def Capture_Live_Call(): Here I'm capturing the live calls to see how many calls are connected right now. And I'm storing the live calls into the History Table.

12. def Stop_Recordings(): It only stops the recording. It's not completed. It's only flask functions.

Here I'm explaining another function that I using to own my Flask app._______________________________________

1. Get_Token.py: first it's getting the code from Google using Selenium, and after that, I'm storing the code into my refresh_token function. When I get the refresh token, I store the token in the access token.
2. Call_Api.py is a file for only core Python.
3. database.ini:      Here I'm keeping my database credentials and authorization email.
4. Insert_into_db.py:      It's putting the records into the database; it's only for the call_Api.py python file.
5. postredb.py: Here is my database function, which I'm using in the app.py file.
6. Existing_Check: Here I'm checking the s3 buckets file to see if it already exists in the bucket or not.
