import cgi
import datetime
import urllib
import webapp2
import jinja2
import os

from google.appengine.ext import ndb

from webapp2_extras import json

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Reading(ndb.Model):
    temperature = ndb.FloatProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
  
"""
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
"""           

class MainPage(webapp2.RequestHandler):
    def get(self):         
        self.response.out.write("<html>Hello world!</html>")

class SubmitReading(webapp2.RequestHandler):
    def get(self):         
        self.response.out.write("""
        <html><form action="/submit" method="post">
            <input type="text" name="temperature" value="Temperature Reading">
            <input type="password" name="pw" value="password">
            <input type="submit" value="Submit">
        </form></html>
        """)
               
    def post(self):
        
        if self.request.get('pw')=="hcpw":
            T=self.request.get('temperature')
            new_reading = Reading()
            new_reading.temperature = float(T) 
            new_reading.put()

            self.response.write("Thanks, you've submited the reading T= "+T)#"{0:3.2f}".format(T))

        else:
            self.response.out.write("Password error!")


class queryDB(webapp2.RequestHandler):
    def get(self):
        query = Reading.query()
        query= query.order(-Reading.date)
        last_readings = query.fetch(100)#iter()
        out=[]
        i=1
        for reading in last_readings[-1::-1]:
            out.append([i, reading.temperature])
            i+=1     
        self.response.content_type = 'application/json'
        self.response.write(json.encode(out))
        

class showChart(webapp2.RequestHandler):
    def get(self):         
        self.response.out.write("""
        <html><head>
        <script src="http://code.jquery.com/jquery-git2.js"></script>
        <script src="http://code.highcharts.com/highcharts.js"></script>
        <script src="http://code.highcharts.com/highcharts-more.js"></script>
        <script src="http://code.highcharts.com/modules/exporting.js"></script>
        <script type="text/javascript" src="scripts/chart.js"></script>
        </head><body>

        <div id="container" style="min-width: 400px; height: 400px; margin: 0 auto"></div></body>
        """)
        

app = webapp2.WSGIApplication([ ('/submit', SubmitReading),
                                ('/chart', showChart),
                                ('/query', queryDB),
                                ('/', MainPage) ]
                                , debug=True)
