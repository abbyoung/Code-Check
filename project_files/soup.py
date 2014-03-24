from bs4 import BeautifulSoup
soup = BeautifulSoup(open("alice.html"), "lxml")

print(soup.prettify())