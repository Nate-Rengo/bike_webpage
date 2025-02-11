from flask import Flask, render_template, request, redirect
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import foreign
from flask_login import LoginManager, UserMixin, login_user,logout_user,current_user,login_required

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY']="secretKey"
db= SQLAlchemy(app)

class Bike(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        brand= db.Column(db.String(80))
        model = db.Column(db.String(80))
        weight= db.Column(db.Integer)
        price= db.Column(db.Integer)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        user = db.relationship('User', backref='bikes')


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    age = db.Column(db.Integer)


with app.app_context():
    db.create_all()
login_manager = LoginManager(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(uid):
    user = User.query.get(uid)
    return user


@app.route("/")
def home():
    return render_template('home_user.html')


@app.route("/create_user", methods=['GET', 'POST'])
def handle_post_create():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        age = int(request.form['age'])
        userCheck = User.query.filter_by(username=username).first()
        if not userCheck:
            user = User(name=name, username=username, password=password, age=age)
            db.session.add(user)
            db.session.commit()
            user2 = User.query.filter_by(username=username).first()
            login_user(user2)
            return redirect('/')
        else:
            return render_template('createError_user.html')

    return render_template('form_user.html')


@app.route("/login", methods=['GET', 'POST'])
def handle_post_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            return redirect("/")
        else:
            return render_template('login_error_user.html')
    return render_template('loginform_user.html')


@app.route("/view_all_users")
@login_required
def read():
    user = User.query.all()
    return render_template('read_user.html', users=user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/update_user", methods=['GET', 'POST'])
@login_required
def update():
    if request.method == 'POST':
        curPassword = request.form['password']
        newPassword = request.form['newPassword']
        user = User.query.filter_by(username=current_user.username).first()
        if curPassword == user.password:
            user.password = newPassword
            db.session.add(user)
            db.session.commit()
            return redirect('view_all_users')
        else:
            return render_template('updateError_user.html')
    return render_template('update_user.html')




@app.route("/create_bike", methods=['GET','POST'])
@login_required
def handle_post_create_bike():
    if request.method=='POST':
        brand = request.form['brand']
        model = request.form['model']
        weight= float(request.form['weight'])
        price= float(request.form['price'])
        bike = Bike(brand=brand, model=model,weight=weight,price=price, user_id=current_user.id)
        db.session.add(bike)
        db.session.commit()
        return redirect('/read')
    return render_template('form_bike.html')

@app.route("/read")
@login_required
def read_bike():
    bikes= Bike.query.all()
    return render_template('read_bike.html',bikes=bikes)
@app.route("/update/<id>", methods=['GET','POST'])
@login_required
def update_bike(id):
    b= Bike.query.filter_by(id=int(id)).first()
    if request.method=='POST':
        b.brand=request.form['brand']
        b.model = request.form['model']
        b.weight= float(request.form['weight'])
        b.price= float(request.form['price'])
        db.session.commit()
        return redirect('/read')
    return render_template('form_bike_update.html',brand=b.brand, model=b.model,weight=b.weight,price=b.price, id=id)
@app.route("/delete/<id>")
@login_required
def delete_bike(id):
    b = Bike.query.filter_by(id=int(id)).first()
    db.session.delete(b)
    db.session.commit()
    bikes = Bike.query.all()
    return render_template('read_bike.html',bikes=bikes)
@app.errorhandler(Exception)
def errorfunc_user(e):
    return render_template('error_catchall.html', error=str(e))

app.run()