# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup, NavigableString
import bs4
from num2words import num2words
import requests
import re



def page_stat_summary(soup):
   
    links = []
    for tag in soup.findAll(re.compile('^a')):
        links.append(tag)
    num_links = len(links)

    headings = []
    for tag in soup.findAll(re.compile('^h\d')):
        headings.append(tag)
    num_headings = len(headings)
    print "-"*10
    print "Page has %s headings and %s links." % (num_headings, num_links)
    print "-"*10

def page_outline(soup):
    print "-"*10
    print "Outline"
    print "-"*10
    for heading in soup.findAll(re.compile('^h\d')):
        #insert h at end of string
        print heading.text, heading.name
        #print tag.string 
        # + " (%s)" % tag.name

def page_links(soup):
    links = []
    for tag in soup.findAll(re.compile('^a')):
        links.append(tag)
    print "-"*10
    print "Links"
    print "-"*10
    for i in range(len(links)):    
        print links[i].string
    return links

def extract_element(var):
    for item in var:
        item.extract()

def table_summary(soup):
    tables = soup.findAll('table')
    for i in range(len(tables)):
        my_table = tables[i]
        rows = my_table.findChildren('tr')
        row_count = 0
        column_count = 0
        for row in rows:
            row_count += 1
        for row[0] in rows:
            columns = row[0].findChildren('td')
            column_count = len(columns)
            break
        my_table.insert(0, " Table with %s rows and %s columns. " % (row_count, column_count))
        #print "Column Count: %s" % column_count

def main_body(soup):
    #clean script tags
    scripts = soup.findAll('script')
    extract_element(scripts)
    #clean meta tags
    meta = soup.findAll('meta')
    extract_element(meta)
    #print LINK for <a>
    for a in soup.findAll('a'):
        a. attrs['class'] = "link"
        a.insert(0, 'LINK ')
    #print GRAPHIC and alt text for img

    imgs = soup.findAll('img')
    for img in imgs:
        if img.has_attr('alt'):
            img_alt = img.attrs['alt']
            img.append('GRAPHIC, ' + img_alt)
        else:
            break
    #print BULLET in front of <li>
    for li in soup.findAll('li'):
        li.insert(0, 'BULLET ')
    #print FORM in front of <form>
    for form in soup.findAll('form'):
        form.insert(0, 'FORM ')

    #print heading level
    for heading in soup.findAll(re.compile('^h\d')):
        
        if heading.name == "h1":
            heading.insert(0, "Heading Level One\n")
        elif heading.name == "h2":
            heading.insert(0, "Heading Level Two\n")
        elif heading.name == "h3":
            heading.insert(0, "Heading Level Three\n")
        elif heading.name == "h4":
            heading.insert(0, "Heading Level Four\n")
        elif heading.name == "h5":
            heading.insert(0, "Heading Level Five\n")
        elif heading.name == "h6":
            heading.insert(0, "Heading Level Six\n")

    #get text from bs4 object
    body = soup.get_text()
        #converts special characters. needs to be before num2words
    characters = {
                    '-': "dash",
                    '>': "greater",
                    '<': "less",
                    ':': "colon",
                    '%': "percent",
                    '|': "vertical bar",
                    u'©': "copyright",
                    u'»': "right double angle bracket",
                    u'«': "left double angle bracket",
                    '~': "tilde",
                    '/': "slash",
                    '&': "and",
                    u'®': "registered",
                    u'™': "trademark",
                    u'£': "british pounds",
                    u'€': "euros",
                    '@': "at",                
                    '+': "plus",
                    '[': "left bracket",
                    ']': "right bracket",
                    '{': "left brace",
                    '}': "right brace",
                    '$': "dollars",
                    '*': "asterisk",
                    '#': "hash",
                    '(': "left paren",
                    ')': "right paren",
                    u'•': "bullet",
                    '=': "equals",
                    '"': "quote",
                    '_': "underscore",



                }

    for key, value in characters.iteritems():
        body = body.replace(key, value)

    #pull out all digist in text, cast as integers
    numbers = [int(n) for t in soup(text=True) 
                for n in re.findall('\d+', t)]
    # # #sort in descending order
    numbers = sorted(numbers, reverse=True)
 
    for i in range(len(numbers)):
        body = re.sub(str(numbers[i]), num2words(numbers[i]), body)
    #replace %20 with space
    body = body.replace('%20', ' ')
   

    print body
        

   


# def main():

r = requests.get("http://modelviewculture.com")
data = r.text
data.encode('utf-8')
soup = BeautifulSoup(data)
page_stat_summary(soup)
table_summary(soup)
page_outline(soup)
page_links(soup)

main_body(soup)


# if __name__ == "__main__":
#     main()
  