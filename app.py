from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config  #Imports config class from config.py
from flask_login import LoginManager, login_user, login_required, logout_user
import os

# Import db from db.py
from db import db
from models import *  # Import models after db is initialized
from models import create_admin_user  # Import function to create the admin user


# This line initializes your web application, and tells Flask where to find your files and how to set up the app
#__name__ refers to the current file name
app = Flask(__name__)
#Applies all the configuration from config.py
app.config.from_object(Config)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_default_key')
#This creates an instance of the SQLAlchemy class and associates it with the app you just created. 
#Now db can be used to interact with the database in your Flask application 
# Initialize db with app
db.init_app(app)

# Initialize LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

#Initialize migration extensions
migrate = Migrate(app, db)

#Activates a session
Session(app)
# Define the app context to create the admin user
with app.app_context():
    create_admin_user()




#Get the user from the database
@login_manager.user_loader
def load_user(user_id):
    #Rreturns user info with the given user_id
    return User.query.get(int(user_id))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/listing")
def listing():
    return render_template("listing.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    #Forget any user_id
    #session.clear()
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        #Ensure email is provided
        if not email:
            flash('Please Enter Your Email.','error')

        #Ensure password is provided
        if not password:
            flash('Please Enter Your Password.','error')

        #Check if the user exits by filtering for the email
        user = User.query.filter_by(email=email).first()

        #Checks if email and password match the user
        if user and check_password_hash(user.password_hash, password):
            #Successful login and sets the user session
            login_user(user)
            #Checks if this user is admin the display admin dashboard
            if user.role == 'admin':
                return redirect("/admin/dashboard")
            #If not then display user dashboard
            else:
                return redirect("/user/dashboard")
        #If email and password don't match the display error message
        else:
            flash('Invaild email or password','error')
        
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    return render_template("admin_dash.html")

@app.route("/user/dashboard")
@login_required
def user_dashboard():
    return render_template("user_dash.html")

@app.route("/product")
def product():
    return render_template("product.html")