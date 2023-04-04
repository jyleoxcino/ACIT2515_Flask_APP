from database import db


class Product(db.Model):
    
    # Fields/Columns
    name = db.Column(db.String, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    # Methods
    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity
        }

class Order(db.Model):
    
    # Fields/Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    products = db.relationship('ProductsOrder', back_populates='order')
    # Methods
    def to_dict(self):
        return {
            "customer_name": self.name,
            "customer_address": self.address,
            "products": None,
            "price": None
        }
    
    
class ProductsOrder(db.Model):
    
    # Fields/Columns
    # Product foreign key is name
    product_name = db.Column(db.ForeignKey("product.name"), primary_key=True)
    # Order foreign key is ID
    order_id = db.Column(db.ForeignKey("order.id"), primary_key=True)
    # This is how many items we want
    quantity = db.Column(db.Integer, nullable=False)
    
    # Relationships and backreferences for SQL Alchemy
    product = db.relationship('Product')
    order = db.relationship('Order', back_populates='products')
    