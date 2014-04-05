from flask import Flask, render_template, redirect, request, g, session, url_for, flash, Markup, make_response
from model import Report, Message, Report_Message, PageParser
from flask.ext.login import LoginManager, login_required, login_user, current_user
from flaskext.markdown import Markdown
import config
import forms
import model
import forms
import re
from num2words import num2words
import json
import os
from crossdomain import crossdomain
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref


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
    # form = forms.LinkForm(request.form)
    # url = form.page_url.data
    url = request.form.get("url")
    if not re.match('^(http|https)://', url):
        url = 'http://' + url
    # if not form.validate():
    #     flash("Error")
    #     return render_template("index.html")
    # url = form.url.data
    #     # return render_template("index.html")
    # # url = request.form.get("url")
    # if not re.match('^(http|https)://', url):
    #     url = 'http://' + url
     
    return redirect(url_for("results", url=url))

@app.route("/api", methods=["POST"])
@crossdomain(origin="*")
def get_bookmarklet():
   
    html = request.form.get('html')
    url = request.form.get('url')
    
    page = model.PageParser(html=html, url=url)
    results = model.results(page, url)

    resp = make_response(json.dumps(results['report_id']))
    
    return resp

@app.route("/report/<data>", methods=["GET"])
def bookmarklet_results(data):
    report_id = data
    report = model.db_session.query(model.Report).filter_by(id=report_id).first()

    stats = json.loads(report.stats)
    headings = num2words(stats['Number of Headings'])
    links = num2words(stats['Number of Links'])

    body = Markup(report.text_output)
    outline = json.loads(report.outline)
    links_list = json.loads(report.links)
    page_report = model.db_session.query(model.Report_Message).filter_by(report_id=report_id).all()
    
    messages = {}

    for i in range(len(page_report)):
        print page_report[i]
        msg_title = page_report[i].message.title
        msg = page_report[i].message.message
        
        #page_report[0].message.message
        # messages[page_report[i].message.title] = [page_report[i].message.message]
        if page_report[i].code_snippet:
            code_snippet = json.loads(page_report[i].code_snippet)
            messages[msg_title] = [msg, code_snippet]
        else:
            messages[msg_title] = msg
    
    html = render_template("bk_results.html", headings=headings, links=links, body=body, 
                    outline=outline, links_list=links_list, messages=messages)
    return html


@app.route("/results", methods=["GET"])
def results():
  
    url = request.args.get("url")
    try:
        page = model.PageParser(url=url)
    except Exception, e:
        print 'nope!'
        flash('Couldn\'t get page. Please try again!')
        return redirect(url_for("index"))
    
    results = model.results(page, url)

    html = render_template("results.html", headings=results['headings'],
                                links=results['links'], body=results['body'], outline=results['outline'],
                                links_list=results['links_list'], page_report=results['page_report'])
    return html


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/help")
def help():
    return render_template("help.html")


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
    app.run(debug=True, host="0.0.0.0")
