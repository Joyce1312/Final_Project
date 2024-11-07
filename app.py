#from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# This line initializes your web application, and tells Flask where to find your files and how to set up the app
#__name__ refers to the current file name
app = Flask(__name__)

#Configures the session
#SESSION_PERMANENT is a configuration variable (Flask specific)
"""
- Setting this to false means that the session data will all be 
deleted after you close the browser 

- Setting it to true means that the session data would last 
until the specified PERMANENT_SESSION_LIFETIME expires, even if the browser is closed
"""
app.config["SESSION_PERMANENT"] = False
#Stores them in a server file instead of the cookie for privacy reasons
app.config["SESSION_TYPE"] = "filesystem"
#Activates a session
Session(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/product")
def product():
    return render_template("product.html")