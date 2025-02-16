from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    # ForeignKey to the Role model
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False, default=1)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', role_id='{self.role_id}')"

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    # Relationship with User (one role can be assigned to many users)
    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f"Role('{self.name}')"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #stock = db.Column(db.Integer, default=0)

    image_file = db.Column(db.String(120), nullable=False, default='xr.png')

    def __repr__(self):
        return f"Product('{self.name}', '{self.price}', '{self.image_file}')"
    
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Add relationship to access product details
    product = db.relationship('Product', backref='cart_items')

    def __repr__(self):
        return f"Cart('{self.user_id}', '{self.product_id}', '{self.quantity}')"