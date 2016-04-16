import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)



class Entry(ndb.Model):
    """Models an individual Translation entry."""
    word = ndb.StringProperty()
    sentence = ndb.StringProperty(indexed=False)
    translation = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)



class MainPage(webapp2.RequestHandler):
    def get(self):
#        self.response.headers['Content-Type'] = 'text/plain'
#        self.response.write('funzt!')
        
        entry_query = Entry.query()
        entries = entry_query.fetch(10)
        template = JINJA_ENVIRONMENT.get_template('index.html')
        template_values = { 'entries' : entries }
        self.response.write(template.render(template_values))

class EntryPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('entry.html')
        self.response.write(template.render())

    def post(self):
        entry = Entry()
        entry.word = self.request.get('word')
        entry.sentence = self.request.get('sentence')
        entry.translation = self.request.get('translation')
        entry.put()
        
        word=self.request.get('word')
        self.response.write("<html>You've entered the word "+word+"<br> <a href='/'>Home</a> </html>")


application = webapp2.WSGIApplication([ ('/', MainPage),
                                        ('/enter', EntryPage),
                                        ('/edit', EditPage),
                                      ], debug=True)
