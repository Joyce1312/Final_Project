from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config  #Imports config class from config.py

# This line initializes your web application, and tells Flask where to find your files and how to set up the app
#__name__ refers to the current file name
app = Flask(__name__)
#Applies all the configuration from config.py
app.config.from_object(Config)
#This creates an instance of the SQLAlchemy class and associates it with the app you just created. 
#Now db can be used to interact with the database in your Flask application 
db = SQLAlchemy(app)
#Initialize migration extensions
migrate = Migrate(app, db)
#Activates a session
Session(app)

import models


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/listing")
def listing():
    return render_template("listing.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/product")
def product():
    return render_template("product.html")