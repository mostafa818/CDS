from extensions import db
from datetime import datetime
from abc import ABC, ABCMeta, abstractmethod

# Get the actual metaclass from db.Model
ModelMetaclass = type(db.Model)

class CombinedMeta(ModelMetaclass, ABCMeta):
    pass

# Association Tables
cart_products = db.Table('cart_products',
    db.Column('cart_id', db.String(50), db.ForeignKey('cart.id'), primary_key=True),
    db.Column('product_id', db.String(50), db.ForeignKey('product.id'), primary_key=True)
)

order_products = db.Table('order_products',
    db.Column('order_id', db.String(50), db.ForeignKey('order.id'), primary_key=True),
    db.Column('product_id', db.String(50), db.ForeignKey('product.id'), primary_key=True)
)

# Abstract User Class
class User(db.Model, ABC, metaclass=CombinedMeta):
    __abstract__ = True
    
    # Private attributes (marked with - in diagram)
    _id = db.Column('id', db.String(50), primary_key=True)
    _name = db.Column('name', db.String(100), nullable=False)
    _email = db.Column('email', db.String(120), unique=True, nullable=False)
    _password = db.Column('password', db.String(128), nullable=False)

    # Property getters and setters for encapsulation
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
    
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, value):
        self._email = value
    
    @property
    def password(self):
        return self._password
    
    @password.setter
    def password(self, value):
        self._password = value

    def login(self, password_attempt):
        return self._password == password_attempt

    def sign_up(self):
        db.session.add(self)
        db.session.commit()

    @abstractmethod
    def update_data(self, **kwargs):
        pass
    
class Customer(User):
    # Private attributes (marked with - in diagram)
    _address = db.Column('address', db.String(200))
    _phone = db.Column('phone', db.String(20))
    
    # Property getters and setters
    @property
    def address(self):
        return self._address
    
    @address.setter
    def address(self, value):
        self._address = value
    
    @property
    def phone(self):
        return self._phone
    
    @phone.setter
    def phone(self, value):
        self._phone = value
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy=True)
    cart = db.relationship('Cart', backref='customer', uselist=False, lazy=True)

    def update_data(self, **kwargs):
        if 'address' in kwargs: self.address = kwargs['address']
        if 'phone' in kwargs: self.phone = kwargs['phone']
        if 'name' in kwargs: self.name = kwargs['name']
        if 'email' in kwargs: self.email = kwargs['email']
        db.session.commit()

    def get_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "address": self.address,
            "phone": self.phone
        }

    def set_data(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

    def to_dict(self):
        return self.get_data()

    def create_orders(self, products_list):
        new_order = Order(id=str(datetime.now().timestamp()), customer_id=self.id)
        new_order.products.extend(products_list)
        new_order.calculate_price()
        db.session.add(new_order)
        db.session.commit()
        return new_order

    def view_order(self, order_id):
        return Order.query.filter_by(id=order_id, customer_id=self.id).first()

    def check_profile_data(self):
        return self.get_data()

    def view_cart(self):
        return self.cart

class Admin(User):
    # Private attributes (marked with - in diagram)
    _status = db.Column('status', db.String(50))
    
    # Property getters and setters
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        self._status = value

    def update_data(self, **kwargs):
        if 'status' in kwargs: self.status = kwargs['status']
        if 'name' in kwargs: self.name = kwargs['name']
        db.session.commit()

    def get_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "status": self.status
        }

    def set_data(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

    def to_dict(self):
        return self.get_data()

    def manage_products(self):
        pass

    def view_users_profile(self):
        pass

class Courier(User):
    # Private attributes (marked with - in diagram)
    _status = db.Column('status', db.String(50))
    _salary = db.Column('salary', db.Float)
    _area = db.Column('area', db.String(100))
    
    # Property getters and setters
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        self._status = value
    
    @property
    def salary(self):
        return self._salary
    
    @salary.setter
    def salary(self, value):
        self._salary = value
    
    @property
    def area(self):
        return self._area
    
    @area.setter
    def area(self, value):
        self._area = value
    
    orders = db.relationship('Order', backref='courier', lazy=True)

    def update_data(self, **kwargs):
        if 'status' in kwargs: self.status = kwargs['status']
        if 'area' in kwargs: self.area = kwargs['area']
        db.session.commit()

    def get_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "status": self.status,
            "salary": self.salary,
            "area": self.area
        }

    def set_data(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

    def to_dict(self):
        return self.get_data()

    def view_orders(self):
        return Order.query.filter_by(courier_id=self.id).all()

    def edit_area(self, new_area):
        self.area = new_area
        db.session.commit()

    def choose_order(self, order):
        order.courier_id = self.id
        db.session.commit()

class ServiceOfferor(User):
    # Private attributes (marked with - in diagram)
    _service_type = db.Column('service_type', db.String(50))
    _area = db.Column('area', db.String(100))
    
    # Property getters and setters
    @property
    def service_type(self):
        return self._service_type
    
    @service_type.setter
    def service_type(self, value):
        self._service_type = value
    
    @property
    def area(self):
        return self._area
    
    @area.setter
    def area(self, value):
        self._area = value
    
    products = db.relationship('Product', backref='provider', lazy=True)

    def update_data(self, **kwargs):
        if 'service_type' in kwargs: self.service_type = kwargs['service_type']
        if 'area' in kwargs: self.area = kwargs['area']
        db.session.commit()

    def get_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "service_type": self.service_type,
            "area": self.area
        }

    def set_data(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

    def to_dict(self):
        return self.get_data()

    def add_products(self, product):
        product.provider_id = self.id
        db.session.add(product)
        db.session.commit()

    def update_products(self, product, **kwargs):
        if product.provider_id == self.id:
            if 'name' in kwargs: product.name = kwargs['name']
            if 'price' in kwargs: product.price = kwargs['price']
            db.session.commit()

    def remove_products(self, product_id):
        prod = Product.query.get(product_id)
        if prod and prod.provider_id == self.id:
            db.session.delete(prod)
            db.session.commit()

class Product(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    weight = db.Column(db.Float)
    price = db.Column(db.Float)
    category = db.Column(db.String(50))
    status = db.Column(db.String(50))
    
    provider_id = db.Column(db.String(50), db.ForeignKey('service_offeror.id'), nullable=False)

    def get_product_details(self):
        return {
            "id": self.id,
            "name": self.name,
            "details": self.details,
            "price": self.price
        }

    def update_product(self, name, price, details):
        self.name = name
        self.price = price
        self.details = details
        db.session.commit()

    def check_availability(self):
        return self.status == 'Available'

    def calculate_weight(self):
        return self.weight

    def set_availability(self, status):
        self.status = status
        db.session.commit()
    
    def to_dict(self):
        return self.get_product_details()

class Cart(db.Model):
    # Private attributes (marked with - in diagram)
    _id = db.Column('id', db.String(50), primary_key=True)
    _price = db.Column('price', db.Float, default=0.0)
    customer_id = db.Column(db.String(50), db.ForeignKey('customer.id'), nullable=False)
    
    # Property getters and setters
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value
    
    @property
    def price(self):
        return self._price
    
    @price.setter
    def price(self, value):
        self._price = value
    
    products = db.relationship('Product', secondary=cart_products, lazy='subquery',
        backref=db.backref('carts', lazy=True))

    def add_product(self, product):
        if product not in self.products:
            self.products.append(product)
            self.calculate_price()
            db.session.commit()

    def remove_product(self, product_id):
        product = next((p for p in self.products if p.id == product_id), None)
        if product:
            self.products.remove(product)
            self.calculate_price()
            db.session.commit()

    def calculate_price(self):
        self.price = sum(p.price for p in self.products)
        return self.price

    def clear_cart(self):
        self.products = []
        self.price = 0.0
        db.session.commit()

    def checkout(self):
        pass

class Order(db.Model):
    # Private attributes (marked with - in diagram)
    _id = db.Column('id', db.String(50), primary_key=True)
    _order_date = db.Column('order_date', db.DateTime, default=datetime.utcnow)
    _status = db.Column('status', db.String(50))
    _pickup_address = db.Column('pickup_address', db.String(200))
    _delivery_address = db.Column('delivery_address', db.String(200))
    _total_weight = db.Column('total_weight', db.Float)
    _price = db.Column('price', db.Float)
    
    customer_id = db.Column(db.String(50), db.ForeignKey('customer.id'), nullable=False)
    courier_id = db.Column(db.String(50), db.ForeignKey('courier.id'), nullable=True)
    
    # Property getters and setters
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value
    
    @property
    def order_date(self):
        return self._order_date
    
    @order_date.setter
    def order_date(self, value):
        self._order_date = value
    
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        self._status = value
    
    @property
    def pickup_address(self):
        return self._pickup_address
    
    @pickup_address.setter
    def pickup_address(self, value):
        self._pickup_address = value
    
    @property
    def delivery_address(self):
        return self._delivery_address
    
    @delivery_address.setter
    def delivery_address(self, value):
        self._delivery_address = value
    
    @property
    def total_weight(self):
        return self._total_weight
    
    @total_weight.setter
    def total_weight(self, value):
        self._total_weight = value
    
    @property
    def price(self):
        return self._price
    
    @price.setter
    def price(self, value):
        self._price = value

    products = db.relationship('Product', secondary=order_products, lazy='subquery',
        backref=db.backref('orders', lazy=True))

    def create_order(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        db.session.add(self)
        db.session.commit()

    def add_products(self, product):
        self.products.append(product)
        self.calculate_price()
        db.session.commit()

    def remove_products(self, product_id):
        product = next((p for p in self.products if p.id == product_id), None)
        if product:
            self.products.remove(product)
            self.calculate_price()
            db.session.commit()

    def calculate_price(self):
        self.price = sum(p.price for p in self.products if p.price)
        self.total_weight = sum(p.weight for p in self.products if p.weight)
        return self.price

    def update_status(self, new_stats):
        self.status = new_stats
        db.session.commit()

    def cancel_order(self):
        self.status = "Cancelled"
        db.session.commit()

    def change_pickup_addr(self, new_addr):
        self.pickup_address = new_addr
        db.session.commit()

    def change_delivery_addr(self, new_addr):
        self.delivery_address = new_addr
        db.session.commit()
