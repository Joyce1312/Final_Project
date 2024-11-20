import os
class Config:
    #Configures the session
    #SESSION_PERMANENT is a configuration variable (Flask specific)
    """
    - Setting this to false means that the session data will all be 
    deleted after you close the browser 

    - Setting it to true means that the session data would last 
    until the specified PERMANENT_SESSION_LIFETIME expires, even if the browser is closed
    """
    SESSION_PERMANENT = False
    #Stores them in a server file instead of the cookie for privacy reasons
    SESSION_TYPE = "filesystem"
    #Sets up the database URI (Uniform Resorces Identifier) in flask app configuration
    #Tells flask to use SQLite and store database in sqlite:///ecommerce.db
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'instance', 'ecommerce.db')
    #This turns off a feature that tracks modifications to objects in the database. 
    #False will help you can save memory a
    SQLALCHEMY_TRACK_MODIFICATIONS = False