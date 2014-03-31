from flask import Flask, render_template, redirect, request, g, session, url_for, flash, Markup
from model import Report, Message, Report_Message, PageParser
from flask.ext.login import LoginManager, login_required, login_user, current_user
from flaskext.markdown import Markdown
import config
import forms
import model
import re
from num2words import num2words
import json

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
    
    #encode outline and lists as json objects
    store_outline = json.dumps(outline)
    store_links = json.dumps(links_list)
    #create report
    # report = model.create_report(url, body, store_outline, store_links)
    r = Report(url=url, text_output=body, links=store_links, outline=store_outline)
    #run checks
    checks = page.checks()
    page_report = {}

    #if error found, add to report_message database
    if checks['Header'] == 'header':
        message = model.add_message(report=r, key='Header', value='header', error='header', code_snippet=page.header())
        page_report['Header'] = message
    
    if checks['Title'] == 'titleoveruse':
        message = model.add_message(report=r, key='Title', value='titleoveruse', error='titleoveruse', code_snippet=None)
        page_report['Title'] = message

    if checks['Title'] == 'titlenone':
        message = model.add_message(report=r, key='Title', value='titlenone', error='titlenone', code_snippet=None)
        page_report['Title'] = message

    if checks['Redundant Links']:
        redundant_links = json.dumps(page.redundant_link())
        message = model.add_message(report=r, key='Redundant Links', value=redundant_links, error='redundantlinks', code_snippet=redundant_links)
        page_report['Redundant Links'] = [message, json.loads(redundant_links)]

    if checks['Empty Links']['Total'] > 0:
        empty_links = json.dumps(page.empty_links())
        message = model.add_message(report=r, key='Empty Links', value=empty_links, error='emptylink', code_snippet=empty_links)
        page_report['Empty Links'] = message

    if checks['Alt Tags'] == 'alttags':
        message = model.add_message(report=r, key='Alt Tags', value='alttags', error='alttags', code_snippet=None)
        page_report['Alt Tags'] = message

    if checks['Headings'] == 'missingh1':
        message = model.add_message(report=r, key='Headings', value='missingh1', error='missingh1', code_snippet=None)
        page_report['Headings'] = message

    if checks['Headings'] == 'noheadings':
        message = model.add_message(report=r, key='Headings', value='noheadings', error='noheadings', code_snippet=None)
        page_report['Headings'] = message

    if checks['Headings'] == 'headingsskip':
        message = model.add_message(report=r, key='Headings', value='headingsskip', error='headingsskip', code_snippet=None)
        page_report['Headings'] = message

    if checks['Tables'] == 'layouttables':
        message = model.add_message(report=r, key='Tables', value='layouttables', error='layouttables', code_snippet=None)
        page_report['Tables'] = message

    if checks['Language'] == 'language':
        message = model.add_message(report=r, key='Language', value='language', error='language', code_snippet=None)
        page_report['Language'] = message

    if checks['No Script'] == 'noscript':
        message = model.add_message(report=r, key='No Script', value='noscript', error='noscript', code_snippet=None)
        page_report['No Script'] = message

    if checks['Form - Input Label'] == 'inputlabel':
        message = model.add_message(report=r, key='Form - Input Label', value='inputlabel', error='inputlabel', code_snippet=None)
        page_report['Form - Input Label'] = message

    if checks['Form - Text Area Label'] == 'textarealabel':
        message = model.add_message(report=r, key='Form - Text Area Label', value='textarealabel', error='textarealabel', code_snippet=None)
        page_report['Form - Text Area Label'] = message 

    if checks['Form - Select Label'] == 'selectlabel':
        message = model.add_message(report=r, key='Form - Select Label', value='selectlabel', error='selectlabel', code_snippet=None)
        page_report['Form - Select Label'] = message

    


    html = render_template("results.html", headings=headings,
                                links=links, body=body, outline=outline,
                                links_list=links_list, page_report=page_report)
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
