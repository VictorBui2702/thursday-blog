from flask import Flask, render_template, flash, redirect, url_for,request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager,login_user,logout_user, current_user, login_required
from flask import request
from flask import session
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
# Model - View - Controller


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
app.secret_key= "asshd"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

contributions = db.Table('contributions',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    contributors = db.relationship('User', secondary=contributions, lazy='subquery',
        backref = db.backref('posts', lazy=True))

    def __init__(self, title, body,user_id):
        self.title = title
        self.body = body
        self.user_id= user_id

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), index=True, unique=True)
  email = db.Column(db.String(120), index=True, unique=True)
  password_hash = db.Column(db.String(128), nullable=False)
  
  def __init__(self, username, email):
        self.username = username
        self.email = email

  def set_password(self, password):
      self.password_hash = generate_password_hash(password)

  def check_password(self, password):
      return check_password_hash(self.password_hash, password)

db.create_all()

@app.route("/")
# @login_required
def hello():
    # user_id = request.args.get('id')
    # post = Posts.query.get(post_id)
    username1  = session.get('username')
    print("111")
    print(username1)
    return render_template('main.html',username1=username1, posts = Posts.query.order_by(desc(Posts.created_at)).all())
    # entities = MyEntity.query.order_by(desc(MyEntity.time)).limit(3).all()


# @app.route("/posts")
# def post():
#     return "These are the posts"

@app.route('/update', methods=['POST', 'GET'])
@login_required
def update():
    post_id = request.args.get('id')
    post = Posts.query.get(post_id)
    print("111")
    print(post)
    if request.method == 'POST':   
        # get form data
        post.title = request.form['title']
        post.body = request.form['body']
        db.session.commit()

        return redirect(url_for('update', id=post_id))
    else:
        return render_template("update_form.html", post = post)

@app.route('/delete', methods=['POST','GET'])
@login_required
def delete():
    # if not session.get('logged_in'):
    #      abort(401)
    post_id = request.args.get('id')
    post = Posts.query.get(post_id)
    print(post_id)
    print("111")
    print(post)
    db.session.delete(post)
    db.session.commit()
    flash('Entry deleted')
    return redirect (url_for("hello"))

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        if not request.form['title'] or not request.form['body']:
            flash('Please enter all the required fields')
        else:
            post = Posts(request.form['title'],
                        request.form['body'],
                        current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post successfully added')
            return redirect(url_for('hello'))
    return render_template('create_form.html')


@app.route('/signup', methods=['GET', 'POST'])

def signup():
    if request.method == 'POST':
        if not request.form['email'] or not request.form['username'] or not request.form['password']:
            flash('Please enter all the required fields')
        else:
            signup = User(request.form['username'],
                            request.form['email'])
            signup.set_password(request.form['password'])
            db.session.add(signup)
            db.session.commit()
            flash('Post successfully added')
            return redirect(url_for('hello'))
    return render_template('signup_form.html')



@app.route('/login',methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email=request.form["email"]
        password=request.form["password"]
        user=User.query.filter_by(email=email).first()
        if user is not None and user.check_password(password):
            flash("Welcome Back")
            login_user(user)
            session['username'] = user.username #user here being the user object you have queried
            return redirect(url_for("hello"))
        else:
            flash("Wrong Email/Password","danger")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    del session['username']
    return render_template('login.html', posts = Posts.query.all())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)