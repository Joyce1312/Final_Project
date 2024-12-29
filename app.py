from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config  #Imports config class from config.py
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
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

# Define the upload folder and allowed file extensions
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to check allowed file extensions (case-insensitive)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {ext.lower() for ext in ALLOWED_EXTENSIONS}


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

@app.route("/product")
def product():
    return render_template("product.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        #Ensure email is provided
        if not email:
            flash('Please Enter Your Email.','error')

        #Ensure password is provided
        if not password:
            flash('Please Enter Your Password.','error')

        #Check if the user exists by filtering for the email
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

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Test user created
    amy.wang@gmail.com
    123
    """
    if request.method == "POST":
        #Gets all info from register form
        first = request.form.get("first")
        last = request.form.get("last")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        # Initialize an empty list for flash messages (to show all at once if needed)
        error_messages = []


        #Ensures first name is given
        if not first:
            error_messages.append('Must Enter First Name')

        #Ensures last name is given
        if not last:
            error_messages.append('Must Enter Last Name')
        
        #Ensures email is given
        if not email:
            error_messages.append('Must Enter Email')

        #Ensures password is given
        if not password:
            error_messages.append('Must Enter Password')

        #Ensures comfirmation password is given
        if not confirm:
            error_messages.append('Must Enter Confirmation Password')

        #Ensures password and comfirmation password match
        if password != confirm:
            error_messages.append('Confirmation Password Must Match Password')

        #Checks if user already exits
        user_exists = db.session.query(User).filter_by(email=email).first()
        if user_exists:
            flash('User Already Exists', 'warning')
            return redirect("/login")
        # If there are any errors, flash them and stop further processing
        if error_messages:
            for msg in error_messages:
                flash(msg, 'error')
            return redirect("/register")
        #Creates a hash for the passwprd
        hash_pw = generate_password_hash(password, method='scrypt', salt_length=16)
        # Create a new user instance
        new_user = User(first_name=first, last_name=last, email=email, password_hash=hash_pw)
        # Add the new user to the session and commit
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")

        
    return render_template("register.html")

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    #Double check and ensure that the user is an admin
    if current_user.role != 'admin':
        redirect("/")
    #Get total number of users that are admin
    total_users = User.query.filter(User.role != 'admin').count()

    #Get total number of orders
    total_orders = Order.query.count()

    #Get total products sold
    total_products_sold = db.session.query(db.func.sum(OrderItem.quantity)).scalar() or 0

    #Get total revenue made (sum of total price from all orders)
    total_revenue = db.session.query(db.func.sum(Order.total_price)).scalar() or 0

    #Get all admin users
    admins = User.query.filter_by(role='admin').all()
    #Creating a list of tuples (admin_data) where each tuple contains the full name and email of each admin user
    admin_data = [(admin.full_name, admin.email) for admin in admins]

    return render_template("admin_dash.html", total_users = total_users, total_orders = total_orders, total_products_sold = total_products_sold, total_revenue = total_revenue, admin_data = admin_data)

@app.route("/admin/add_products", methods=["GET", "POST"])
@login_required
def add_products():
    #Double check and ensure that the user is an admin
    if current_user.role != 'admin':
        redirect("/")
    #All but the image from the add product form
    if request.method == 'POST':
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        stock = request.form.get("stock")
        category = request.form.get("category")

        #Gets the upload image
        image = request.files.get("image")
        #Checking if the uploaded file is an image and if it is part of the list of allowed extensions
        if image and allowed_file(image.filename):
            # Secure the filename (to prevent directory traversal or unsafe filenames)
            filename = secure_filename(image.filename)
            #Defines the full path to where the image will be saved
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Save the image to the specified folder
            image.save(image_path)
        else:
            # If the image is not valid (either no image uploaded or invalid file type)
            flash("Invalid image type. Only JPG, PNG, JPEG, and GIF are allowed.", "error")
    
            # Redirect back to the "add product" form if there's an error
            return redirect("/admin/add_products")

        #Ensures that all fields are filled
        if not name or not description or not price or not stock or not image:
            flash("All fields are required", "error")
            return redirect("/admin/listing")
        
        # Create a new product instance with the image path
        new_product = Product(name=name, description=description, price=price, stock=stock, category=category, image_url=image_path)

        # Add the product to the database
        db.session.add(new_product)
        db.session.commit()

        flash("Product added successfully!", "success")
        return redirect("/admin/listing")  # Redirect to the admin dashboard
        
    return render_template("add_products.html")

@app.route("/admin/listing")
@login_required
def admin_listing():
    # Ensure the user is logged in and is an admin
    if current_user.role != 'admin':
        return redirect("/")

    # Query all products from the database
    products = Product.query.all()  # Get all products

    return render_template("admin_listing.html", products=products)

@app.route("/admin/delete_product/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    # Ensure the user is an admin
    if current_user.role != 'admin':
        flash("You are not authorized to delete products.", "error")
        return redirect("/")

    # Fetch the product by its id
    product = Product.query.get(product_id)
    
    # If the product exists, delete it
    if product:
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted successfully.", "success")
    else:
        flash("Product not found.", "error")

    return redirect("/admin/listing")  # Redirect back to the listing page


@app.route("/user/dashboard")
@login_required
def user_dashboard():
    return render_template("user_dash.html")

@app.route("/logout")
def logout():
    # Log out the current user
    logout_user()
    return redirect("/")





