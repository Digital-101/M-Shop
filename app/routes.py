import os
from flask import render_template, url_for, flash, redirect, request, abort, session, jsonify
from app import app, db
from app.forms import RegistrationForm, LoginForm, ProductForm
from app.models import User, Product, Cart
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

# Sample FAQ Data (Could be from a database)
faqs = [
    {"question": "What payment methods do you accept?", "answer": "We accept Visa, MasterCard and PayPal."},
    {"question": "Do you offer international shipping?", "answer": "Yes, we ship worldwide. Shipping costs may vary based on location."},
    {"question": "How can I track my order?", "answer": "You will receive an email with a tracking link once your order ships."},
    {"question": "What is your return policy?", "answer": "We offer a 30-day return policy for unused products in their original packaging."},
    {"question": "How do I contact customer support?", "answer": "You can reach us via email at support@emshop.com or call us at +27 31-456-7890."},
]

@app.route('/faq')
def faq():
    return render_template('faq.html', faqs=faqs)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            # Check if there is a 'next' page in the query parameters for redirect
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/home")
@login_required
def home():
    return render_template('home.html')  # Make sure this template exists

# Decorator to restrict access to users with manager role (role_id = 1)
def manager_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role_id != 1:  # Only allow managers with role_id 1
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# Route to view all products (everyone can view)
@app.route("/products")
def view_products():
    products = Product.query.all()
    return render_template('products.html', products=products)

# Route to add a product (only for managers)
@app.route("/product/new", methods=['GET', 'POST'])
@manager_required
def add_product():
    if current_user.role is None or current_user.role.name != 'Manager':
        abort(403)  # Only managers can access this

    form = ProductForm()

    if form.validate_on_submit():
        # Handle image upload
        if form.image.data:
            image_file = save_image(form.image.data)

        # Create a new product instance
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            created_by = current_user.id,
            image_file=image_file
        )

        # Add the product to the database
        db.session.add(product)
        db.session.commit()

        flash('Product has been added!', 'success')
        return redirect(url_for('manager_dashboard'))

    return render_template('create_product.html', form=form)

def save_image(image):
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)
    return filename

# Route to update a product (only for managers)
@app.route("/product/<int:product_id>/update", methods=['GET', 'POST'])
@manager_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm()
    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.description = form.description.data
        db.session.commit()
        flash('Product has been updated!', 'success')
        return redirect(url_for('view_products'))
    elif request.method == 'GET':
        form.name.data = product.name
        form.price.data = product.price
        form.description.data = product.description
    return render_template('create_product.html', title='Update Product', form=form, legend='Update Product')

# Route to delete a product (only for managers)
@app.route("/product/<int:product_id>/delete", methods=['POST'])
@manager_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product has been deleted!', 'success')
    return redirect(url_for('view_products'))

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)

    # Fetch the product from the database
    product = Product.query.get(product_id)
    if not product:
        return "Product not found", 404

    # Check if product is already in the cart
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1  # Increment quantity
    else:
        cart[product_id_str] = {
            'name': product.name,
            'price': product.price,
            'quantity': 1,
            'image_file': product.image_file,
        }

    session['cart'] = cart  # Save cart to session
    session['cart_count'] = sum(item['quantity'] for item in cart.values())  # Initialize or update cart count
    session.modified = True  # Mark session as modified
    return redirect(url_for('view_cart'))

@app.route('/remove_from_cart/<int:product_id>', methods=['GET'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        # Remove the product from the cart
        del cart[product_id_str]
        
        # Update the cart count
        session['cart_count'] = sum(item['quantity'] for item in cart.values())  # Sum the quantities of remaining items
        session.modified = True  # Mark the session as modified

    return redirect(url_for('view_cart'))  # Redirect back to the cart view

@app.route('/cart')
@login_required
def view_cart():
    cart = session.get('cart', {})
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    delivery_price = 100.00  # Example delivery price
    total = subtotal + delivery_price
    
    return render_template('cart.html', cart=cart, subtotal=subtotal, delivery_price=delivery_price, total=total)

@app.context_processor
def cart_count():
    cart = session.get('cart', {})
    total_items = sum(item['quantity'] for item in cart.values())  # Sum all quantities
    return {'cart_count': total_items}

from flask import request, redirect, url_for, session, flash
from flask_login import login_required

@app.route('/update_cart/<int:product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    # Get the current cart from the session
    cart = session.get('cart', {})
    
    # Check if the product is in the cart
    if str(product_id) in cart:
        # Get the new quantity from the form
        new_quantity = request.form.get('quantity', type=int)
        
        if new_quantity is None or new_quantity <= 0:
            # If the new quantity is invalid, remove the item from the cart
            flash('Invalid quantity. Item removed from cart.', 'warning')
            del cart[str(product_id)]
        else:
            # Update the quantity in the cart
            cart[str(product_id)]['quantity'] = new_quantity
            flash('Cart updated successfully!', 'success')
    else:
        flash('Item not found in cart.', 'danger')

    # Update the cart in the session
    session['cart'] = cart
    
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    total_price = 0  # ✅ Initialize total_price to avoid unbound variable error

    if 'cart' in session and session['cart']:
        cart = session['cart']
        total_price = sum(item['price'] * item['quantity'] for item in cart.values())  # ✅ Ensure total_price is always defined

    if request.method == 'POST':
        if not session.get('cart'):
            flash('Your cart is empty!', 'warning')
            return redirect(url_for('products'))

        cart = session['cart']
        out_of_stock = False

        try:
            # Get all product IDs in the cart
            product_ids = cart.keys()
            products = Product.query.filter(Product.id.in_(product_ids)).all()

            # Convert to dictionary for quick lookup
            product_dict = {p.id: p for p in products}

            # Validate stock before making any changes
            for product_id, item in cart.items():
                product = product_dict.get(int(product_id))

                if not product:
                    flash(f"Product with ID {product_id} not found.", 'danger')
                    out_of_stock = True
                    continue

                if product.stock < item['quantity']:
                    flash(f"Not enough stock for {product.name}.", 'danger')
                    out_of_stock = True

            if out_of_stock:
                return redirect(url_for('checkout'))  # Don't modify stock if any item fails

            # Deduct stock now that all checks have passed
            for product_id, item in cart.items():
                product = product_dict.get(int(product_id))
                if product:
                    product.stock -= item['quantity']

            db.session.commit()  # ✅ Commit changes once, after all checks pass

            # Clear cart session
            session.pop('cart', None)
            session['cart_count'] = 0

            flash('Checkout successful!', 'success')
            return redirect(url_for('products'))

        except Exception as e:
            db.session.rollback()  # ❌ Rollback in case of an error
            flash('An error occurred during checkout. Please try again.', 'danger')
            print(f"Checkout error: {e}")  # ✅ Print error for debugging
            return redirect(url_for('checkout'))

    return render_template('checkout.html', total_price=total_price)  # ✅ total_price is always defined

@app.route("/manager")
@login_required
def manager_dashboard():
    # Debugging: print the user's role
    print(f"Current User Role: {current_user.role}")  # Check if the role is being retrieved correctly
    print(f"Current User Role Name: {current_user.role.name if current_user.role else 'No role'}")
    
    # Ensure that only users with the "Manager" role can access
    if current_user.role is None or current_user.role.name != 'Manager':
        abort(403)  # Forbidden if not a manager
    return render_template('dashboard.html')

@app.route('/manager/users', methods=['GET'])
@login_required
def view_users():
    # Only allow managers to view users
    if current_user.role is None or current_user.role.name != 'Manager':
        abort(403)  # Forbidden if not a manager
    
    # Query all users from the database
    users = User.query.all()
    return render_template('view_users.html', users=users)