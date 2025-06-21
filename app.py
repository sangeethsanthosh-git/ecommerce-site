from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template,session, redirect, url_for, request,flash
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key='IAm bAtMN'
products = [
     {
        'id': 1,
        'name': 'T-Shirt',
        'price': 499,
        'image': '4.jpg'
    },
    {
        'id': 2,
        'name': 'Shoes',
        'price': 1299,
        'image': '2.jpg'
    },
    {
        'id': 3,
        'name': 'Wrist Watch',
        'price': 2499,
        'image': '3.jpg'
    }
]
@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html',products=products)
@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return "Product not found!", 404

    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']

    # If product already in cart, increase quantity
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': product.price,
            'image': product.image,
            'quantity': 1
        }

    session.modified = True
    return redirect(url_for('home'))
@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0

    for item_id, item in cart.items():
        subtotal = item['price'] * item['quantity']
        total += subtotal
        item['subtotal'] = subtotal
        cart_items.append(item)

    return render_template('cart.html', cart=cart_items, total=total)


@app.route('/remove-from-cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
        session.modified = True
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    session.pop('cart', None)  # clear the cart
    return render_template('checkout.html')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form['name']
        price=float(request.form['price'])
        image = request.form['image']
        
        new_product = Product(name=name, price=price, image=image)
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
    products = Product.query.all()
    return render_template('admin.html', products=products)
# ✅ MAIN APP RUNNER
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if not exists

        # ✅ Insert sample products if table is empty
        if not Product.query.first():
            db.session.add_all([
                Product(name='T-Shirt', price=499, image='4.jpg'),
                Product(name='Shoes', price=1299, image='2.jpg'),
                Product(name='Wrist Watch', price=2499, image='3.jpg')
            ])
            db.session.commit()
            print("✅ Sample products inserted!")

    app.run(debug=True)
