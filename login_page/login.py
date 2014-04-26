import cgi
import datetime
import urllib
import webapp2
import jinja2
import os

from google.appengine.ext import ndb
from google.appengine.api import users



JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)




class User(ndb.Model):
    username = ndb.StringProperty()
    fullname = ndb.StringProperty()
    email = ndb.StringProperty()
    password = ndb.StringProperty()
    signupdate = ndb.DateTimeProperty(auto_now_add=True)
  
 
  
class FrontPage(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.out.write(template.render())            



class MainPage(webapp2.RequestHandler):
            
    def get(self):
        self.response.out.write("Hi again!")



class LoginPage(webapp2.RequestHandler):

    def get(self):         
        template = JINJA_ENVIRONMENT.get_template('templates/login.html')
        self.response.out.write(template.render())

    def post(self):
        users_query = User.query(User.username == self.request.get('username'))
        user = users_query.fetch(1)
        if user:
            if user[0].password == self.request.get('password'):
                self.redirect('/main')
            else:
                self.response.out.write("Wrong password!")
        else:
            self.response.out.write("User unknown!")




class SignupPage(webapp2.RequestHandler):
    def get(self):         
        template = JINJA_ENVIRONMENT.get_template('templates/signup.html')
        self.response.out.write(template.render())
               
    def post(self):
    
        if self.request.get('password')==self.request.get('repeat'):
            new_user = User()
            new_user.fullname = self.request.get('name')
            new_user.email = self.request.get('email')
            new_user.username = self.request.get('username')
            new_user.password = self.request.get('password')
            new_user.put()

            template_values = {
                'name': self.request.get('name'),
                'email': self.request.get('email'),
            }

            template = JINJA_ENVIRONMENT.get_template('templates/signedup.html')
            self.response.write(template.render(template_values))

        else:
            self.response.out.write("Password error!")


app = webapp2.WSGIApplication([('/', FrontPage),
                               ('/main', MainPage),
                               ('/login', LoginPage),
                               ('/signup', SignupPage)],
                              debug=True)
