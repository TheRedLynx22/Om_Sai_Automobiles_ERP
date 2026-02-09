from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Customer, Quotation, TractorModel, User, Role
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
import os
import math  # Import math for ceil function
from flask import send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# --- Data to be inserted (Complete Model List from models.csv) ---
# NOTE: Added placeholder values for new cost fields for initial population.
MODELS_DATA = [
    {'name': 'Jivo 225 Reguler', 'fixed_price': 551980.0}, {'name': 'JIVO 245 DI 4WD Normal', 'fixed_price': 602800.0},
    {'name': '265 XP PLUS 37 HP LT', 'fixed_price': 698500.0}, {'name': '265 XP PLUS 37 HP', 'fixed_price': 681600.0},
    {'name': '265 Orchard LT', 'fixed_price': 666460.0}, {'name': '305 DI Orchard', 'fixed_price': 660320.0},
    {'name': '275 SP PLUS', 'fixed_price': 699540.0}, {'name': '275 YOVU TECH', 'fixed_price': 785440.0},
    {'name': 'JIVO 305 DI 4WD Reguler (Red)', 'fixed_price': 640500.0}, {'name': '475 SP PLUS', 'fixed_price': 824940.0},
    {'name': '475 SP LT', 'fixed_price': 862650.0}, {'name': '475 YOVU TECH 4WD', 'fixed_price': 933270.0},
    {'name': '475 YOVU TECH RCX', 'fixed_price': 869680.0}, {'name': 'ARJUN 555 FLT', 'fixed_price': 949480.0},
    {'name': 'ARJUN 555 LT', 'fixed_price': 961560.0}, {'name': 'ARJUN 555 4S PTO', 'fixed_price': 954490.0},
    {'name': 'ARJUN 555 AUX', 'fixed_price': 962050.0}, {'name': '575 XP PLUS', 'fixed_price': 868520.0},
    {'name': '575 SP FT', 'fixed_price': 897700.0}, {'name': '575 NST', 'fixed_price': 897060.0},
    {'name': '575 YOVU TECH', 'fixed_price': 966820.0}, {'name': '585 NSTAUX', 'fixed_price': 955690.0},
    {'name': '585 XP PLUS', 'fixed_price': 978930.0}, {'name': '605 YOVU TECH', 'fixed_price': 999900.0},
    {'name': '605 YOVU TECH PS', 'fixed_price': 1005000.0}
]
# ------------------------------------------------------------------

app = Flask(__name__)

# --- CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///showroom.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_strong_secret_key_here'  # **CHANGE THIS IN PRODUCTION**
# ---------------------

db.init_app(app)

# --- LOGIN MANAGER SETUP ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect unauthenticated users here

@login_manager.user_loader
def load_user(user_id):
    """Callback to reload the user object from the user ID stored in the session."""
    return db.session.get(User, int(user_id))

# Ensure PDF folder exists
if not os.path.exists("pdfs"):
    os.makedirs("pdfs")

@app.route('/pdfs/<path:filename>')
def view_pdf(filename):
    return send_from_directory('pdfs', filename)

# --- PDF GENERATION FUNCTION (UPDATED) ---
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os, math
from datetime import datetime

def generate_pdf(quotation, customer):
    tractor = TractorModel.query.filter_by(name=quotation.model).first()
    if not tractor:
        print(f"Error: Tractor model '{quotation.model}' not found.")
        return None

    # Compute final price
    on_road = math.ceil(
        tractor.fixed_price +
        tractor.rto_charge +
        tractor.insurance_cost +
        tractor.handling_charge
    )

    safe_name = customer.name.replace(" ", "_")
    safe_model = quotation.model.replace(" ", "_").replace("/", "_")
    date_str = quotation.date.strftime("%d-%m-%Y")
    filename = f"pdfs/{safe_name}_{safe_model}_{date_str}.pdf"

    pdf = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin = 40

    def money(n):
        return f"₹ {int(n):,}"

    # ---------------- HEADER ----------------
    pdf.setFont("Helvetica-Bold", 18)
    pdf.setFillColorRGB(0.8, 0, 0)
    pdf.drawCentredString(width/2, height - 60, "OM SAI AUTOMOBILES")

    pdf.setFont("Helvetica", 10)
    pdf.setFillColorRGB(0, 0, 0)
    pdf.drawCentredString(width/2, height - 82, "Shivdhan Plaza, Thigalsthal, Pune-Nashik Road, Rajgurunagar")
    pdf.drawCentredString(width/2, height - 98, "Tal. Khed, Pune – 410505")
    pdf.drawCentredString(width/2, height - 114, "Contact: 9552523242 / 9767099111")

    y = height - 150

    # --------------- TABLE 1: CUSTOMER DETAILS ----------------
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin, y, "Customer Details")
    y -= 12
    pdf.line(margin, y, width - margin, y)
    y -= 20

    pdf.setFont("Helvetica", 10)
    pdf.drawString(margin, y, f"Name: {customer.name}")
    y -= 16
    pdf.drawString(margin, y, f"Phone: {customer.phone}")
    y -= 16
    pdf.drawString(margin, y, f"Date: {date_str}")

    # --------------- TABLE 2: QUOTATION DETAILS ----------------
    y -= 40
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margin, y, "Quotation Summary")
    y -= 12
    pdf.line(margin, y, width - margin, y)
    y -= 20

    pdf.setFont("Helvetica", 10)

    pdf.drawString(margin, y, "Tractor Model:")
    pdf.drawRightString(width - margin, y, f"{quotation.model}")
    y -= 16

    pdf.drawString(margin, y, "Ex-Showroom Price:")
    pdf.drawRightString(width - margin, y, money(tractor.fixed_price))
    y -= 16

    pdf.drawString(margin, y, "RTO Charges:")
    pdf.drawRightString(width - margin, y, money(tractor.rto_charge))
    y -= 16

    pdf.drawString(margin, y, "Insurance Cost:")
    pdf.drawRightString(width - margin, y, money(tractor.insurance_cost))
    y -= 16

    pdf.drawString(margin, y, "Handling Charges:")
    pdf.drawRightString(width - margin, y, money(tractor.handling_charge))
    y -= 20

    # Total box
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(margin, y, "TOTAL ON-ROAD PRICE:")
    pdf.drawRightString(width - margin, y, money(on_road))

    # ---------------- FOOTER ----------------
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.setFillColorRGB(0.2, 0.2, 0.2)
    pdf.drawString(margin, 40, "Note: Prices are subject to change without prior notice.")

    pdf.save()
    return filename



# --- LOGIN/LOGOUT ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Logged in successfully as {user.name}.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
# ---------------------------


@app.route('/')
@login_required
def index():
    customers = Customer.query.all()
    return render_template('index.html', customers=customers)


@app.route('/add_customer', methods=['POST'])
@login_required
def add_customer():
    # Only Sales Agents are allowed to add customers
    if current_user.role.name != 'Sales Agent' and current_user.role.name != 'Admin':
        flash('You do not have permission to add customers.', 'error')
        return redirect(url_for('index'))

    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']

    # Prevent duplicate phone numbers
    existing_customer = Customer.query.filter_by(phone=phone).first()
    if existing_customer:
        flash(f"Error: Customer with phone number {phone} already exists.", 'error')
        return redirect(url_for('index'))

    new_customer = Customer(name=name, phone=phone, email=email)
    db.session.add(new_customer)
    db.session.commit()
    
    flash(f"Customer '{name}' added successfully.", 'success')
    return redirect(url_for('index'))


@app.route('/create_quotation/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def create_quotation(customer_id):
    # Only Sales Agents are allowed to create quotations
    if current_user.role.name != 'Sales Agent' and current_user.role.name != 'Admin':
        flash('You do not have permission to create quotations.', 'error')
        return redirect(url_for('index'))

    customer = db.session.get(Customer, customer_id)
    if customer is None:
        flash('Customer not found.', 'error')
        return redirect(url_for('index'))
        
    tractor_models = TractorModel.query.all()

    if request.method == 'POST':
        model_id = request.form.get('model_id')
        price = float(request.form.get('price'))  # This is the fixed_price
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        
        selected_model = db.session.get(TractorModel, model_id)
        
        if not selected_model:
            flash('Invalid tractor model selected.', 'error')
            return redirect(url_for('create_quotation', customer_id=customer_id))

        # Create quotation entry
        new_quotation = Quotation(
            model=selected_model.name,
            price=price,
            date=date,
            customer_id=customer.id
        )

        db.session.add(new_quotation)
        db.session.commit()

        # Generate PDF using the full model details from the DB
        pdf_path = generate_pdf(new_quotation, customer)

        # Save PDF path in database
        if pdf_path:
            new_quotation.pdf_path = pdf_path
            db.session.commit()
            flash(f'Quotation for {selected_model.name} created successfully. PDF generated!', 'success')
        else:
            db.session.rollback()
            flash('Error generating PDF. Please check server logs.', 'error')

        return redirect(url_for('index'))

    return render_template('create_quotation.html', customer=customer, models=tractor_models)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # --- INITIAL DATA INSERTION FOR ROLES/USER ---
        if Role.query.count() == 0:
            admin_role = Role(name='Admin')
            sales_role = Role(name='Sales Agent')
            db.session.add_all([admin_role, sales_role])
            db.session.commit()

            if User.query.count() == 0:
                # Create a test Admin user (Username: admin, Password: password123)
                admin_user = User(
                    username='admin', 
                    name='System Admin', 
                    role_id=admin_role.id
                )
                admin_user.set_password('password123')
                # Create a sample Sales Agent (Username: joe, Password: password)
                sales_user = User(
                    username='joe', 
                    name='Joe Smith', 
                    role_id=sales_role.id
                )
                sales_user.set_password('password')
                
                db.session.add_all([admin_user, sales_user])
                db.session.commit()
                print("--- Initial Roles and Users ('admin:password123', 'joe:password') created. ---")
        
        # --- TRACTOR MODEL DATA INSERTION (UPDATED WITH NEW FIELDS) ---
        if TractorModel.query.count() == 0:
            new_models = []
            for item in MODELS_DATA:
                fixed_price = item['fixed_price']
                # Calculate placeholder costs based on a percentage of the fixed price
                rto = round(fixed_price * 0.10)   # 10% for RTO
                insurance = round(fixed_price * 0.05) # 5% for Insurance
                handling = round(fixed_price * 0.005) # 0.5% for Handling
                
                new_models.append(TractorModel(
                    name=item['name'], 
                    fixed_price=fixed_price,
                    rto_charge=rto,
                    insurance_cost=insurance,
                    handling_charge=handling
                ))
            
            db.session.add_all(new_models)
            db.session.commit()
            print(f"--- Successfully inserted {len(MODELS_DATA)} Tractor Models with cost components. ---")
        # -----------------------------------------------------------

    app.run(debug=True)
