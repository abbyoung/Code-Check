from flask.ext.wtf import Form
from flask_wtf.html5 import URLField
from wtforms import TextField
from wtforms.validators import Required, url

# class LinkForm(Form):
#     def __init__(self, require_tld=False, message="Error!"):
#         self.page_url = URLField(validators=[url()])