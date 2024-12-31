Project Title: E-Commerence Platform (Slime)
Video Demo: https://youtu.be/6D7-cFlIxgg
Description:
The Slime E-Commerce project is a web-based online shopping platform designed people for who would like to sell slime. 
It allows users and guestto search, select, and purchase a many differen slime products with easily. 
---

Features:
1. User and Admin Authentication 
   - Users and admins can securely login in register accounts
   - Registered users can view order history and edit their profiles
   - Admins can view basic data, orders, and users on the platform
   - Admins can create new admin users

2. Shopping Cart 
   - Update quanitiy or remove items from cart

3. Guest and User Checkout
   - Users that are not registered can also easiy shop and checkout
   - Registered users can checkout and view the order to check its status
  
4. Order, Product and User Management
   - Admins can manange users and admin accounts
   - Admins can update order status and add/remove products
6. Search
   - Allows shoppers to easily find products


---

File Descriptions:
Root Files:
1. app.py:
   - Main application file that intialized Flask app and defines each of the routes for the website
   - This is where all parts of the project like the templates, models(tables), and configirations are connected

2. config.py
   - Has all the configuration settings that the Flask app needs
     
3. db.py
   - Manages database connection using SQLAlchemey
     
4. models.py:
   - This is where the defines models(tabels) and the relatation of the tables are.

5. alembic.ini:
   - Configuation file for Alemcic that helps deal with database migration in SQLAlchemy
   - Manages the changes in the database over time
     
6. README.md:
   - Contains details of the projects features, technologies, and design decisions

Directory Folders:
1. flask_session:
   - Stores the session data that Flask uses

2.instance:
  - This is where the SQLite database is stored

3.migrations:
  - Has the database migration files that Alembic created. Each file is a change that was made to the database
  - Also has a version folder that containes each migration scripts to track the changes
  - versions:
      - 41ece915034e_try.py: Attempt to drop price column in the cart_items table
      - 67f4fa96462f_create_tables.py: Created the product, user, orders, order_items table
      - 68c2c10655e7_add_image_url_to_product_model.py: Adding a img_url column in the products table to store images 
      - 139ab05ded21.py: Adding Order number and total number of items column in the orders table
      - a24af13c5e1c_try_drop.py: Attempt to drop the price_at_addition column and add a price column instead in the cart_items table 
      - af90637d73a4_add_is_active_column_to_cart.py: Adding is_active column to the cart table and dropping the created_at and updated_at column
      - e14fd1c7ac7b_add_cart_and_cartitem_tables.py: Created cart and cart_items table
4.static:
    - images: contains the images that are needed in the website
    - script.js: Implements the toggle of the admin dashboard sidebar nav and the hiding of flash messages
    - styles.css:Styling of the webpage

5.templates:
  - add_products.html: Allows the admin to add new products
  - admin_dash.html: Admin dashboard
  - admin_layout.html: The layout that all admin pages follow
  - admin_listing.html: Displays all of the products and its details
  - admin_order.html: Allows admin to manage order status
  - cart.html: The shopping cart for users and non-users
  - edit.html: Allows registered users to edit profile (First/Last name, email, and change password)
  - guest_comfirmation.html: The confirmation that non-users get when orders are placed
  - index.html: The homepage that all users see
  - layout.html: The layout for users and non-users
  - listing.html: Displays all products that are being sold
  - login.html: Login form for users and admins
  - orders_comfirmation.html: Past Order and conformation of orders for registered users
  - product.html: Displays details of the products when specific product is clicked on
  - register.html: For non-users to create an account
  - user_dash.html: User dashboard



---

Technologies Used
- Frontend: HTML, CSS, JavaScript
- Backend: Flask (Python)
- Database: SQLAlchemy

---

Design Decisions:
1. Cart Updates: Allows shoppers to change the quantity in the cart instead of deleting re-adding to the cart again
2. Support Guest Users: Not all shoppers want to have an account, so I added a guest checkout option.
3. Main Default Admin: To create more admin accounts since the register shouldn't be the same as the user register form


---

Future Improvements:
- Advanced Search Features: Adding filters like price range and product ratings.
- Admin Dashboard: For better product(editing already created product) and order management. More analytics to track how well the business is doing.
- Payment Integration: Implementing a secure online payment system.
- Order Tracking System: To allow users to track orders instead of only seeing a status.
- User Dashboard: Favorites/Save For Later page to save or like products for future purchases
