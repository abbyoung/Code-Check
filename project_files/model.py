# -*- coding: UTF-8 -*-


from bs4 import BeautifulSoup, NavigableString, Comment
import bs4
from num2words import num2words
import requests
import re
import sys
import config
import bcrypt
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Text

from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref

from flask.ext.login import UserMixin

engine = create_engine(config.DB_URI, echo=False) 
session = scoped_session(sessionmaker(bind=engine,
                         autocommit = False,
                         autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

class Messages(Base):
    __tablename__ = "messages" 
    id = Column(Integer, primary_key=True)
    
    title = Column(String(64), nullable=False)
    message = Column(String(64), nullable=False)

    reports = relationship("Reports", uselist=True)

    # def set_password(self, password):
    #     self.salt = bcrypt.gensalt()
    #     password = password.encode("utf-8")
    #     self.password = bcrypt.hashpw(password, self.salt)

    # def authenticate(self, password):
    #     password = password.encode("utf-8")
    #     return bcrypt.hashpw(password, self.salt.encode("utf-8")) == self.password

class Reports(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(64), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    posted_at = Column(DateTime, nullable=True, default=None)
    message_id = Column(Integer, ForeignKey("messages.id"))

    user = relationship("User")


def create_tables():
    Base.metadata.create_all(engine)
    u = User(email="test@test.com")
    u.set_password("unicorn")
    session.add(u)
    p = Post(title="This is a test post", body="This is the body of a test post.")
    u.posts.append(p)
    session.commit()

class PageParser():
    def __init__(self, url):
        self.url = url
        self.r = requests.get(self.url)
        self.data = self.r.text
        self.soup = BeautifulSoup(self.data)
        self.body = self.soup.get_text()
        self.is_parsed = False
        self.char_replaced = False
        self.pagelinks = []
        self.pagestats = []
        self.pageoutline = []
        self.pagebody = []


    # Generate number of headings and links on page
    def headings(self):
        headings = []
        for tag in self.soup.findAll(re.compile('^h\d')):
            headings.append(tag.name)
        return headings

    def stats(self):
        stats = {}

        num_links = len(self.links())
        stats["Number of Links"] = num_links

        num_headings = len(self.headings())
        stats["Number of Headings"] = num_headings
        
        return stats

    # Generate page outline of all headings
    def outline(self):
        outline = {}
        for heading in self.soup.findAll(re.compile('^h\d')):
            #insert h at end of string
            outline[heading.text] = heading.name
        
        return outline

    # Add in table stats to body
    def tables(self):
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
        #clean html comments
        comments = self.soup.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]
        
        #clean script tags
        scripts = self.soup.findAll('script')
        [script.extract() for script in scripts]
        
        #clean meta tags
        meta = self.soup.findAll('meta')
        [met.extract() for met in meta]

        #clean style
        styles = self.soup.findAll('style')
        [style.extract() for style in styles]

    
    def landmarks(self):
       
        #print LINK for <a>
        for a in self.soup.findAll('a'):
            a.attrs['class'] = "link"
            a.insert(0, ' {{LINK}} ')
        
        #print GRAPHIC and alt text for img
        imgs = self.soup.findAll('img')
        for img in imgs:
            if img.has_attr('alt'):
                img_alt = img.attrs['alt']
                img.append(' {{GRAPHIC}}, ' + img_alt)
            else:
                break
        
        #print BULLET in front of <li>
        for li in self.soup.findAll('li'):
            li.insert(0, ' {{BULLET}} ')
        
        #print FORM in front of <form>
        for form in self.soup.findAll('form'):
            form.insert(0, ' {{FORM}} ')

        #print heading level
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
        #converts special characters. needs to be before num2words
        characters = {
                        '-': " dash ",
                        '>': " greater ",
                        '<': " less ",
                        ':': " colon ",
                        '%': " percent ",
                        '|': " vertical bar ",
                        u'©': " copyright ",
                        u'»': " right double angle bracket ",
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
        
        return body    

    # Create list of all links on page    
    def links(self):
        links = []
        
        for tag in self.soup.findAll(re.compile('^a')):
            links.append(tag)
        return links

    # Generate printed list of all links
    def links_list(self):
        links = self.links()
        links_list = []
        for i in range(len(links)):
            link = links[i].string
            if link != None:
                links_list.append(link)
        return links_list

    # WARNINGS/ERRORS CHECKS -- MAY MOVE TO REPORT CLASS
    def check_title(self):
        title = []
        for tag in self.soup.findAll(re.compile('title')):
            title.append(tag)
        if len(title) == 1:
            return "True"
        elif len(title) > 1:
            return "False - Overuse of Title Attribute"
        else:
            return "False - No Page Title"

    def img_alt(self):
        #check if alt tag present. if not, throw error
        imgs = self.soup.findAll('img')
        for img in imgs:
            if img.has_attr('alt'):
                return "True"
            else:
                return "False"
                #TODO: check for where in code missing alt tags are


    def headings_check(self):
        headings_check = {}
        headings = self.headings()
        
        #are there any headings?
        if len(headings) > 0:
        #is there an h1?
            if headings[0] == 'h1':
                headings_check['h1'] = 'True'
            else:
                headings_check['h1'] = 'False'
        else:
            headings_check['h1'] = 'False'
            headings_check['Headings Step Check'] = 'Pass - No Headings'
        #check for steps
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
                headings_check['Headings Step Check'] = "False"
            else:
                headings_check['Headings Step Check'] = "True"

        return headings_check
        

    def redundant_link(self):
        hrefs = []
        
        redundant_links = []
        for sibling in self.soup.findAll('a'):
            hrefs.append(sibling['href'])
        for i in range(len(hrefs) - 1):
            if hrefs[i] == hrefs[i+1]:
               redundant_links.append(hrefs[i+1])

        return redundant_links

    def empty_links(self):
        links_inner = {}
        empty_links = {'URLS': [], 'Total': 0}

        for link in self.soup.findAll('a'):
            links_inner[link] = link.text
            if link.text == '':
                empty_links['URLS'] += [link]
                empty_links['Total'] += 1

        return empty_links

    def layout_table(self):
        for tag in self.soup.findAll('table'):
            if self.soup.th:
                return "Tabular Data Okay"
            else:
                return "Check for Layout Tables"

    def language(self):
        
        if self.soup.html.has_attr('lang'):
            return (self.soup.html['lang'])
        else:
            return "False"

    def input(self):
        #check if <input>, <textarea> and <select> elemenets have labels
        if self.soup.findAll('input'):
            for sibling in self.soup.input.previous_siblings:
                sib = (repr(sibling))
                if re.match('^<label', sib):
                    return "True"
                else:
                    return "False"

    def text_area(self):    
        if self.soup.findAll('textarea'):
            for sibling in self.soup.input.previous_siblings:
                sib = (repr(sibling))
                if re.match('^<label', sib):
                    return "True"
                else:
                    return "False"

    def select(self):    
        if self.soup.findAll('select'):
            for sibling in self.soup.input.previous_siblings:
                sib = (repr(sibling))
                if re.match('^<label', sib):
                    return "True"
                else:
                    return "False"

    def noscript(self):
        if self.soup.findAll('noscript'):
            return 'True'
        else:
            return 'False'

    def header(self):
        if self.soup.findAll('header'):
            return 'True'
        else:
            return 'False'

        
    def checks(self):
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
        
        self.extract()
        self.char_replacement()
        self.replace_numbers()
        self.tables()
        self.landmarks()   
        self.is_parsed = True
    
    def get_links(self):
        if not self.char_replaced:
            self.char_replacement()

        if self.pagelinks == []:
            self.pagelinks = self.links_list()

        return self.pagelinks

    def get_stats(self):
        if self.pagestats == []:
            self.pagestats = self.stats()

        return self.pagestats

    def get_outline(self):
        if self.pageoutline == []:
            self.pageoutline = self.outline()

        return self.pageoutline

    def get_body(self):
        if not self.is_parsed:
            self.parse()

        if self.pagebody == []:
            self.pagebody = self.soup.get_text()

        return self.pagebody


   


if __name__ == "__main__":
    #create_tables()
    pass
