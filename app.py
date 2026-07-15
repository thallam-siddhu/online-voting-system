from flask import Flask, render_template, request, redirect, session
import sqlite3
import random
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
import os

print("Current working directory:", os.getcwd())
print("Database path:", os.path.abspath("voting.db"))
app.secret_key = "onlinevoting123"

generated_otp = None


# ---------------- LOGIN ---------------- #

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("voting.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["email"] = email
            return redirect("/home")
        else:
            return "Invalid Email or Password!"

    return render_template("login.html")


# ---------------- REGISTER ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():
    global generated_otp

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        otp = request.form["otp"]

        if generated_otp is None:
            return "Please click Send OTP first."

        if otp != str(generated_otp):
            return "Invalid OTP!"

        conn = sqlite3.connect("voting.db")
        cursor = conn.cursor()

        # Check duplicate email
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        if user:
            conn.close()
            return "Email already registered! <br><a href='/'>Go to Login</a>"

        cursor.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (name, email, password)
        )

        conn.commit()
        conn.close()

        generated_otp = None

        return """
        <h2>Registration Successful!</h2>
        <a href="/">Go to Login</a>
        """

    return render_template("register.html")


# ---------------- SEND EMAIL OTP ---------------- #

@app.route("/send_otp", methods=["POST"])
def send_otp():
    global generated_otp

    email = request.form["email"]

    generated_otp = random.randint(100000, 999999)

    sender = "siddhureddy9701@gmail.com"
    app_password = "iwjmtfzequvumdlz"

    msg = MIMEText(f"Your Online Voting OTP is: {generated_otp}")
    msg["Subject"] = "Online Voting OTP"
    msg["From"] = sender
    msg["To"] = email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, app_password)
        server.send_message(msg)
        server.quit()

        return "OTP Sent Successfully! Check your email."

    except Exception as e:
        print(e)
        return "Error sending OTP!"
# ---------------- HOME ---------------- #

@app.route("/home")
def home():
    if "email" not in session:
        return redirect("/")

    return render_template("home.html")


# ---------------- VOTE ---------------- #

@app.route("/vote", methods=["POST"])
def vote():

    if "email" not in session:
        return redirect("/")

    email = session["email"]
    candidate = request.form["candidate"]

    conn = sqlite3.connect("voting.db")
    cursor = conn.cursor()

    # Check whether the user has already voted
    cursor.execute("SELECT voted FROM users WHERE email=?", (email,))
    result = cursor.fetchone()

    if result is None:
        conn.close()
        return "User not found!"

    if result[0] == 1:
        conn.close()
        return "You have already voted!"

    # Save vote
    cursor.execute(
        "INSERT INTO votes(user_email, candidate) VALUES (?, ?)",
        (email, candidate)
    )

    # Mark user as voted
    cursor.execute(
        "UPDATE users SET voted=1 WHERE email=?",
        (email,)
    )

    conn.commit()

    # Count votes
    cursor.execute("SELECT COUNT(*) FROM votes WHERE candidate='Candidate A'")
    a = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM votes WHERE candidate='Candidate B'")
    b = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM votes WHERE candidate='Candidate C'")
    c = cursor.fetchone()[0]

    conn.close()

    return render_template("result.html", a=a, b=b, c=c)
# ---------------- ADMIN LOGIN ---------------- #

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "siddhu" and password == "4565":

            conn = sqlite3.connect("voting.db")
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM votes WHERE candidate='Candidate A'")
            a = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM votes WHERE candidate='Candidate B'")
            b = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM votes WHERE candidate='Candidate C'")
            c = cursor.fetchone()[0]

            conn.close()

            return render_template("admin.html", a=a, b=b, c=c)

        else:
            return "Invalid Admin Login!"

    return render_template("admin_login.html")


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- RESET ELECTION ---------------- #

@app.route("/reset")
def reset():

    conn = sqlite3.connect("voting.db")
    cursor = conn.cursor()

    # Delete all votes
    cursor.execute("DELETE FROM votes")

    # Allow all users to vote again
    cursor.execute("UPDATE users SET voted=0")

    conn.commit()
    conn.close()

    return """
    <h2>Election Reset Successfully!</h2>
    <a href="/admin">Back to Admin</a>
    """


# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run(debug=True)