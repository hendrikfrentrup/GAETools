import os
import webapp2
import jinja2

import logging

from google.appengine.ext import db



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



class Polls(db.Model):
    #author = db.StringProperty(required=True)
    #poll_id = db.IntegerProperty() #autoincrement
    question = db.TextProperty(required=True)
    answers = db.StringListProperty(required=True)
    nAnswer = db.ListProperty(int) #default=0)
    nCount = db.IntegerProperty(default=0)
    created = db.DateTimeProperty(auto_now_add=True)

#myQuestion = "What\'s your favourite colour?"
#myAnswers = [('opt1','Red'),
#             ('opt2','Green'),
#             ('opt3','Blue'),
#             ('opt4','Yellow'),
#             ('opt5','Pink'),
#             ('opt6','Black')]
#myAnswerCount = [0,0,0,0,0,0]



indexMap   = {'opt1':0, 
              'opt2':1, 
              'opt3':2,
              'opt4':3,
              'opt5':4,
              'opt6':5}


results_preamble="<dl class='graph'>"
results_bar_title="<dt class='bar-title'>" # ... {{a[1]}}</dt>
results_bar="<dd class='bar-container'><div style='width:"
results_bar_end="%; background-color:#111111; color:#000000'>&nbsp;</div><strong>" # ... {{votes[i]}} %</strong></dd>
results_end="</dl> <p>Total Votes:"# {{total_votes}}</p> <p><a href='localhost:8080'>Home</a></p>"
results_links="<a href='http://localhost:8080'>Home</a> | <a href='http://localhost:8080'>Back to poll</a>"

#class TakePoll
#class ViewResults
#class AddPoll


class MainPage(Handler):
    
    def get_poll(self):
        thisPoll = db.GqlQuery("SELECT * FROM Polls "
                               "ORDER BY created DESC")
        logging.error('db query in get_poll!')
        
        if not thisPoll.get():
            tempPoll = Polls(question = "What\'s your favourite colour?", \
                             answers = ['Red','Green','Blue','Yellow','Pink','Black'],
                             nAnswer = [0 for i in xrange(6)] )
            tempPoll.put()
            logging.error('Poll example added!')
        
        return thisPoll.get()
        
              
    def render_poll(self, error="", question="", answers=""):

    	myPoll = self.get_poll()
    	
    	outStr='render poll with question={0}'.format(myPoll.question)
    	logging.error(outStr)

        self.render("poll.html", error=error, question=myPoll.question, answers=myPoll.answers)


    def get(self):
        # Upon first load, poll is not rendered (NoneType error, no entry in the database)

        # Get popular polls (question, answers and nAnswersTotal) from db
        # then render list with links to poll and results
        self.render_poll()


#    def render_results(self, answers=""):
#        votes=[0.,0.,0.,0.,0.,0.]
#        total_votes=0
#        self.render("results.html", answers=myAnswers, votes=votes, total_votes=total_votes)

#    def increment_votes(key, question):
#	obj = db.get(key)
#	obj.votes += 1


    def post(self):
        # self.write("<html><b>Thanks!</b><br></html>")
        # title = self.request.get("title")
        # question = self.request.get("question")
        # answer1 = self.request.get("answer1")
        # answer2 = self.request.get("answer2")
        

        results_html=results_preamble      
        
        poll_res = self.request.get("poll")
        
        if poll_res:
            #global myAnswerCount
            #global indexMap

            #self.write("thanks!")
            #self.write(self.request.get("poll"))
            #self.redirect("/")


        # UPDATE POLL IN DB (nAnswers, nAnswersTotal)
        # Pickle and unpickle answers and nAnswers
        # or find an array property in db.Model
        # then redirect to show results
            

            # get votes
            # poll_res -> index
            # new votes = [votes++]
            # -> total_votes=sum(new_votes)
            # update Poll
            # render results


            myPoll=self.get_poll()
            myAnswerCount=myPoll.nAnswer
            myAnswerCount[indexMap[poll_res]]+=1
            total_votes=sum(myAnswerCount)            
            myPoll.nAnswer=myAnswerCount
            myPoll.nCount=total_votes
            myPoll.put()
            
            

            votes=[]
            for v in myAnswerCount:
                votes.append(float(v)/total_votes*100)
            for i,a in enumerate(myPoll.answers):
                results_html = results_html+results_bar_title+a+"</dt>" + \
                               results_bar+str(int(votes[i]))+results_bar_end+str(votes[i])+"%</strong></dd>"
            
            results_html=results_html+results_end+str(total_votes)+"</p>"+results_links

            self.response.out.write(results_html)
            #self.render_results(answers=myAnswers, votes=votes, total_votes=total_votes)
        else:
            error = "Answer the god-damn question!!!"
            self.render_poll(error)

app = webapp2.WSGIApplication([('/', MainPage)], debug=True)


