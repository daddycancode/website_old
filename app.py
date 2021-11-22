from flask import Flask, Blueprint, redirect, url_for, render_template, flash, send_from_directory, request
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from files.files import files, target

app = Flask(__name__)
app.register_blueprint(files, url_prefix='/files')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:W00dcutt3rz@localhost:3306/flask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecretkey'

admin = Admin(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'account.login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('account.login'))
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
admin.add_view(ModelView(User, db.session, name='User DB'))
admin.add_view(FileAdmin(target, name='Files'))


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/pills')
def mattearly():
    return send_from_directory('static/images', 'mattyearly.PNG')

@app.errorhandler(404)
def error404(e):
    return render_template('404.html'), 404


account = Blueprint('account', __name__, static_folder='static', template_folder='templates')

@account.route('/', methods = ['GET', 'POST'])
@login_required
def dashboard():
    return render_template('account.html')

@account.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('account.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.check_password_hash(user.password, password):
            flash('Incorrect login details')
            return redirect(url_for('account.login'))
        login_user(user)
        return redirect(url_for('account.dashboard'))
    else:
        return render_template('login.html')

@account.route('/signup', methods = ['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('account.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('account.signup'))
        new_user = User(username=username, password=bcrypt.generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('account.login'))
    else:
        return render_template('signup.html')

@account.route('/delete')
@login_required
def delete():
    db.session.delete(current_user)
    db.session.commit()
    return redirect(url_for('account.dashboard'))

@account.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('account.login'))

app.register_blueprint(account, url_prefix='/account')


if __name__ == '__main__':
    app.run(debug=True)
