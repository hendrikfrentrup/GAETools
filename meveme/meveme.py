import cgi
import urllib
import webapp2
import jinja2
import os

import logging

from google.appengine.ext import ndb
#from google.appengine.api import users --> ease up some of the authentication issues!
from google.appengine.api import mail

from datetime import datetime
from datetime import timedelta
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


class Challenge(ndb.Model):
    creationdate = ndb.DateTimeProperty(auto_now_add=True)
    enddate = ndb.DateTimeProperty()
    definition = ndb.StringProperty()
    stake = ndb.FloatProperty()
    challenger = ndb.StringProperty()
    challenger_email = ndb.StringProperty()
    originator_ID = ndb.StringProperty()#ndb.IntegerProperty()
    #check = 
    
#    @classmethod
#    def get_recent_challenges(cls, ancestor_key):
#    return cls.query(ancestor=ancestor_key).order(-cls.creationdate)



def get_user(username):
    # query database and return user if exisiting
    # can be improved and sped up by making email the key and select by ID/Key instead of query
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
  








  
class LandingPage(Handler):
    def get(self):
        self.render('index.html', message='Welcome!')


class MainPage(Handler):

    def get(self):
        unique_id=self.request.cookies.get('unique_id')
        if unique_id:
            # TODO:
            # use unique keys to query challenge list
            
            logging.info("unique_id: {0}".format(unique_id))
            # query for own challenges          
            challenge_query = Challenge.query(Challenge.originator_ID == unique_id)
            challenges = challenge_query.fetch(10)
            # query for others challenging me
            challenge_query = Challenge.query(Challenge.challenger == unique_id)
            challenged = challenge_query.fetch(10)

            logging.info("Challenge List Length: {0}".format(len(challenges)))
            #if len(challenges)>0:
            #    pass#print challenged
            
            self.render('main.html', message="Here are your current challenges:", challenges=challenges, challenged=challenged)

        else:
            auth=self.request.cookies.get('auth')
            if auth:
                username=auth.split("|")[0]
                password=auth.split("|")[1]
                user=get_user(username)
                if user:
                    # check if password of User is correct
                    if user.password == password:
                        # TODO:
                        # use unique keys to query challenge list
                        self.response.headers.add_header( 'Set-Cookie', \
                                                           str('unique_id={0:s}'.format(user.username)) )
                        logging.info('ID cookie set upon successful login (username for now)!')
                        self.redirect('/main')
                    else:
                        self.redirect('login.html', username = user.username )
                else:
                    self.redirect('login.html', username = "Login with your username" )                
            else:
                self.redirect('login.html', username = "Login with your username" )





class CreatePage(Handler):
    def get(self):
        self.render('create.html', example='Go to the gym THREE times per week.',
                                   amount='10.00', duration='3', color='#000000')

    def post(self):
    
        definition = self.request.get('definition')
        challenger = self.request.get('challenger')
        challenger_email = self.request.get('challenger_email')
        stake = self.request.get('stake')
        duration = self.request.get('duration')
        unique_id = self.request.cookies.get('unique_id')
        if unique_id:
            if self.request.get('oath'):# == 'yes'
                new_challenge = Challenge() #parent=ndb.Key("Book", guestbook_name or "*notitle*")
                new_challenge.definition = definition
                new_challenge.challenger = challenger
                new_challenge.challenger_email = challenger_email
                # check for stake to be a number!
                new_challenge.stake = float(stake)
                new_challenge.originator_ID = unique_id #int(unique_id)
                new_challenge.enddate = datetime.now() + timedelta(weeks=int(duration))
                new_challenge.put()
                
                self.redirect('/created')
                
                if challenger_email:
                    to_addr = challenger_email
                    base_url = "http://meveme-prototype-v01.appspot.com/signup"
                    if not mail.is_email_valid(to_addr):
                        # Return an error message...
                        logging.infor("Signup confirmation not sent, email invalid!")

                    message = mail.EmailMessage()
                    message.sender = "ibetyouwill@meveme-prototype-v01.appspotmail.com" #user.email()
                    message.subject = "You've been challenged!"
                    message.to = to_addr
                    message.body = """
                        Hey, you've been challenged to {0}:
                        
                        {1}
                        
                        Check out your challenge at:
                        {2}
                    """.format(stake, definition, base_url)

                    message.send()
                
            else:
                self.render('create.html', example=definition, errors=['You need to show us you are serious!'],
                                           email=challenger, amount=stake, color='#FF0000')
        else:
            self.redirect('login.html', username = "Login with your username" )


class CreatedPage(Handler):
    def get(self):
        self.render('created.html')




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
                    
        self.render('login.html', username='')
        

    def post(self):

        username = self.request.get('username')
        password = self.request.get('password')
        user = get_user(username)
        
        if user:

            # check if password of User is correct
            if user.password == password:

                # check if user wants to be remembered
                if self.request.get('remember'):
                    # TODO:
                    # Look into authentication methods
                    self.response.headers.add_header( 'Set-Cookie', \
                    str('auth={0:s}|{1:s}'.format(user.username, user.password)) )
                    logging.info('Login cookie set (auth: username|pw for now!!! DANGER!!)!')
                    self.redirect('/main')
                else:
                    self.redirect('/main')
            else:
                self.render('login.html', username=username,
                                          pw_error= "Wrong password!")
        else:
            self.render('login.html', user_error= "User unknown!",
                                      username=username)



class LogoutPage(Handler):
    def get(self):
        self.response.delete_cookie('auth')
        self.response.delete_cookie('unique_id')
        self.redirect('/')
        




class SignupPage(Handler):

    def get(self):         
        self.render('signup.html')
               
               
               
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
                    
                    #########################################################
                    # put this in it's own function'
                    #########################################################
                    to_addr = email
                    base_url = "http://meveme-prototype-v01.appspot.com/login"
                    if not mail.is_email_valid(to_addr):
                        # Return an error message...
                        logging.infor("Signup confirmation not sent, email invalid!")

                    message = mail.EmailMessage()
                    message.sender ="welcome@meveme-prototype-v01.appspotmail.com" #user.email()
                    message.to = to_addr
                    message.subject = "Your account has been created!"
                    message.body = """
                        Welcome to Meveme!

                        Your account has been created, congratulations!
                        
                        Come on and login at:
                        %s
                    """ % base_url

                    message.send()


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



app = webapp2.WSGIApplication([('/', LandingPage),
                               ('/main', MainPage),
                               ('/create', CreatePage),
                               ('/created', CreatedPage),
                               ('/login', LoginPage),
                               ('/logout', LogoutPage),
                               ('/signup', SignupPage)],
                               debug=True)
