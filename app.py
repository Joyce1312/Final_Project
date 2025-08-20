from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config  #Imports config class from config.py
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
from sqlalchemy.orm import joinedload

# Import db from db.py
from db import db
from models import *  # Import models after db is initialized
from models import create_admin_user  # Import function to create the admin user


# This line initializes your web application, and tells Flask where to find your files and how to set up the app
#__name__ refers to the current file name
app = Flask(__name__)
# Define the upload folder and allowed file extensions
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#Applies all the configuration from config.py
app.config.from_object(Config)
os.makedirs(app.instance_path, exist_ok=True)               # for SQLite file
os.makedirs("flask_session", exist_ok=True)                 # for filesystem sessions
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)     # static/images
#app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_default_key')
#This creates an instance of the SQLAlchemy class and associates it with the app you just created. 
#Now db can be used to interact with the database in your Flask application 
# Initialize db with app
db.init_app(app)

# Initialize LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

#Initialize migration extensions
migrate = Migrate(app, db)

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
    # Query products that have the category 'best seller'
    best_sellers = Product.query.filter_by(category="Best Seller").all()
    return render_template("index.html", best_sellers=best_sellers)

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "").strip()
    if query:
        # Search for products where the name or description contains the query
        results = Product.query.filter(
            (Product.name.ilike(f"%{query}%")) | (Product.description.ilike(f"%{query}%"))).all()
    else:
        results = []  # No results if the query is empty

    return render_template("listing.html", query=query, products=results)


@app.route("/listing")
def listing():
    # Query the database for all products
    all_products = Product.query.all()
    return render_template("listing.html", products=all_products)

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    # Query the database for the product with the given ID
    product = Product.query.get(product_id)
    if not product:
        return redirect("/")

    return render_template("product.html", product=product)


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
        return redirect("/")
    #Get total number of users that are admin
    total_users = User.query.filter(User.role != 'admin').count()

    #Get total number of orders
    total_orders = Order.query.count()

    #Get total products sold
    total_products_sold = db.session.query(db.func.sum(OrderItem.quantity)).join(Order, Order.id == OrderItem.order_id).filter(Order.status == 'Delivered').scalar() or 0

    #Get total revenue made (sum of total price from all orders)
    total_revenue = db.session.query(db.func.sum(Order.total_price)).filter(Order.status == 'Delivered').scalar() or 0

    #Get all admin users
    admins = User.query.filter_by(role='admin').all()
    #Creating a list of tuples (admin_data) where each tuple contains the full name and email of each admin user
    admin_data = [(admin.full_name, admin.email) for admin in admins]

    return render_template("admin_dash.html", total_users = total_users, total_orders = total_orders, total_products_sold = total_products_sold, total_revenue = total_revenue, admin_data = admin_data)

@app.route('/admin/create_admin', methods=['POST'])
@login_required
def create_admin():
    """
    Test 2nd Admin created
    test@example.com
    testing
    """
    first = request.form.get("first")
    last = request.form.get("last")
    email = request.form.get("email")
    password = request.form.get("password")

    # Check if the email already exists
    existing_admin = User.query.filter((User.email == email)).first()
    if existing_admin:
        flash('Email already exists. Please choose a different one.', 'error')
        return redirect("/admin/dashboard")

    # Hash the password for security
    hashed_password = generate_password_hash(password)

    # Create new admin account
    new_admin = User(first_name=first, last_name=last, email=email, role='admin', password_hash=hashed_password)
    
    # Add the new admin to the database
    db.session.add(new_admin)
    db.session.commit()

    return redirect("/admin/dashboard")

@app.route("/admin/users")
@login_required
def admin_users():
    # Check if the current user is an admin
    if current_user.role != 'admin':
        return redirect("/login")  # Redirect to login

    # Fetch all users from the database
    users = User.query.all()

    # Render the admin users page
    return render_template("admin_user.html", users=users)

@app.route("/admin/delete/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
     # Check if the current user is an admin
    if current_user.role != 'admin':
        return redirect("/login")  # Redirect to login
    
    # This will return 404 if user doesn't exist
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect("/admin/users")


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
        return redirect("/")

    # Fetch the product by its id
    product = Product.query.get(product_id)
    
    # If the product exists, delete it
    if product:
        db.session.delete(product)
        db.session.commit()
    else:
        flash("Product not found.", "error")

    return redirect("/admin/listing")  # Redirect back to the listing page

@app.route('/admin/orders', methods=['GET', 'POST'])
def admin_orders():
    if request.method == 'POST':
        # Handle order status update
        order_id = request.form.get('order_id')
        new_status = request.form.get('status')
        order = Order.query.get(order_id)
        
        if order:
            order.status = new_status
            db.session.commit()
            return redirect("/admin/orders")

    # Fetch all users and their orders
    users = User.query.filter_by(role='user').all()
    return render_template("admin_orders.html", users=users)


@app.route("/user/dashboard")
@login_required
def user_dashboard():
    # Fetch the current user's email and mask the password
    email = current_user.email
    password_hidden = "*" * len("password") + ("  (Hidden)")  # Mask the password with stars
    return render_template("user_dash.html", email=email, password_hidden=password_hidden)

@app.route("/user/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        # Get the updated values from the form
        first_name = request.form.get("first")
        last_name = request.form.get("last")
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Update the user's information
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.email = email
        
        # If password is provided, hash it and update it
        if password:
            current_user.password_hash = generate_password_hash(password)
        
        db.session.commit()  # Commit the changes to the database
        return redirect("/user/dashboard")
    
    return render_template("edit.html")

### User Cart Routes ###
@app.route("/user/add_to_cart/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart_user(product_id):
    # Get the product to get the price
    product = Product.query.get_or_404(product_id)
    
    # Get the current cart (assuming one cart per user)
    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not cart:
        # Create a new cart if it doesn't exist
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()

    # Check if the product is already in the cart
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()

    if cart_item:
        # If item already exists, update the quantity
        cart_item.quantity += int(request.form.get('quantity', 1))
    else:
        # Add the new product to the cart
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, 
                             quantity=int(request.form.get('quantity', 1)),
                             price=product.price)  # Store the product price
        db.session.add(cart_item)

    db.session.commit()
    return redirect("/user/cart")



@app.route("/user/edit_cart/<int:product_id>", methods=["POST"])
@login_required
def edit_cart_user(product_id):
    new_quantity = int(request.form.get("quantity"))
    product = Product.query.get_or_404(product_id)

    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not cart:
        return redirect("/user/cart")

    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()
    if cart_item:
        if new_quantity == 0:
            db.session.delete(cart_item)
        else:
            cart_item.quantity = min(new_quantity, product.stock)
        db.session.commit()
    else:
        flash("Item not found in your cart!", "error")

    return redirect("/user/cart")


@app.route("/user/remove_from_cart/<int:product_id>", methods=["POST"])
@login_required
def remove_from_cart_user(product_id):
    # Fetch the active cart of the current user
    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()
    
    # If no active cart exists
    if not cart:
        return redirect("/user/cart")

    # Log cart items before deletion attempt
    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    
    # Check if the product exists in the cart
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    else:
        flash(f"Product {product_id} not found in the cart.", "error")

    # Log cart items after removal attempt
    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()

    # Optionally deactivate cart if it's empty
    if not cart_items:
        cart.is_active = False
        db.session.commit()

    return redirect("/user/cart")





@app.route("/user/cart")
@login_required
def view_cart_user():
    # Query the cart and load associated items and product details with a joinedload
    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).options(
        joinedload(Cart.items).joinedload(CartItem.product)
    ).first()

    # If cart exists, load items, otherwise return an empty list
    cart_items = cart.items if cart else []

    # Calculate the total price of the cart
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render_template("cart.html", cart_items=cart_items, total_price=total_price)



### Guest Cart Routes ###
@app.route("/guest/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart_guest(product_id):
    # Get the product to get the price
    product = Product.query.get_or_404(product_id)
    
    # Initialize the guest cart in session if it doesn't exist
    if "cart" not in session or not isinstance(session["cart"], dict):
        session["cart"] = {}  # Initialize as a dictionary if not already a dictionary
    
    # Check if the product is already in the cart
    if product_id in session["cart"]:
        # If item already exists, update the quantity
        session["cart"][product_id]["quantity"] += int(request.form.get("quantity", 1))
    else:
        # Add the new product to the cart
        session["cart"][product_id] = {
            "quantity": int(request.form.get("quantity", 1)),
            "name": product.name,
            "price": product.price,
            "image_url": product.image_url,  # Assuming you have image_url in your Product model
        }
    
    # Mark session as modified to ensure it's saved
    session.modified = True
    
    # Redirect to the cart page for guests
    return redirect("/cart")





@app.route("/guest/edit_cart/<int:product_id>", methods=["POST"])
def edit_cart_guest(product_id):
    cart = session.get("cart", {})  # Get the current cart from session

    # Check if the product is in the cart
    if product_id in cart:
        new_quantity = int(request.form.get('quantity', 1))  # Get the new quantity from the form
        product = Product.query.get(product_id)  # Query the product to check its stock
        if new_quantity > product.stock:
            return redirect("/cart")  # Redirect if quantity exceeds stock
        
        # Update the quantity in the cart
        cart[product_id]["quantity"] = new_quantity

    # Save the updated cart back to session
    session["cart"] = cart
    session.modified = True  # Ensure session is updated
    return redirect("/cart")  # Redirect back to the cart page



@app.route("/guest/remove_from_cart/<int:product_id>", methods=["POST"])
def remove_from_cart_guest(product_id):
    cart = session.get("cart", {})  # Get the current cart from session

    # Check if the product is in the cart
    if product_id in cart:
        del cart[product_id]  # Remove the product from the cart

    # Save the updated cart back to session
    session["cart"] = cart
    session.modified = True  # Ensure session is updated
    return redirect("/cart")  # Redirect back to the cart page




@app.route("/cart")
def view_cart_guest():
    # Get the cart from session (stored as a dictionary of product ids as keys)
    cart = session.get("cart", {})

    # Ensure cart is a dictionary, if it's not, initialize it
    if not isinstance(cart, dict):
        cart = {}

    # Prepare the cart items with product details from the session
    cart_items = []
    for pid, details in cart.items():  # Now cart is expected to be a dictionary
        # Query the Product model to get the product details by ID
        product = Product.query.get(pid)
        if product:
            # Append the product details to the cart_items list
            cart_items.append({
                "id": pid,
                "name": product.name,
                "price": product.price,
                "quantity": details["quantity"],  # details["quantity"] from the session
                "stock": product.stock,
                "image_url": product.image_url,
            })

    # Calculate the total price
    total_price = sum(item["price"] * item["quantity"] for item in cart_items)

    # Render the cart template for guests
    return render_template("cart.html", cart_items=cart_items, total_price=total_price)

### Checkout Routes ###
@app.route("/checkout", methods=["POST"])
@login_required
def checkout_user():
    cart = Cart.query.filter_by(user_id=current_user.id, is_active=True).first()

    if not cart or not cart.items:
        return redirect("/user/cart")

    # Create a new order
    new_order = Order(
        user_id=current_user.id,
        total_price=sum(item.product.price * item.quantity for item in cart.items),
        total_items=sum(item.quantity for item in cart.items),
    )
    db.session.add(new_order)
    db.session.flush()  # Flush to get the order ID for the items

    # Add order items from the cart
    for cart_item in cart.items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price_at_purchase=cart_item.product.price,
        )
        db.session.add(order_item)

        # Reduce stock for each product
        cart_item.product.stock -= cart_item.quantity
        if cart_item.product.stock < 0:
            db.session.rollback()
            return redirect("/user/cart")

    # Empty the user's cart after checkout
    db.session.delete(cart)
    db.session.commit()
    return redirect("/orders")

@app.route("/orders")
@login_required
def view_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template("orders_comfirmation.html", orders=orders)



@app.route("/guest/checkout", methods=["POST"])
def checkout_guest():
    # Retrieve the cart from the session
    cart_items = session.get("cart", {})
    print("Cart content during checkout:", cart_items)  # Debugging output

    # Check if the cart is empty
    if not cart_items:
        return redirect("/cart")

    # Validate cart items to ensure proper format
    valid_items = []
    for item in cart_items.values():
        if isinstance(item, dict) and "price" in item and "quantity" in item:
            # Add item to valid_items if it has the necessary keys
            valid_items.append(item)

    # Handle invalid cart data
    if not valid_items:
        return redirect("/cart")

    # Calculate the total price
    total_price = sum(item["price"] * item["quantity"] for item in valid_items)

    # Calculate the total number of items
    total_items = sum(item["quantity"] for item in valid_items)

    # Order summary for the confirmation page
    order_summary = {
        "items": valid_items,
        "total_price": total_price,
        "total_items": total_items
    }

    # Clear the cart after checkout
    session.pop("cart", None)
    session.modified = True

    # Render the guest confirmation page
    return render_template("guest_comfirmation.html", order_summary=order_summary)



@app.route("/logout")
def logout():
    # Log out the current user
    logout_user()
    return redirect("/")





