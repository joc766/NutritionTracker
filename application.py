import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
from datetime import datetime, date, time, timedelta
# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///fitness.db")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        # Ensure username was submitted
        if not username:
            return apology("must provide email", 403)

        if "@yale.edu" not in username:
            return apology("must provide a yale email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

#homepage
@app.route("/", methods=["GET", "POST"])
@login_required
def homepage():
    if request.method == "GET":
        today = date.today()
        access = db.execute("SELECT * FROM lastaccessed WHERE id = :id", id=session["user_id"])
        if not access:
            db.execute("INSERT INTO lastaccessed (date, id) VALUES (:date, :id)", date = today, id=session["user_id"])
        else:
            last = access[0]["date"]
            last = str(last)
            today = str(today)
            if last != today:
                db.execute("DELETE FROM food WHERE id=:id", id=session["user_id"])
                db.execute("UPDATE lastaccessed SET date=:date WHERE id=:id", date=today, id=session["user_id"])
                user = db.execute("SELECT * FROM Daily WHERE id=:id", id=session["user_id"])
                calories = user[0]["permcals"]
                db.execute("UPDATE Daily SET calories=:permcals WHERE id=:id", permcals=calories, id=session["user_id"])
        user = db.execute("SELECT * FROM Daily WHERE id=:id", id = session["user_id"])
        if not user:
            return render_template("homepage.html", length = 0, totcals=0, remaining=0, excess=0, goalcals=0, totcarbs=0, goalcarbs=0, totprotein=0, gaolprotein=0, totfats=0, goalfats=0)
        calories = db.execute("SELECT calories FROM food WHERE id IN (:id)", id=session["user_id"])
        carbs = db.execute("SELECT carbs FROM food WHERE id IN (:id)", id=session["user_id"])
        protein = db.execute("SELECT protein FROM food WHERE id IN (:id)", id=session["user_id"])
        fats = db.execute("SELECT fats FROM food WHERE id IN (:id)", id=session["user_id"])
        i = 0
        totcals = 0
        totcarbs = 0
        totfats = 0
        totprotein = 0
        for food in calories:
            totcals = totcals + calories[i]["calories"]
            i+=1
        i = 0
        for food in carbs:
            totcarbs = totcarbs + carbs[i]["carbs"]
            i+=1
        i = 0
        for food in protein:
            totprotein = totprotein + protein[i]["protein"]
            i+=1
        i = 0
        for food in fats:
            totfats = totfats + fats[i]["fats"]
            i+=1
        i = 0
        goalcals = user[0]["calories"]
        goalcarbs = user[0]["carbs"]
        goalprotein = user[0]["protein"]
        goalfats = user[0]["fats"]
        remaining = goalcals-totcals
        excess = abs(remaining)
        #probably could've done this in fewer lines by just making one food dictionary instead of one for each macro nutrient, but I don't have time
        favorites = db.execute("SELECT * FROM favorites WHERE id IN (:id) ORDER BY count DESC", id=session["user_id"])
        if not favorites:
            length = 0
            print(length)
        else:
            length = len(favorites)
            print(length)
        return render_template("homepage.html", length=length, favorites=favorites, excess=excess, remaining=remaining, totcals=totcals, totcarbs=totcarbs, totprotein=totprotein, totfats=totfats, goalcals=goalcals, goalcarbs=goalcarbs, goalprotein=goalprotein, goalfats=goalfats)
    else:
        i = int(request.form.get("food"))
        favorite = db.execute("SELECT * FROM favorites WHERE id IN (:id) ORDER BY count DESC", id=session["user_id"])
        calories = favorite[i]["calories"]
        carbs = favorite[i]["carbs"]
        protein = favorite[i]["protein"]
        fats = favorite[i]["fats"]
        name = favorite[i]["name"]
        count = favorite[i]["count"]
        count += 1
        db.execute("INSERT INTO food (calories, carbs, protein, fats, id) VALUES (:calories, :carbs, :protein, :fats, :id)", calories=calories, carbs=carbs, protein=protein, fats=fats, id=session["user_id"])
        db.execute("UPDATE favorites SET count=:count WHERE id=:id AND name=:name", count=count, id=session["user_id"], name=name)
        user = db.execute("SELECT * FROM Daily WHERE id=:id", id = session["user_id"])
        if not user:
            return render_template("homepage.html", totcals=0, remaining=0, excess=0, totcarbs=0, goalcarbs=0, totprotein=0, gaolprotein=0, totfats=0, goalfats=0)
        calories = db.execute("SELECT calories FROM food WHERE id IN (:id)", id=session["user_id"])
        carbs = db.execute("SELECT carbs FROM food WHERE id IN (:id)", id=session["user_id"])
        protein = db.execute("SELECT protein FROM food WHERE id IN (:id)", id=session["user_id"])
        fats = db.execute("SELECT fats FROM food WHERE id IN (:id)", id=session["user_id"])
        i = 0
        totcals = 0
        totcarbs = 0
        totfats = 0
        totprotein = 0
        for food in calories:
            totcals = totcals + calories[i]["calories"]
            i+=1
        i = 0
        for food in carbs:
            totcarbs = totcarbs + carbs[i]["carbs"]
            i+=1
        i = 0
        for food in protein:
            totprotein = totprotein + protein[i]["protein"]
            i+=1
        i = 0
        for food in fats:
            totfats = totfats + fats[i]["fats"]
            i+=1
        i = 0
        goalcals = user[0]["calories"]
        goalcarbs = user[0]["carbs"]
        goalprotein = user[0]["protein"]
        goalfats = user[0]["fats"]
        remaining = goalcals-totcals
        excess = abs(remaining)
        #probably could've done this in fewer lines by just making one food dictionary instead of one for each macro nutrient, but I don't have time
        favorites = db.execute("SELECT * FROM favorites WHERE id IN (:id) ORDER BY count DESC", id=session["user_id"])
        length = len(favorites)
        return render_template("homepage.html", length=length, favorites=favorites, excess=excess, remaining=remaining, totcals=totcals, totcarbs=totcarbs, totprotein=totprotein, totfats=totfats, goalcals=goalcals, goalcarbs=goalcarbs, goalprotein=goalprotein, goalfats=goalfats)

@app.route("/excercise", methods=["GET", "POST"])
@login_required
def excercise():
    if request.method == "GET":
        return render_template("excercise.html")
    else:
        nutrition = db.execute("SELECT * FROM Daily WHERE id=:id", id=session["user_id"])
        weight = db.execute("SELECT weight FROM Nutrition WHERE id=:id", id=session["user_id"])
        weight = weight[0]["weight"]
        dailycals = int(nutrition[0]["calories"])
        ex = request.form.get("excercise")
        hrs = float(request.form.get("hours"))
        print(ex)
        # if you have time, consider making a function that makes an exact estimate for each person's weight based on the given data
        if ex == "rowing":
            if weight < 155:
                cals = hrs * 465
            elif weight >= 155 and weight < 185:
                cals = hrs * 576
            elif weight >= 185:
                cals = hrs * 688
        elif ex == "walking":
            if weight < 155:
                cals = hrs * 270
            elif weight >= 155 and weight < 185:
                cals = hrs * 334
            elif weight >= 185:
                cals = hrs * 400
        elif ex == "running":
            if weight < 155:
                cals = hrs * 600
            elif weight >= 155 and weight < 185:
                cals = hrs * 744
            elif weight >= 185:
                cals = hrs * 888
        elif ex == "swimming":
            if weight < 155:
                cals = 480 * hrs
            elif weight >= 155 and weight <= 185:
                cals = 744 * hrs
            elif weight > 185:
                cals = 888 * hrs
        elif ex == "biking":
            if weight < 155:
                cals = 525 * hrs
            elif weight >= 155 and weight <= 185:
                cals = 595 * hrs
            elif weight >= 185:
                cals = 710 * hrs
#all calculations for cals are based on data from https://www.health.harvard.edu/diet-and-weight-loss/calories-burned-in-30-minutes-of-leisure-and-routine-activities
        elif ex == "select":
            return apology("Please select an excercise")
        calories = dailycals + cals
        db.execute("UPDATE Daily SET calories=:calories WHERE id=:id", calories=calories, id=session["user_id"])
        return render_template("excercise.html")


@app.route("/goals", methods=["GET", "POST"])
@login_required
def goals():
    #TODO
    if request.method == "GET":
        user = db.execute("SELECT * FROM Nutrition WHERE id=:id", id = session["user_id"])
        if not user:
            return render_template("goals.html")
        else:
            height = user[0]["height"]
            m = height * 0.0256
            weight = user[0]["weight"]
            kg = weight * 0.453592
            goalweight = user[0]["goalweight"]
            sex = user[0]["sex"]
            age = user[0]["age"]
            activity = user[0]["activity"]
            if sex == "male":
                bmr = 66 + (13.7 * kg) + (500 * m) - (6.8 * age)
            if sex =="female":
                bmr = 655 + (9.6 * kg) + (180 * m) - (4.7 * age)
    #bmr equation calculated using the Harris-Benedict equation
            if activity == "sedentary":
                maintain = bmr*1.2
            elif activity == "lightly":
                maintain = bmr*1.375
            elif activity == "moderately":
                maintain = bmr*1.55
            elif activity == "very":
                maintain = bmr*1.725
            elif activity == "extra":
                maintain = bmr*1.9
            difference = goalweight - weight
            if goalweight > weight:
                calories = maintain + 500
                carbs = (calories/4)*0.60
            elif goalweight < weight:
                if difference < 15:
                    calories = maintain - 500
                elif difference > 15 and difference < 30:
                    calories = maintain - 750
                elif difference >= 30:
                    calories = maintain - 1000
                carbs = (calories/4)*0.45
            if difference < 1:
                calories = maintain
            protein = weight
            fats = (calories/9)*0.25
            calories = round(calories)
            protein = round(protein)
            fats = round(fats)
            carbs = round(carbs)
            return render_template("goals.html", calories=calories, carbs=carbs, protein=protein, fats=fats)
    else:
        sex = request.form.get("sex")
        sex = sex.lower()
        if sex != "male" and sex != "female":
                return apology("sex must be male or female")
        age = int(request.form.get("age"))
        height = int(request.form.get("height"))
        m = height * 0.0256
        weight = int(request.form.get("weight"))
        kg = weight * 0.453592
        goalweight = int(request.form.get("goalweight"))
        user = db.execute("SELECT * FROM Nutrition WHERE id=:id", id = session["user_id"])
        if not user:
            db.execute("INSERT INTO Nutrition (id, height, weight, goalweight, sex, age) VALUES (:id, :height, :weight, :goalweight, :sex, :age)", age=age, id=session["user_id"], height = height, weight=weight, goalweight=goalweight, sex=sex)
        else:
            db.execute("UPDATE Nutrition SET height=:height, weight=:weight, goalweight=:goalweight, age=:age, sex=:sex WHERE id=:id", height=height, weight=weight, goalweight=goalweight, age=age, sex=sex, id = session["user_id"])
        if sex == "male":
            bmr = 66 + (13.7 * kg) + (500 * m) - (6.8 * age)
        if sex =="female":
            bmr = 655 + (9.6 * kg) + (180 * m) - (4.7 * age)
#bmr equation calculated using the Harris-Benedict equation
        activity = request.form.get("activity")
        db.execute("UPDATE nutrition SET activity=:activity WHERE id=:id", activity=activity, id=session["user_id"])
        if activity == "sedentary":
            maintain = bmr*1.2
        elif activity == "lightly":
            maintain = bmr*1.375
        elif activity == "moderately":
            maintain = bmr*1.55
        elif activity == "very":
            maintain = bmr*1.725
        elif activity == "extra":
            maintain = bmr*1.9
        difference = goalweight - weight
        if goalweight >= weight:
            calories = maintain + 500
            carbs = (calories/4)*0.60
        elif goalweight < weight:
            if difference < 15:
                calories = maintain - 500
            elif difference > 15 and difference < 30:
                calories = maintain - 750
            elif difference >= 30:
                calories = maintain - 1000
            carbs = (calories/4)*0.45
        if difference < 1:
            calories = maintain
        protein = weight
        fats = (calories/9)*0.25
        calories = round(calories)
        protein = round(protein)
        fats = round(fats)
        carbs = round(carbs)
        if not user:
            db.execute("INSERT INTO Daily (calories, carbs, fats, protein, id, permcals) VALUES (:calories, :carbs, :fats, :protein, :id, :permcals)", permcals=calories, calories=calories, carbs=carbs, fats=fats, protein=protein, id=session["user_id"])
        else:
            db.execute("UPDATE Daily SET calories=:calories, carbs=:carbs, fats=:fats, protein=:protein WHERE id=:id", calories=calories, carbs=carbs, fats=fats, protein=protein, id=session["user_id"])
        return render_template("goals.html", protein=protein, carbs=carbs, fats=fats, calories=calories)
            #calculate weight gain formulas
            #calculate weight loss formulas



@app.route("/daily", methods=["GET", "POST"])
@login_required
def food():
    if request.method == "GET":
        # make a frequently used foods page that displays foods that have been input
        # create a favorites table
        return render_template("daily.html")
    else:
        #for the sake of efficiency, can you make different functions within the same route so that excercise and food can be separate but on the same page?
        name = request.form.get("name").lower()
        print(name)
        calories = float(request.form.get("calories"))
        carbs = float(request.form.get("carbs"))
        protein = float(request.form.get("protein"))
        fats = float(request.form.get("fats"))
        db.execute("INSERT INTO food (calories, carbs, protein, fats, id) VALUES (:calories, :carbs, :protein, :fats, :id)", calories=calories, carbs=carbs, protein=protein, fats=fats, id=session["user_id"])
        favorites = db.execute("SELECT * FROM favorites WHERE name=:name AND id=:id", name=name, id=session["user_id"])
        print(favorites)
        if not favorites:
            count = 1
            db.execute("INSERT INTO favorites (calories, carbs, protein, fats, id, name, count) VALUES (:calories, :carbs, :protein, :fats, :id, :name, :count)", calories=calories, carbs=carbs, protein=protein, fats=fats, id=session["user_id"], name=name, count=count)
        else:
            count = favorites[0]["count"]
            count += 1
            db.execute("UPDATE favorites SET count=:count WHERE name=:name AND id=:id", count=count, name=name, id=session["user_id"])
        return render_template("daily.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        hash = generate_password_hash(password)
        if confirmation != password:
            return apology("confirmation does not match password")
        elif not username or not password or not confirmation:
            return apology("missing input")
        if "@yale.edu" not in username:
            return apology("please enter a yale email")
        elif username == db.execute("SELECT username FROM users WHERE username = :username", username=username):
            return apology("username taken")
        else:
            if password.isdigit():
                db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=hash)
                id = db.execute("SELECT id FROM users WHERE username = :username", username=username)
                id = id[0]['id']
                session["user_id"] = id
                return redirect("/")
            return apology("password must contain a number")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")