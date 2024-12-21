import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash
import pytz

# Import db instance from db.py to establish model relationships
from db import db

# User Model
class User(db.Model):
    __tablename__ = 'users'  # Define table name in the database
    id = db.Column(db.Integer, primary_key=True)  # Primary key for user
    first_name = db.Column(db.String(50), nullable=False)  # User's first name
    last_name = db.Column(db.String(50), nullable=False)  # User's last name
    email = db.Column(db.String(100), unique=True, nullable=False)  # Unique email for user authentication
    password_hash = db.Column(db.String(128), nullable=False)  # Hashed password
    role = db.Column(db.String(10), default="user")  # User role (default: user)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('America/New_York')))  # Timestamp in NY timezone

    #Relationship to Cart table with a back-reference named 'cart'
    cart = db.relationship('Cart', back_populates='user', uselist=False)

    # Relationship to Order table with a back-reference named 'orders'
    orders = db.relationship('Order', back_populates='user')

    # Flask-Login method: Checks if user is active
    def is_active(self):
        return True

    # Flask-Login method: Checks if user is authenticated
    def is_authenticated(self):
        return True

    # Flask-Login method: Checks if user is anonymous (always False for logged-in users)
    def is_anonymous(self):
        return False

    # Property to get the full name of the user
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    # String representation for debugging
    def __repr__(self):
        return f'<User {self.full_name}>'

    # Flask-Login method: Returns unique user identifier
    def get_id(self):
        return str(self.id)

# Function to create an admin user if none exists
def create_admin_user():
    if not User.query.filter_by(email='admin@example.com').first():  # Check if admin exists
        admin_first = 'admin'
        admin_last = 'test'
        admin_email = 'admin@example.com'
        admin_password = generate_password_hash('admin_password')  # Hash admin password
        admin = User(first_name=admin_first, last_name=admin_last, email=admin_email, password_hash=admin_password, role='admin')
        db.session.add(admin)  # Add admin user to the session
        db.session.commit()  # Commit to save the user in the database
        print("Admin user created successfully!")
    else:
        print("Admin user already exists.")

#Cart Model
class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the cart
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Link to the User who owns the cart
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('America/New_York')))  # Timestamp for when the cart was created
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('America/New_York')), onupdate=lambda: datetime.now(pytz.timezone('America/New_York')))  # Automatically updated timestamp

    # Relationship to User table
    user = db.relationship('User', back_populates='cart')

    # Relationship to CartItem table
    items = db.relationship('CartItem', back_populates='cart', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Cart {self.id} for User {self.user_id}>'
    
# CartItem Model
class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the cart item
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)  # Link to the Cart it belongs to
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # Link to the Product being added to the cart
    quantity = db.Column(db.Integer, nullable=False, default=1)  # Quantity of the product in the cart
    price_at_addition = db.Column(db.Float, nullable=False)  # Price of the product at the time it was added to the cart

    # Relationship to Cart table
    cart = db.relationship('Cart', back_populates='items')

    # Relationship to Product table
    product = db.relationship('Product', backref='cart_items')

    def __repr__(self):
        return f'<CartItem {self.id} (Product {self.product_id}) in Cart {self.cart_id}>'



# Product Model
class Product(db.Model):
    __tablename__ = 'products'  # Define table name in the database
    id = db.Column(db.Integer, primary_key=True)  # Primary key for product
    name = db.Column(db.String(100), nullable=False)  # Product name
    description = db.Column(db.Text, nullable=False)  # Detailed product description
    price = db.Column(db.Float, nullable=False)  # Product price
    stock = db.Column(db.Integer, nullable=False)  # Quantity available in stock
    category = db.Column(db.String, nullable=False)  # Product category

# Order Model
class Order(db.Model):
    __tablename__ = 'orders'  # Define table name in the database
    id = db.Column(db.Integer, primary_key=True)  # Primary key for order

    # Foreign Key to User table
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_user_order'), nullable=False)

    order_date = db.Column(db.Date, default=lambda: datetime.now(pytz.timezone('America/New_York')).date())  # Date of the order
    total_price = db.Column(db.Float, nullable=False)  # Total price for the order
    total_items = db.Column(db.Integer, nullable=False, default=0)  # Total items in the order
    status = db.Column(db.String(20), default='pending')  # Order status (e.g., pending, shipped)
    order_number = db.Column(db.String(36), unique=True, nullable=False)  # UUID for unique order number

    # Relationship to User table with a back-reference named 'user'
    user = db.relationship('User', back_populates='orders')

    # Relationship to OrderItem table with a back-reference named 'items'
    items = db.relationship('OrderItem', back_populates='order')

    # Dynamically calculate the total number of items in the order
    @property
    def total_order_items(self):
        return sum(item.quantity for item in self.items)

    # String representation for debugging
    def __repr__(self):
        return f'<Order {self.id} for {self.user_id}>'

    # Automatically generate a unique order number using UUID
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.order_number:
            self.order_number = str(uuid.uuid4())

# OrderItem Model
class OrderItem(db.Model):
    __tablename__ = 'order_items'  # Define table name in the database
    id = db.Column(db.Integer, primary_key=True)  # Primary key for order item

    # Foreign Key to Order table
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', name='jc_order_item'), nullable=False)

    # Foreign Key to Product table
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', name='jc_product_order_item'), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)  # Quantity of the product in this order
    price_at_purchase = db.Column(db.Float, nullable=False)  # Price of the product at the time of purchase

    # Relationship to Order table with a back-reference named 'items'
    order = db.relationship('Order', back_populates='items')

    # Relationship to Product table
    product = db.relationship('Product', backref='order_items')

