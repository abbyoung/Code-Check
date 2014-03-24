# -*- coding: UTF-8 -*-


from bs4 import BeautifulSoup, NavigableString
import bs4
from num2words import num2words
import requests
import re
import sys

class PageParser():
    def __init__(self, url):
        self.url = url
        self.r = requests.get(self.url)
        self.data = self.r.text
        self.soup = BeautifulSoup(self.data)
        self.body = self.soup.get_text()
        
    
    # Create list of all links on page    
    def links(self):
        links = []
        for tag in self.soup.findAll(re.compile('^a')):
            links.append(tag)
        return links

    # Generate number of headings and links on page
    def stats(self):
        num_links = len(self.links())

        headings = []
        for tag in self.soup.findAll(re.compile('^h\d')):
            headings.append(tag)
        num_headings = len(headings)
        print "-"*10
        print "Page has %s headings and %s links." % (num_headings, num_links)
        print "-"*10

    # Generate page outline of all headings
    def outline(self):
        print "-"*10
        print "Outline"
        print "-"*10
        for heading in self.soup.findAll(re.compile('^h\d')):
            #insert h at end of string
            print heading.text, heading.name

    
    # Function to delete elements
    def extract_element(self, var):
        for item in var:
            item.extract()

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

    
    def landmarks(self, soup):

        #clean script tags
        scripts = self.soup.findAll('script')
        self.extract_element(scripts)
        
        #clean meta tags
        meta = self.soup.findAll('meta')
        self.extract_element(meta)
       
        #print LINK for <a>
        for a in self.soup.findAll('a'):
            a. attrs['class'] = "link"
            a.insert(0, 'LINK ')
        
        #print GRAPHIC and alt text for img
        imgs = self.soup.findAll('img')
        for img in imgs:
            if img.has_attr('alt'):
                img_alt = img.attrs['alt']
                img.append('GRAPHIC, ' + img_alt)
            else:
                break
        
        #print BULLET in front of <li>
        for li in self.soup.findAll('li'):
            li.insert(0, 'BULLET ')
        
        #print FORM in front of <form>
        for form in self.soup.findAll('form'):
            form.insert(0, 'FORM ')

        #print heading level
        for heading in self.soup.findAll(re.compile('^h\d')):
            
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



# Generate printed list of all links
    def links_list(self):
        links = self.links()
        print "-"*10
        print "Links"
        print "-"*10
        for i in range(len(links)):
            link = links[i].string
            print link


    def char_replacement(self, body):
        
        #body = self.soup.get_text()

        #body = var
        #converts special characters. needs to be before num2words
        characters = {
                        '-': " dash ",
                        '>': " greater ",
                        '<': " less ",
                        ':': "colon ",
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
        print body    



        # #this works:
        # for i in range(len(numbers)):
        #     body = re.sub(str(numbers[i]), num2words(numbers[i]), body)
            
        # # Replace '%20' with space
        # body = body.replace('%20', ' ')
       
        # #print body
    
    def main_body(self):
        self.landmarks(self.soup)
        self.char_replacement(self.body)
        self.replace_numbers()

    def parse(self):
        parsed = {
                    "summary": self.stats(),
                    "tables": self.tables(),
                    "outline": self.outline(),
                    "links": self.links_list(),
                    "main": self.main_body()
        }
        return parsed
       
        
# class Report():
#     def __init__(self, page):
#         self.page = PageParser.soup


#     def check_title(self):
#         pass





def main():
    # print "Enter URL to parse."
    # response = raw_input("> ")
    # script, url = sys.argv
    output = PageParser("http://modelviewculture.com")
    output.parse()


if __name__ == "__main__":
    main()


