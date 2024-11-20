from datetime import datetime
from werkzeug.security import generate_password_hash
import pytz

# Import db from db.py, not app.py
from db import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), default="user")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('America/New_York')))

    # Add this method to handle the is_active check
    def is_active(self):
        # Return True if the user is active, False if they are not
        return True  # Assuming all users are active by default
    
    # Method required by Flask-Login
    def is_authenticated(self):
        # Flask-Login checks this method to determine if the user is logged in.
        return True  # Assuming user is always authenticated

    # Method required by Flask-Login
    def is_anonymous(self):
        # Flask-Login checks this method to determine if the user is anonymous.
        return False  # Return False since this is an authenticated user

    # Method required by Flask-Login
    def get_id(self):
        return str(self.id)  # Returns the user ID as a string

# Function to create the admin user if none exist
def create_admin_user():
    # Check if an admin user already exists
    if not User.query.filter_by(email='admin@example.com').first():
        admin_first = 'admin'
        admin_last = 'test'
        admin_email = 'admin@example.com'
        admin_password = generate_password_hash('admin_password')
        admin = User(first_name=admin_first, last_name=admin_last, email=admin_email, password_hash=admin_password, role='admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists.")


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String, nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.Date, default=lambda: datetime.now(pytz.timezone('America/New_York')).date())
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    user = db.relationship('User', backref='orders')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)
    order = db.relationship('Order', backref='items')
    product = db.relationship('Product', backref='order_items')

    