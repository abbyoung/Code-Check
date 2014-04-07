from flask import Flask, render_template, redirect, request, g, session, url_for, flash, Markup, make_response
from model import Report, Message, Report_Message, PageParser
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


# Adding markdown capability to the app
Markdown(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def get_url():
    url = request.form.get("url")
    if not re.match('^(http|https)://', url):
        url = 'http://' + url
     
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
    url = re.sub('^(http|https)://', '', url)
    if len(results['page_report']) > 0:
        issues = len(results['page_report'])
    else:
        issues = None
        results['page_report'] = ["No issues."]

    html = render_template("results.html", headings=results['headings'],
                                links=results['links'], body=results['body'], outline=results['outline'],
                                links_list=results['links_list'], page_report=results['page_report'], url=url, issues=issues)
    return html


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/help")
def help():
    return render_template("help.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
