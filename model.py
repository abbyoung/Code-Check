# -*- coding: UTF-8 -*-


from bs4 import BeautifulSoup, NavigableString, Comment
import bs4
from num2words import num2words
import requests
import re
import sys
import config
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Text

from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
from flask import Markup
from flask.ext.login import UserMixin
import json

engine = create_engine(config.DB_URI, echo=False) 
db_session = scoped_session(sessionmaker(bind=engine,
                         autocommit = False,
                         autoflush = False))

Base = declarative_base()
Base.query = db_session.query_property()



# Create table of error messages
class Message(Base):
    __tablename__ = "messages" 
    
    id = Column(Integer, primary_key=True)
    title = Column(String(64), nullable=False)
    message = Column(Text, nullable=False)
    error = Column(Text, nullable=False)

# Create table of error messages per report
class Report_Message(Base):
    
    __tablename__ = "report_message"
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('reports.id'))
    message_id = Column(Integer, ForeignKey('messages.id'))
    code_snippet = Column(String(64))
    report = relationship("Report", backref=backref("messages", order_by=report_id))
    message = relationship("Message")

# Create table of reports
class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True)
    url = Column(String(64))
    text_output = Column(Text, nullable=False)
    outline = Column(Text, nullable=False)
    links = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    stats = Column(Text, nullable=False)


def create_tables():
    Base.metadata.create_all(engine)
    db_session.commit()


class PageParser():
    def __init__(self, url=None, html=None):
        # Accept either html or url for parsing
        if html:
            # print "THIS IS HTML"
            # print html
            self.soup = BeautifulSoup(html)
        
        elif url:
            self.url = url
            self.r = requests.get(self.url)

            self.data = self.r.text
            # print "THIS IS FROM URL"
            # print self.data
            self.soup = BeautifulSoup(self.data)
        
        else:
            print "ERROR! Invalid input."
            raise
        self.body = self.soup.get_text()
        self.is_parsed = False
        self.char_replaced = False
        self.pagelinks = []
        self.pagestats = []
        self.pageoutline = []
        self.pagebody = []
        self.num_replaced = False


    
    def headings(self):
        # Generate number of headings and links on page
        headings = []
        for tag in self.soup.findAll(re.compile('^h\d')):
            headings.append(tag.name)
        
        return headings


    def stats(self):
        # Count number of links and headings
        stats = {}

        num_links = len(self.links())
        stats["Number of Links"] = num_links

        num_headings = len(self.headings())
        stats["Number of Headings"] = num_headings
        
        return stats

    
    def outline(self):
        # Generate page outline of all headings
        outline = []
        for heading in self.soup.findAll(re.compile('^h\d')):
            #insert h at end of string
            outline_dict = {}
            outline_dict[heading.text] = heading.name
            outline.append(outline_dict)
        
        return outline

    
    def tables(self):
        # Add in table stats to body
        tables = self.soup.findAll('table')

        for i in range(len(tables)):
            my_table = tables[i]
            rows = my_table.findChildren('tr')
            row_count = 0
            column_count = 0
            for row in rows:
                row_count += 1
            for row in rows:
                columns = row.findChildren('td')
                column_count = len(columns)
                break
            my_table.insert(0, "Table with %s rows and %s columns. " % (row_count,column_count))

    def extract(self):
        # Clean html comments
        comments = self.soup.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]

        doctype = self.soup.findAll(text=lambda text:isinstance(text, bs4.Doctype))
        [doc.extract() for doc in doctype]
        
        # Clean script tags
        scripts = self.soup.findAll('script')
        [script.extract() for script in scripts]
        
        # Clean meta tags
        meta = self.soup.findAll('meta')
        [met.extract() for met in meta]

        # Clean style
        styles = self.soup.findAll('style')
        [style.extract() for style in styles]

    
    def landmarks(self):
       
        # Print LINK for <a>
        for a in self.soup.findAll('a'):
            a.attrs['class'] = "link"
            a.insert(0, ' {{LINK}} ')
        
        # Print GRAPHIC and alt text for img
        imgs = self.soup.findAll('img')
        for img in imgs:
            if img.has_attr('alt'):
                img_alt = img.attrs['alt']
                img.append(' {{GRAPHIC}}, ' + img_alt)
            else:
                break
        
        # Print BULLET in front of <li>
        for li in self.soup.findAll('li'):
            li.insert(0, ' {{BULLET}} ')
        
        # Print FORM in front of <form>
        for form in self.soup.findAll('form'):
            form.insert(0, ' {{FORM}} ')

        # Print heading level
        for heading in self.soup.findAll(re.compile('^h\d')):
            
            if heading.name == "h1":
                heading.insert(0, "^Heading Level One*")
            elif heading.name == "h2":
                heading.insert(0, "^Heading Level Two*")
            elif heading.name == "h3":
                heading.insert(0, "^Heading Level Three*")
            elif heading.name == "h4":
                heading.insert(0, "^Heading Level Four*")
            elif heading.name == "h5":
                heading.insert(0, "^Heading Level Five*")
            elif heading.name == "h6":
                heading.insert(0, "^Heading Level Six*")


    def char_replacement(self):
        
        body = self.soup.get_text()
        # Converts special characters. Needs to be before num2words.
        characters = {
                        '-': " dash ",
                        '>': " greater ",
                        '<': " less ",
                        ':': " colon ",
                        '%': " percent ",
                        '|': " vertical bar ",
                        u'©': " copyright ",
                        u'»': " right double angle bracket ",
                        u'›': " right angle bracket ",
                        u'〈': "left angle bracket",
                        u'«': " left double angle bracket ",
                        '~': " tilde ",
                        '/': " slash ",
                        '&': " and ",
                        u'®': " registered ",
                        u'™': " trademark ",
                        u'£': " british pounds ",
                        u'€': " euros ",
                        '@': " at ",                
                        '+': " plus ",
                        '[': " left bracket ",
                        ']': " right bracket ",
                        '{': " left brace ",
                        '}': " right brace ",
                        '$': " dollars ",
                        '*': " asterisk ",
                        '#': " hash ",
                        '(': " left paren ",
                        ')': " right paren ",
                        u'•': " bullet ",
                        '=': " equals ",
                        '"': " quote ",
                        '_': " underscore ",
                        '∞': " infinity symbol ",
                    }

        # Replace characters with word
        for key, value in characters.iteritems():
            find_key = self.soup.find_all(text=re.compile('\\'+key))
            for n in find_key:
                fixed_text = unicode(n).replace(key, value)
                n.replace_with(fixed_text)

        body = self.soup.get_text()

        self.char_replaced = True
        
        return body 
        

    def replace_numbers(self):
        # Pull out all digits in text, cast as integers
        numbers = [int(n) for t in self.soup(text=True) 
                    for n in re.findall('\d+', t)]
        # Sort in descending order
        numbers = sorted(numbers, reverse=True)

        for i in range(len(numbers)):
            find_number = self.soup.find_all(text=re.compile(str(numbers[i])))
            for n in find_number:
                fixed_text = unicode(n).replace(str(numbers[i]), num2words(numbers[i]))
                n.replace_with(fixed_text)

        body = self.soup.get_text()
        
        self.num_replaced = True
        return body    

       
    def links(self):
        # Create list of all links on page 
        links = []
        
        for tag in self.soup.findAll(re.compile('^a')):
            links.append(tag)

        return links

    
    def links_list(self):
        # Generate printed list of all links
        links = self.links()
        links_list = []
        for i in range(len(links)):
            link = links[i].string
            if link != None:
                links_list.append(link)
        return links_list

    def title(self):
        title = []
        for tag in self.soup.findAll(re.compile('title')):
            title.append(tag)
        return title[0]

    # Warnings/Errors Checks

    def check_title(self):
        # Does page have properly used <title>?
        title = []
        for tag in self.soup.findAll(re.compile('title')):
            title.append(tag)
        if len(title) == 1:
            return "True"
        elif len(title) > 1:
            print title
            return "titleoveruse"
        else:
            return "titlenone"

    def img_alt(self):
        # Check if alt tag present
        imgs = self.soup.findAll('img')
        for img in imgs:
            if img.has_attr('alt'):
                return "True"
            else:
                return "alttags"
                


    def headings_check(self):
        headings_check = {}
        headings = self.headings()
        
        # Are there any headings?
        if len(headings) > 0:
        # Is there an h1?
            if headings[0] == 'h1':
                headings_check['h1'] = 'True'
            else:
                headings_check['h1'] = 'missingh1'
        else:
            headings_check['h1'] = 'missingh1'
            headings_check['Headings Step Check'] = 'noheadings'
        # Check for steps
        for i in range(len(headings)):
            if headings[i] == 'h1':
                headings[i] = 1
            elif headings[i] == 'h2':
                headings[i] = 2
            elif headings[i] == 'h3':
                headings[i] = 3
            elif headings[i] == 'h4':
                headings[i] = 4
            elif headings[i] == 'h5':
                headings[i] = 5
            elif headings[i] == 'h6':
                headings[i] = 6

        for i in range(len(headings)-1):
            if abs(headings[i] - headings[i+1]) > 1:
                return "headingsskip"

        return headings_check
        

    def redundant_link(self):
        # Check for/gather redundant links
        hrefs = []
        
        redundant_links = []
        for sibling in self.soup.findAll('a'):
            if sibling.has_attr('href'):
                if sibling['href'] != '#':
                    hrefs.append(sibling['href'])
        for i in range(1, len(hrefs)):
            if hrefs[i] == hrefs[i-1]:
               redundant_links.append(hrefs[i])
               redundant_links.append(hrefs[i-1])

        return redundant_links

    def empty_links(self):
        # Check for/gather empty links
        links_inner = {}
        empty_links = {'URLS': [], 'Total': 0}

        for link in self.soup.findAll('a'):
            links_inner[link] = link.text
            if link.text == '':
                empty_links['URLS'] += [link]
                empty_links['Total'] += 1

        return empty_links

    def layout_table(self):
        # Are layout tables used?
        for tag in self.soup.findAll('table'):
            if self.soup.th:
                return "True"
            else:
                return "layouttables"

    def language(self):
        # Is a language declared?
        if self.soup.html.has_attr('lang'):
            return "True"
        else:
            return "language"

    def input(self):
        # Check if <input> has label
        if self.soup.findAll('input'):
            for sibling in self.soup.input.previous_siblings:
                sib = (repr(sibling))
                if re.match('^<label', sib):
                    return "True"
                else:
                    return "inputlabel"

    def text_area(self):  
        # Check if <textarea> has label  
        if self.soup.findAll('textarea'):
            for sibling in self.soup.input.previous_siblings:
                sib = (repr(sibling))
                if re.match('^<label', sib):
                    return "True"
                else:
                    return "textarealabel"

    def select(self):
        # Check if <select> has label    
        if self.soup.findAll('select'):
            for sibling in self.soup.input.previous_siblings:
                sib = (repr(sibling))
                if re.match('^<label', sib):
                    return "True"
                else:
                    return "selectlabel"

    def noscript(self):
        # Check for <noscript> tag
        if self.soup.findAll('noscript'):
            return 'noscript'
        else:
            return None

    def header(self):
        # Check for <header> tag
        if self.soup.findAll('header'):
            return 'header'

        
    def checks(self):
        # Add check results to checks dict
        checks = {}
        checks['Title'] = self.check_title()
        checks['Redundant Links'] = self.redundant_link()
        checks['Alt Tags'] = self.img_alt()
        checks['Headings'] = self.headings_check()
        checks['Tables'] = self.layout_table()
        checks['Empty Links'] = self.empty_links()
        checks['Language'] = self.language()
        checks['No Script'] = self.noscript()
        checks['Header'] = self.header()
        checks['Form - Input Label'] = self.input()
        checks['Form - Text Area Label'] = self.text_area()
        checks['Form - Select Label'] = self.select() 
        return checks

    def parse(self):
        # Parse page
        self.extract()
        self.char_replacement()
        self.replace_numbers()
        self.tables()
        self.landmarks()   
        self.is_parsed = True
    
    def get_links(self):
        # Get links list, as long as characers and numbers are replaced
        if not self.char_replaced:
            self.char_replacement()

        if not self.num_replaced:
            self.replace_numbers()

        if self.pagelinks == []:
            self.pagelinks = self.links_list()

        return self.pagelinks

    def get_stats(self):
        # Get page stats
        if self.pagestats == []:
            self.pagestats = self.stats()

        return self.pagestats

    def get_outline(self):
        # Get page outline
        if self.pageoutline == []:
            self.pageoutline = self.outline()

        return self.pageoutline

    def get_body(self):
        # Get body only if page is parsed
        if not self.is_parsed:
            self.parse()

        if self.pagebody == []:
            self.pagebody = self.soup.get_text()

        return self.pagebody

## End class delcarations

def add_message(report, key, value, error, code_snippet):
    # Add error messages for report to db
    message = db_session.query(Message).filter_by(error=error).first()
    message_id = message.id
    m = Report_Message(message_id=message_id, code_snippet=code_snippet)
    report.messages.append(m)
    db_session.add(m)
    db_session.commit()
    message = message.message
    
    return message


def results(page, url):
    results = {}
    url = url
    extract = page.extract()
    links_list = page.get_links()
    outline = page.get_outline()
    stats = page.get_stats()
    headings = stats['Number of Headings']
    headings = num2words(headings)
    links = stats['Number of Links']
    links = num2words(links)

    # Format body for web. Replace new lines with spaces, add markup for styling
    body = Markup(page.get_body())
    body = body.replace('\n', (' '))
    body = body.replace('{{', Markup('<span class="highlight">'))
    body = body.replace('}}', Markup('</span>'))
    body = body.replace('^', Markup('<br><span class="highlight"><br />'))
    body = body.replace('*', Markup('</span><br>'))
    
    # Encode outline and lists as json objects
    store_outline = json.dumps(outline)
    store_links = json.dumps(links_list)
    store_stats = json.dumps(stats)
    
    # Create and store report
    r = Report(url=url, text_output=body, links=store_links, outline=store_outline, stats=store_stats)
    
    # Run checks
    checks = page.checks()
    page_report = {}

    # If error found, add to report_message database
    if checks['Header'] == 'header':
        message = add_message(report=r, key='Header', value='header', error='header', code_snippet=None)
        page_report['Header Element Present'] = message
    
    if checks['Title'] == 'titleoveruse':
        message = add_message(report=r, key='Title', value='titleoveruse', error='titleoveruse', code_snippet=None)
        page_report['Title'] = message

    if checks['Title'] == 'titlenone':
        message = add_message(report=r, key='Title', value='titlenone', error='titlenone', code_snippet=None)
        page_report['Title'] = message

    if checks['Redundant Links']:
        redundant_links = json.dumps(page.redundant_link())
        message = add_message(report=r, key='Redundant Links', value=redundant_links, error='redundantlinks', code_snippet=redundant_links)
        page_report['Redundant Links'] = [message, json.loads(redundant_links)]

    if checks['Empty Links']['Total'] > 0:
        empty_links = json.dumps(page.empty_links())
        message = add_message(report=r, key='Empty Links', value=empty_links, error='emptylink', code_snippet=empty_links)
        page_report['Empty Links'] = message

    if checks['Alt Tags'] == 'alttags':
        message = add_message(report=r, key='Alt Tags', value='alttags', error='alttags', code_snippet=None)
        page_report['Missing Alternative Text'] = message

    if checks['Headings'] == 'missingh1':
        message = add_message(report=r, key='Headings', value='missingh1', error='missingh1', code_snippet=None)
        page_report['Headings'] = message

    if checks['Headings'] == 'noheadings':
        message = add_message(report=r, key='Headings', value='noheadings', error='noheadings', code_snippet=None)
        page_report['Headings'] = message

    if checks['Headings'] == 'headingsskip':
        message = add_message(report=r, key='Headings', value='headingsskip', error='headingsskip', code_snippet=None)
        page_report['Headings Steps'] = message

    if checks['Tables'] == 'layouttables':
        message = add_message(report=r, key='Tables', value='layouttables', error='layouttables', code_snippet=None)
        page_report['Layout Tables'] = message

    if checks['Language'] == 'language':
        message = add_message(report=r, key='Language', value='language', error='language', code_snippet=None)
        page_report['Language'] = message

    if checks['No Script'] == 'noscript':
        message = add_message(report=r, key='No Script', value='noscript', error='noscript', code_snippet=None)
        page_report['noscript Element Present'] = message

    if checks['Form - Input Label'] == 'inputlabel':
        message = add_message(report=r, key='Form - Input Label', value='inputlabel', error='inputlabel', code_snippet=None)
        page_report['Missing Input Label'] = message

    if checks['Form - Text Area Label'] == 'textarealabel':
        message = add_message(report=r, key='Form - Text Area Label', value='textarealabel', error='textarealabel', code_snippet=None)
        page_report['Missing Text Area Label'] = message 

    if checks['Form - Select Label'] == 'selectlabel':
        message = add_message(report=r, key='Form - Select Label', value='selectlabel', error='selectlabel', code_snippet=None)
        page_report['Missing Select Label'] = message

    report_id = r.id
    # Add report details to dict
    results['headings'] = headings
    results['links'] = links
    results['body'] = body
    results['outline'] = outline
    results['links_list'] = links_list
    results['page_report'] = page_report
    results['report_id'] = report_id

    return results
    



if __name__ == "__main__":
    # create_tables()
    pass
    
