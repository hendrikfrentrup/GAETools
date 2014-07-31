import cgi
import datetime
import urllib
import webapp2
import jinja2
import os

import logging

from google.appengine.ext import ndb
from google.appengine.api import users

import re


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



def get_user(username):
    # query database and return user if exisiting
    users_query = User.query(User.username == username)
    user = users_query.fetch(1)
    if user:
        logging.info('User found in db')
        return user[0]










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
        self.render('main.html', message='Hi again!')

class LogoutPage(Handler):
    def get(self):
        self.response.delete_cookie('auth')
        self.redirect('/')
        
        
        
        
class LoginPage(Handler):
    def get(self):
        auth=self.request.cookies.get('auth')
        if auth:
            username=auth.split("|")[0]
            password=auth.split("|")[1]
            user=get_user(username)
            if user:
                # check if password of User is correct
                if user.password == password:
                    self.redirect('/main')
                    
        self.render('login.html', username = "Usernie" )
        

    def post(self):

        username = self.request.get('username')
        password = self.request.get('password')
        user = get_user(username)
        
        if user:

            # check if password of User is correct
            if user.password == password:

                # check if user wants to be remembered
                if self.request.get('remember'):
                    self.response.headers.add_header( 'Set-Cookie', \
                    str('auth={0:s}|{1:s}'.format(user.username, user.password)) )
                    logging.info('cookie set!')
                    self.redirect('/main')
                else:
                    self.redirect('/main')
            else:
                self.render('login.html', username = user.username, password="", pw_error= "Wrong password!")
        else:
            self.render('login.html', user_error= "User unknown!", password="")






class SignupPage(Handler):

    def get(self):         
        self.render('signup.html', name="Enter your full name",
                                   email="Enter a valid email",
                                   username="Enter your username",
                                   password="Password" )
               
               
               
    def post(self):

        fullname = self.request.get('name')
        email = self.request.get('email')
        username = self.request.get('username')
        password = self.request.get('password')
        repeat = self.request.get('repeat')
        
        # check if username is alphanumeric ('[^\w-]+$' or '[\W-]+$')
        valid_username = re.match('^[\w-]+$', username) is not None
        valid_password = re.match('^[\w-]+$', password) is not None
        
        logging.info('Username Valid: {0}'.format(valid_username))
        logging.info('Password Valid: {0}'.format(valid_password))
        
        # check if password is correctly repeated
        if password==repeat and valid_username and valid_password:
        
            # check if username exists already  # check if User with username exists
            users_query = User.query(User.username == username)
            user = users_query.fetch(1)
            if user:
                logging.info('User exists')
                self.write("Username is already in use, sorry!")
            else:    
                # check if email exists already
                users_query = User.query(User.email == email)
                user = users_query.fetch(1)
                if user:
                    logging.info('Email exists')
                    self.write("Email is already in use, sorry!")
                else:                         
                    new_user = User()
                    new_user.fullname = fullname
                    new_user.email = email
                    new_user.username = username
                    new_user.password = password
                    new_user.put()

                    template_values = {
                        'name': fullname,
                        'email': email,
                    }

                    template = JINJA_ENVIRONMENT.get_template('signedup.html')
                    self.response.write(template.render(template_values))

        else:
            errors=[]
            if not valid_username:
                errors.append("Please use a normal username!")
            if not valid_password:
                errors.append("Please use a normal password!")
            if not password==repeat:
                errors.append('Passwords need to be identical!')

            self.render('signup.html', name=self.request.get('name'),
                                   email=self.request.get('email'),
                                   username=self.request.get('username'),
                                   password="",
                                   errors=errors)




app = webapp2.WSGIApplication([('/', FrontPage),
                               ('/main', MainPage),
                               ('/login', LoginPage),
                               ('/logout', LogoutPage),
                               ('/signup', SignupPage)],
                               debug=True)
