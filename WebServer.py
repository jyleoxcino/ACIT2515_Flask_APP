from pathlib import Path

from flask import Flask, jsonify, render_template, request

from database import db
from models import Product, Order, ProductsOrder

############################################
#               CREATE DATABASE
############################################

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"
app.instance_path = Path(".").resolve()
db.init_app(app)

############################################
#               LANDING
############################################

@app.route("/")
def home():
    data = Product.query.all()
    return render_template("index.html", products=data)

############################################
#
#               PRODUCT MANAGEMENT
#
############################################

############################################
#               GET PRODUCT
############################################

@app.route("/api/product/<string:name>", methods=["GET"])
def api_get_product(name):
    product = db.session.get(Product, name.lower())
    if not product:
        return f"{name} doesn't exist", 404
    product_json = product.to_dict()
    return jsonify(product_json)

############################################
#               CREATE PRODUCT
############################################

@app.route("/api/product", methods=["POST"])
def api_create_product():
    data = request.json
    # Check all data is provided
    for key in ("name", "price", "quantity"):
        if key not in data:
            return f"The JSON provided is invalid (missing: {key})", 400

    try:
        price = float(data["price"])
        quantity = int(data["quantity"])
        # Make sure they are positive
        if price < 0 or quantity < 0:
            raise ValueError
    except ValueError:
        return (
            "Invalid values: price must be a positive float and quantity a positive integer",
            400,
        )

    # Create Product for session
    product = Product(
        name=data["name"],
        price=price,
        quantity=quantity,
    )
    
    # Add product to database
    db.session.add(product)
    db.session.commit()
    
    return "Item added to the database"

############################################
#               DELETE PRODUCT
############################################

@app.route("/api/product/<string:name>", methods=["DELETE"])
def api_delete_product(name):
    product = db.session.get(Product, name.lower())
    if not product:
        return f"Product doesn't exist", 400

    db.session.delete(product)
    db.session.commit()

    return f"{name} has been deleted from database.", 200

############################################
#               UPDATE PRODUCT
############################################

@app.route("/api/product/<string:name>", methods=["PUT"])
def api_update_product(name):
    data = request.json
    # Check all data is provided
    for key in ("name", "price", "quantity"):
        if key not in data:
            return f"The JSON provided is invalid (missing: {key})", 400

    product = db.session.get(Product, data["name"])
    if not product:
        return f"Product doesn't exist", 400

    try:
        price = float(data["price"])
        quantity = int(data["quantity"])
        # Make sure they are positive
        if price < 0 or quantity < 0:
            raise ValueError
    except ValueError:
        return (
            "Invalid values: price must be a positive float and quantity a positive integer",
            400,
        )

    product.price = price
    product.quantity = quantity

    db.session.commit()

    return f"{name} has been updated."

############################################
#
#               ORDER MANAGEMENT
#
############################################

############################################
#               GET ORDER
############################################

@app.route("/api/order/<int:order_id>", methods=["GET"])
def api_get_order(order_id):
    products_order = db.session.get(Order, order_id)
    if not products_order:
        return f"order {order_id} not found.", 400
    products_order_json = products_order.to_dict()

    # get products and quantity
    products_order_query = db.session.query(
        ProductsOrder).filter_by(order_id=order_id).all()
    products_order_list = []
    products_order_price = 0

    for product in products_order_query:
        product_info = db.session.get(Product, product.product_name)
        if not product_info:
            return f"{product} doesn't exist", 400
        products_order_price += product_info.price * product.quantity
        products_order_list.append(
            {"name": product.product_name, "quantity": product.quantity})

    products_order_json["products"] = products_order_list
    products_order_json["price"] = products_order_price

    return products_order_json

############################################
#               CREATE ORDER
############################################

@app.route("/api/order/", methods=["POST"])
def api_create_order():

    data = request.json

    # Validate payload
    for key in ("customer_name", "customer_address", "products", "price"):
        if key not in data:
            return f"The JSON provided is invalid (missing: {key})", 400

    # Store data
    customer_name = data["customer_name"]
    customer_address = data["customer_address"]
    products = data["products"]

    # validate price
    try:
        price = float(data["price"])
        if price < 0:
            raise ValueError
    except ValueError:
        return "Invalid values: price must be a positive float and quantity a positive integer", 400

    local_price = 0

    # Iterate through each product in products payload
    for product in products:
        product_info = db.session.get(Product, product["name"])

        # check if product exists
        if not product_info:
            return f"Product: {product['name']}, not in database. ", 400

        # check product data types
        if type(product["quantity"]) is float:
            return f"{product['name']} must have a positive integer as a value.", 400
        elif type(product["quantity"]) is str:
            return f"{product['name']} must have a positive <b>integer</b> as a value.", 400

        # calculate local prices for comparison later
        local_price += product_info.price * product["quantity"]

    # check if local costs same as price in payload
    if (local_price != price):
        print(price)
        print(local_price)
        return "Error in cost, check local store cost", 400

    # Create [Order] Object
    order = Order(
        name=customer_name,
        address=customer_address
    )

    # Insert [Order] Object
    db.session.add(order)
    db.session.commit()

    # Create [ProductOrder] Object and Insert [ProductOrder]
    for product in products:
        obj = ProductsOrder(
            order_id=order.id, product_name=product["name"], quantity=product["quantity"])
        db.session.add(obj)
        print(".", end="")

    db.session.commit()

    return api_get_order(order.id)

############################################
#               PROCESS ORDER
############################################

@app.route("/api/order/<int:order_id>", methods=["PUT"])
def api_process_order(order_id):

    # SELECT [order]
    order = db.session.get(Order, order_id)
    if order.completed == True:
        return f"This order has already been completed.", 400

    # SELECT [Products_Order]
    products_order = db.session.query(
        ProductsOrder).filter_by(order_id=order_id).all()
    products_order_price = 0

    # Iterate through each product in order list
    for product in products_order:
        # grab store info relating to product
        store_product_info = db.session.get(Product, product.product_name)
        store_product_quantity = store_product_info.quantity

        # set order quantity to store quantity if order quantity is greater
        if product.quantity > store_product_quantity:
            product.quantity = store_product_quantity

        # subtract from store quantity
        store_product_info.quantity -= product.quantity
        # add price after if any quantity adjustments
        products_order_price += store_product_info.price * product.quantity

    # set order to completed
    order.completed = True

    # run query to update session
    db.session.commit()

    # Return Order Details
    return api_get_order(order.id), 200


if __name__ == "__main__":
    app.run(debug=True)
