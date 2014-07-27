import cgi
import datetime
import urllib
import webapp2
import jinja2
import os

from google.appengine.ext import ndb
from google.appengine.api import users

# makes templates/ default directory for template files
template_dir=os.path.join(os.path.dirname(__file__),"templates")

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)




class User(ndb.Model):
    username = ndb.StringProperty()
    fullname = ndb.StringProperty()
    email = ndb.StringProperty()
    password = ndb.StringProperty()
    signupdate = ndb.DateTimeProperty(auto_now_add=True)




class Handler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)    
    
    def render_str(self, template, **params):
        # 'template' is a string with the filename for template
        # 'params' are the parameters for the jinja2 template
        t = JINJA_ENVIRONMENT.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
  


  
class FrontPage(Handler):

    def get(self):
        self.render('index.html', message='Welcome!')




class MainPage(Handler):
            
    def get(self):
        self.response.out.write("Hi again!")



class LoginPage(Handler):

    def get(self):         
        self.render('login.html', username = "Usernie" )
        

    def post(self):
        # check if User with username exists
        users_query = User.query(User.username == self.request.get('username'))
        user = users_query.fetch(1)
        if user:
            # check if password of User is correct
            if user[0].password == self.request.get('password'):
                self.redirect('/main')
            else:
                self.render('login.html', username = user[0].username, pw_error= "Wrong password!")
        else:
            self.render('login.html', user_error= "User unknown!")




class SignupPage(Handler):

    def get(self):         
        self.render('signup.html', name="Enter your full name",
                                   email="Enter a valid email",
                                   username="Enter your username",
                                   password="Password" )
               
               
               
    def post(self):
        # check if password is correctly repeated
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

            template = JINJA_ENVIRONMENT.get_template('signedup.html')
            self.response.write(template.render(template_values))

        else:
            self.render('signup.html', name=self.request.get('name'),
                                   email=self.request.get('email'),
                                   username=self.request.get('username'),
                                   password="Password",
                                   pw_error='Passwords need to be identical!')




app = webapp2.WSGIApplication([('/', FrontPage),
                               ('/main', MainPage),
                               ('/login', LoginPage),
                               ('/signup', SignupPage)],
                               debug=True)
