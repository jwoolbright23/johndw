from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash
import jinja2
import os
import cgi
import re

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:rkw23jdw@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "pmotion2354"


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(360))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))


    def __init__(self, name, body, owner):
        self.name = name
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship("Blog", backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

@app.before_request
def require_login():
    allowed_routes = ["login", "new_blog", "signup", "index"]
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")


@app.route("/")
def index():
    template_blog = jinja_env.get_template("index.html")
    users = User.query.all()
    return template_blog.render(users=users, header="Blog Users")

@app.route("/new_entry", methods = ["POST", "GET"])
def new_entry():
    template_blog = jinja_env.get_template("new_blog.html")
    template_entry = jinja_env.get_template("new_entry.html")
    new_blog_id = request.args.get("id")
    if new_blog_id == None:
        posts = Blog.query.all()
        return template_blog.render(posts=posts, name="Blogs on Blogs")
    else:
        post = Blog.query.get(new_blog_id)
        return template_entry.render(post=post, name="Blog Entry")

    return template_entry.render()


@app.route("/new_blog")
def new_blog():
    template_index = jinja_env.get_template("index.html")
    template_entry = jinja_env.get_template("new_entry.html")
    template_blog = jinja_env.get_template("new_blog.html")
    template_user = jinja_env.get_template("user_posts.html")
    posts = Blog.query.all()
    blog_id = request.args.get("id")
    user_id = request.args.get("user")

    if user_id:
        posts = Blog.query.filter_by(owner_id=user_id)
        return template_user.render(posts=posts, header="User Posts")
    if blog_id:
        post = Blog.query.get(blog_id)
        return template_entry.render(post=post)
    
    return template_blog.render(posts=posts, header = "Every Blog Post Hopefully")

@app.route("/new_post", methods=["POST", "GET"])
def new_post():
    template_blog = jinja_env.get_template("new_blog.html")
    template_post = jinja_env.get_template("new_post.html")
    owner = User.query.filter_by(username=session["username"]).first()

    if request.method == "POST":
        blog_name = request.form["blog name"]
        blog_entry = request.form["blog entry"]
        name_error = ""
        entry_error = ""

        if not blog_name:
            name_error = "Please enter a blog name"
        if not blog_entry:
            entry_error = "Please enter a blog entry"

        if not entry_error and not name_error:
            new_entry = Blog(blog_name, blog_entry, owner)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect("/new_blog?id={}".format(new_entry.id)) 
        else:
            return template_post.render(name="New Entry", name_error=name_error, entry_error=entry_error, 
                blog_name=blog_name, blog_entry=blog_entry)
    
    return template_post.render(name="New Entry")

@app.route("/login", methods =["POST","GET"])
def login():
    template_login = jinja_env.get_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session["username"] = username
            flash("Logged in")
            return redirect("/new_entry")
        else:
            flash("User password incorrect, or user does not exist", "error")
    return template_login.render(header="Login")

@app.route("/signup", methods=["POST","GET"])
def signup():
    template_signup = jinja_env.get_template("signup.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        verify = request.form["verify"]

        existing_user = User.query.filter_by(username = username).first()
        if not existing_user:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            return redirect("/")
        else:
            return "<h1>Duplicate user</h1>"
    return template_signup.render()

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/new_blog")
    


if __name__ == "__main__":
    app.run()