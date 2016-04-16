import os
import webapp2
import jinja2

import logging

from google.appengine.ext import db

#template_dir = os.path.join(os.path.dirname(__file__), 'templates')
#jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
#                               autoescape=True)

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Question(db.Model):
    #author = db.StringProperty(required=True)
    question = db.TextProperty(required=True)
    answer1 = db.TextProperty(required=True)
    answer2 = db.TextProperty(required=True)
#   nAnswer1 = db.IntegerProperty()#(default=0)
#   nAnswer2 = db.IntegerProperty()#(default=0)
    created = db.DateTimeProperty(auto_now_add=True)

class MainPage(Handler):
    def render_front(self, question="", answer1="", answer2="", error=""):
        logging.error('db querying')
        questions = db.GqlQuery("SELECT * FROM Question "
                                "ORDER BY created DESC")
	# db.delete()
        self.render("front.html", question=question, answer1=answer1, answer2=answer2, error=error, questions=questions)

    def get(self):
        self.render_front()
    
    def post(self):
        #title = self.request.get("title")
        question = self.request.get("question")
        answer1 = self.request.get("answer1")
        answer2 = self.request.get("answer2")

        if question and answer1 and answer2:
            a = Question(question=question, answer1=answer1, answer2=answer2)
            a.put()
            #self.write("thanks!")
            self.redirect("/")
        else:
            error = "Pose a question AND give the possible answers?"
            self.render_front(question, answer1, answer2, error)

app = webapp2.WSGIApplication([('/', MainPage)], debug=True)


