from flask import Flask, render_template, redirect, request, g, url_for, flash, Markup, make_response
from model import Report, Message, Report_Message, PageParser
from flaskext.markdown import Markdown
import config
import model
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

model.db.init_app(app)

# Adding markdown capability to the app
Markdown(app)

@app.route("/")
def index():
    return render_template("index.html", host_url=request.host_url)

@app.route("/bookmarklet")
def bookmarklet():
    text = render_template("app.js", host_url=request.host_url)
    response = make_response(text)
    response.mimetype = 'text/javascript'
    return response

@app.route("/", methods=["POST"])
def get_url():
    url = request.form.get("url")
    # Check url for protocol
    if not re.match('^(http|https)://', url):
        url = 'http://' + url
     
    return redirect(url_for("results", url=url))

@app.route("/api", methods=["POST"])
@crossdomain(origin="*")
def get_bookmarklet():
    # Get page data
    html = request.form.get('html')
    url = request.form.get('url')
    # Parse page
    page = model.PageParser(html=html, url=url)
    # Run checks, store in database
    results = model.results(page, url)
    # Return report_id for pulling report
    resp = make_response(json.dumps(results['report_id']))
    
    return resp

@app.route("/report/<data>", methods=["GET"])
@crossdomain(origin="*")
def bookmarklet_results(data):
    # Get report_id
    report_id = data
    # Get report from db
    report = model.db.session.query(model.Report).filter_by(id=report_id).first()
    url = report.url
    # Format url for display
    url = re.sub('^(http|https)://', '', url)
    # Load data for display
    stats = json.loads(report.stats)
    headings = num2words(stats['Number of Headings'])
    links = num2words(stats['Number of Links'])
    body = Markup(report.text_output)
    outline = json.loads(report.outline)
    links_list = json.loads(report.links)
    # Get report errors messages from db
    page_report = model.db.session.query(model.Report_Message).filter_by(report_id=report_id).all()
    
    # Display number of issues in Issues tab
    if len(page_report) > 0:
        issues = len(page_report)
    else:
        issues = None
        page_report = ["No issues."]
    
    # Assemble error messages for display
    messages = {}

    for i in range(len(page_report)):

        msg_title = page_report[i].message.title
        msg = page_report[i].message.message
        
        if page_report[i].code_snippet:
            code_snippet = json.loads(page_report[i].code_snippet)
            messages[msg_title] = [msg, code_snippet]
        else:
            messages[msg_title] = msg

    
    
    html = render_template("bk_results.html", headings=headings, links=links, body=body, 
                    outline=outline, links_list=links_list, messages=messages, url=url, issues=issues)
    return html


@app.route("/results", methods=["GET"])
def results():
    # Get url to process
    url = request.args.get("url")
    # Ir url can be reached, parse
    # If url can't be reached, return error
    try:
        page = model.PageParser(url=url)
    except Exception, e:
        print 'nope!'
        flash('Couldn\'t get page. Please try again!')
        return redirect(url_for("index"))
    
    # Run checks and store in db
    results = model.results(page, url)
    # Format url for display
    url = re.sub('^(http|https)://', '', url)
    # Display number of issues in Issues tab
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
