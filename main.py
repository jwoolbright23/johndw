from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import jinja2
import os
import cgi
import re

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:jdw23rkw@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(360))

    def __init__(self, name, body):
        self.name = name
        self.body = body

@app.route("/")
def index():
    template_blog = jinja_env.get_template("new_blog.html")
    return template_blog.render()

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
    template_blog = jinja_env.get_template("new_blog.html")
    template_post = jinja_env.get_template("new_post.html")
    template_entry = jinja_env.get_template("new_entry.html")
    new_blog_id = request.args.get("id")

    if new_blog_id == None:
        posts = Blog.query.all()
        return template_blog.render(posts=posts, name="Blogs on Blogs")
    else:
        post = Blog.query.get(new_blog_id)
        return template_entry.render(post=post, name="Blog Entry")

@app.route("/new_post", methods=["POST", "GET"])
def new_post():
    template_blog = jinja_env.get_template("new_blog.html")
    template_post = jinja_env.get_template("new_post.html")
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
            new_entry = Blog(blog_name, blog_entry)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect("/new_blog?id={}".format(new_entry.id)) 
        else:
            return template_post.render(name="New Entry", name_error=name_error, entry_error=entry_error, 
                blog_name=blog_name, blog_entry=blog_entry)
    
    return template_post.render(name="New Entry")


if __name__ == "__main__":
    app.run()