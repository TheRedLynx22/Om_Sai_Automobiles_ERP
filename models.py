from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ------------------------------------
# --- NEW/UPDATED MODELS FOR ROLES ---
# ------------------------------------
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy=True)

class User(UserMixin, db.Model): # Inherit from UserMixin
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False) # Stores the hashed password
    name = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks a plain password against the stored hash."""
        return check_password_hash(self.password_hash, password)

# ------------------------------------
# --- EXISTING MODELS ---
# ------------------------------------
class TractorModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    fixed_price = db.Column(db.Float, nullable=False) # Ex-Showroom Price

    # --- NEW COLUMNS ADDED TO MATCH TRACEBACK ---
    rto_charge = db.Column(db.Float, nullable=False, default=0.0)
    insurance_cost = db.Column(db.Float, nullable=False, default=0.0)
    handling_charge = db.Column(db.Float, nullable=False, default=0.0)
    # --------------------------------------------

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100))
    quotations = db.relationship('Quotation', backref='customer', lazy=True)

class Quotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False) # This is the fixed_price (Ex-Showroom)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    pdf_path = db.Column(db.String(200))