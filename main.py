from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3, os
import re
import random

app =Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection of the application)
app.secret_key = os.urandom(24)

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/home/leave-Approved")
def leaveApproved():
    return ("<h1>Leave Approved Fragment!</h1>")

@app.route("/home/leave-Pending")
def leavePending():
    return ("<div><h1>Leave Pending Fragment!</h1></div")

@app.route("/home/leave-Rejected")
def leaveRejected():
    return ("<h1>Leave Rejected Fragment!</h1>")

@app.route("/leaveApply")
def leaveApply():
    if request.method == 'POST' and 'leave_from' in request.form and 'leave_upto' in request.form and 'leave_resion' in request.form:
        # Create variables for easy access
        leaveFrom = request.form['leave_from']
        leaveUpto = request.form['leave_upto']
        leaveReason = request.form['leave_reason']
        # opening database sqlite3
        db = sqlite3.connect("project.sqlite3")
        #get cursor object it is responsible for handling database query
        cursor = db.cursor()
        #Execute database query
        cursor.execute('INSERT INTO leaveinfo(leave_from, leave_upto, reason) VALUES(?,?,?)', (leaveFrom, leaveUpto, leaveReason))
        db.commit()
        db.close()
        #corrently working.......
    return render_template('leaveApply.html')

@app.route("/leaveStatus")
def leaveStatus():
    return("<h1>Leave Status</h1>")

@app.route("/home/assignment-Create")
def assignmentCreate():
    return render_template('createAssignment.html')

@app.route("/viewAssignment")
def viewAssignment():
    data=[]
    if 'loggedin' in session:
        user = session['id']
        #print(user)
        # We need all the assignment info. for the user so we can display it on the view assignment page
        db = sqlite3.connect("project.sqlite3")
        cursor = db.cursor()
        cursor.execute('SELECT assignmentinfo.*, facultyinfo.name, facultyinfo.subject from userinfo inner join studentinfo on studentinfo.student_id = userinfo.student_id inner join assignmentinfo on assignmentinfo.class = studentinfo.class inner join facultyinfo on facultyinfo.class = assignmentinfo.class where userinfo.user_id = ?',(user,))
        data = cursor.fetchall()
        # print(data) #for testing purpose.. in CONSOLEs
        db.close()
        if data == None:
            return render_template('viewAssignment.html', data=data)
    return render_template('viewAssignment.html', data=data)

@app.route("/login/downloadFile")
def downloadFile():
    print("downloaded.....")
    return("<h1>Assignment file</h1>")

@app.route("/home/assignment-Update")
def assignmentUpdate():
    return render_template('updateAssignment.html')

@app.route("/home/assignment-Delete")
def assignmentDelete():
    return render_template('deleteAssignment.html')

@app.route("/home/students")
def allStudents():
    return render_template('allStudents.html')

@app.route("/home/report-Update")
def reportUpdate():
    return ("<h1>Student Report Updation Module!</h1>")

@app.route("/home/report-Download")
def reportDownload():
    return ("<h1>Student Report Download Module!</h1>")

@app.route("/home/report-Reset")
def reportReset():
    return ("<h1>Student Report Reset Module!</h1>")

# http://localhost/login/ - this will be the login page, we need to use both GET and POST requests
@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msgError = ''
    # Check if "email" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # opening database sqlite3
        db = sqlite3.connect("project.sqlite3")
        #get cursor object it is responsible for handling database query
        cursor = db.cursor()
        #Execute database query
        cursor.execute('SELECT * FROM userinfo WHERE email = ? AND password = ?', (email, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        db.close()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]

            #checking usertype
            if account[4] == "faculty":
                render_template('facultyDashboard.html')
            elif account[4] == "student":
                render_template('studentDashboard.html')
            # Redirect to home page
            # return 'Logged in successfully!'
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msgError = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msgError)

# http://localhost/login/logout - this will be the logout page
@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost/login/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/login/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'student_id' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        student_id = request.form['student_id']
        usertype = 'student'
        # Check if account exists using MySQL
        db = sqlite3.connect("project.sqlite3")
        cursor = db.cursor()
        # cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        cursor.execute('SELECT * FROM studentinfo WHERE student_id = ?', (request.form['student_id'],))
        id_found = cursor.fetchone()
        cursor.execute('SELECT * FROM userinfo WHERE email = ?', (request.form['email'],))
        email_found = cursor.fetchone()
        cursor.execute('SELECT * FROM userinfo WHERE username = ?', (request.form['username'],))
        user_found = cursor.fetchone()

        # validation checks
        if not id_found:
            msg = 'Invalid Student ID!'
        elif id_found and int(id_found[7]):
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email or not student_id:
            msg = 'Please fill out the form!'
        elif email_found or user_found:
            msg = 'Username/Email already exists!'
        else:
            # userid = random.randrange(999999)
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO userinfo (username, password, email, usertype, student_id) VALUES (?, ?, ?, ?, ?)', (username, password, email, usertype, student_id))
            cursor.execute('update studentinfo set "is_register" = "1" where student_id = ?', (request.form['student_id'],))
            db.commit()
            db.close()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost/login/home - this will be the home page, only accessible for logged-in users
@app.route('/login/home', methods=['GET', 'POST'])
def home():
    account=[]
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        db = sqlite3.connect("project.sqlite3")
        #getcursor object it is responsible for handling database query
        cursor = db.cursor()
        #Execute database query
        cursor.execute('SELECT * FROM userinfo WHERE user_id = ?', (session['id'],))
        account = cursor.fetchone()
        #close the database connection
        db.close()
        if account[4] == "faculty":
            return render_template('facultyDashboard.html', username=session['username'])
        elif account[4] == "student":
            return render_template('studentDashboard.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost/login/profile - this will be the profile page, only accessible for logged-in users
@app.route('/login/profile', methods=['GET', 'POST'])
def profile():
    account = []
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        db = sqlite3.connect("project.sqlite3")
        #getcursor object it is responsible for handling database query
        cursor = db.cursor()
        #Execute database query
        cursor.execute('SELECT * FROM userinfo WHERE user_id = ?', (session['id'],))
        account = cursor.fetchone()
        db.commit()
        #close the database connection
        db.close()
        if account[4] == "faculty":
            return render_template('profile.html', account=account)
        elif account[4] == "student":
            return render_template('studentProfile.html', account=account)
        #return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(debug=True, host="0.0.0.0", port=80)
