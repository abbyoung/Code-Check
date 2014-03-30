from flask import Flask, render_template, redirect, request, g, session, url_for, flash, Markup
from model import User, Post
from flask.ext.login import LoginManager, login_required, login_user, current_user
from flaskext.markdown import Markdown
import config
import forms
import model
import re
from num2words import num2words

app = Flask(__name__)
app.config.from_object(config)

# Stuff to make login easier
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(user_id)

# End login stuff

# Adding markdown capability to the app
Markdown(app)

@app.route("/")
def index():
    #posts = Post.query.all()
    return render_template("index.html")

@app.route("/", methods=["POST"])
def get_url():
    url = request.form.get("url")
    if not re.match('^(http|https)://', url):
        url = 'http://' + url
     
    return redirect(url_for("results", url=url))

@app.route("/results")
def results():
    url = request.args.get("url")
    page = model.PageParser(url)
    extract = page.extract()
    links_list = page.get_links()
    outline = page.get_outline()
    stats = page.get_stats()
    headings = stats['Number of Headings']
    headings = num2words(headings)
    links = stats['Number of Links']
    links = num2words(links)
    body = Markup(page.get_body())
    body = body.replace('\n', '')
    body = body.replace('{{', Markup('<span class="highlight">'))
    body = body.replace('}}', Markup('</span>'))
    body = body.replace('^', Markup('<br><span class="highlight"><br />'))
    body = body.replace('*', Markup('</span><br>'))
    checks = page.checks()
    html = render_template("results.html", headings=headings,
                                links=links, body=body, outline=outline,
                                links_list=links_list, checks=checks)
    return html


# @app.route("/post/new", methods=["POST"])
# @login_required
# def create_post():
#     form = forms.NewPostForm(request.form)
#     if not form.validate():
#         flash("Error, all fields are required")
#         return render_template("new_post.html")

#     post = Post(title=form.title.data, body=form.body.data)
#     current_user.posts.append(post) 
    
#     model.session.commit()
#     model.session.refresh(post)

#     return redirect(url_for("view_post", id=post.id))

# @app.route("/login")
# def login():
#     return render_template("login.html")

# @app.route("/login", methods=["POST"])
# def authenticate():
#     form = forms.LoginForm(request.form)
#     if not form.validate():
#         flash("Incorrect username or password") 
#         return render_template("login.html")

#     email = form.email.data
#     password = form.password.data

#     user = User.query.filter_by(email=email).first()

#     if not user or not user.authenticate(password):
#         flash("Incorrect username or password") 
#         return render_template("login.html")

#     login_user(user)
#     return redirect(request.args.get("next", url_for("index")))


if __name__ == "__main__":
    app.run(debug=True)
