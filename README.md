
# Code Check

## The Basics
Code Check is a web standards accessibility testing tool for screen reader compatibility. Utilizing [Section 508](http://http://www.section508.gov/), current web standards, and common screen reader behaviors, Code Check parses the html of any page using [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/), submitted either via url or captured with the Code Check bookmarklet. It performs a series of magic tricks on the code (described below), and stores+returns a unique report. Each report includes approximate screen reader output in text, page outline, page links, and accessibility issues.

![alt text](https://raw.githubusercontent.com/abbyoung/Project/master/static/img/codecheck_home.png "Code Check: Enter a URL.")

<br />
<br />

![alt text](https://raw.githubusercontent.com/abbyoung/Project/master/static/img/codecheck_report.png "Code Check: Report At-A-Glance")

## Installation
Code Check utilizes Python, Flask, Jinja2, Bootstrap, and SQLAlchemy. To install, git clone the repo, create a virtualenv, and `pip install -r requirements.txt`. You'll find the bookmarklet JavaScript in `/static/js/app.js`. Before running `views.py` to see it in action, set up the database.


## Database Know-How
After installing the requirements, you'll need to create your tables. Un-comment out `# create_tables()` at the end of `model.py`, run it, and boom! You now have a simple yet powerful database. Let's look at the tables:


* **Messages**

Messages stores all existing error messages and their codes that get displayed under Issues in the report. These errors are tested in `model.PageParser()`, and added to the database in `model.results()`.

* **Report Message**

For every error detected on a page, a report message is created with the `report_id`, `message_id`, and a `code_snippet` if relevant

* **Reports**

For every url or html submitted, a new report is created. The Reports table stores the `url`, `text_output`, `outline`, `links`, `stats`, and a `created_at` DateTime.


## Okay. So, how does it work?
### The Web App
If you're accessing Code Check from the web app index page, it's as easy as pasting in a URL and clicking "Submit". The app sends the url to the PageParser class, where it creates a new object, pulls the html, and makes "soup" using BeautifulSoup. From here, a number of magical things happen. We:


* Pull page stats including number of headings and links
* Pull a complete outline of the page using h tags (h1, h2...)
* Remove extraneous data including comments, `<script>`, `<meta>`, and `<style`> tags.
* Insert screen reader landmarks such as BULLET, LINK, GRAPHIC, etc.
* Replace special characters with text translations.
* Replace numbers with text translations.
* Compile links list.
* Perform code checks to generate warnings/errors.

Once a page has been parsed, it gets a little extra grooming in `model.results()`. Report data and report error messages are stored in the database, the body text is marked up with HTML, and it's sent to the `/results` route for viewing.

### The Bookmarklet
For easier on-the-go code checks, try the Code Check bookmarklet (found on the index page). Drag it to your bookmarks bar, and click when you've found a page to check. From here, the html is pulled from the document and parsed the same way. After storing the report data, the unique `report_id` gets sent to the `/report` view, where the relevant data is pulled and displayed.

## Why Code Check?
**“The power of the Web is in its universality.
Access by everyone regardless of disability is an essential aspect.”**

*&mdash;Tim Berners-Lee, W3C Director and inventor of the World Wide Web*

The web was born accessible, and it's our job to keep it that way. Code Check was created to make web accessibility easier to achieve, with an initial focus on screen readers.


