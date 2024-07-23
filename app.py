from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///billing_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    items = db.relationship('Item', secondary='bill_items', backref='bills')

class BillItems(db.Model):
    __tablename__ = 'bill_items'
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manage_items', methods=['GET', 'POST'])
def manage_items():
    if request.method == 'POST':
        item_name = request.form.get('name')
        item_price = request.form.get('price')
        item_description = request.form.get('description')
        new_item = Item(name=item_name, price=float(item_price), description=item_description)
        db.session.add(new_item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('manage_items'))
    
    items = Item.query.all()
    return render_template('manage_items.html', items=items)

@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.price = float(request.form.get('price'))
        item.description = request.form.get('description')
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('manage_items'))
    return render_template('add_item.html', item=item)

@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('manage_items'))

@app.route('/generate_bill', methods=['GET', 'POST'])
def generate_bill():
    if request.method == 'POST':
        selected_items = request.form.getlist('items')
        new_bill = Bill()
        for item_id in selected_items:
            item = Item.query.get(item_id)
            new_bill.items.append(item)
        db.session.add(new_bill)
        db.session.commit()
        flash('Bill generated successfully!', 'success')
        return redirect(url_for('view_bills'))

    items = Item.query.all()
    return render_template('bill.html', items=items)

@app.route('/view_bills')
def view_bills():
    bills = Bill.query.all()
    return render_template('view_bills.html', bills=bills)

if __name__ == '__main__':
    app.run(debug=True)
