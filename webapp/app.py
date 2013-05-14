import cherrypy
import datetime
import simplejson
from mako.template import Template
from mako.lookup import TemplateLookupo

load(filename):
  data = simplejson.load(open("data/"+filename))
  return data["records"]

add(filename, record):
  data = simplejson.load(open("data/"+filename))
  index = data["index"]
  data["records"][index + 1] = record
  simplejson.dump(data, open("data/"+filename, "w"))

class squiver:
    @cherrypy.expose
    def index(self):
        return "Welcome to squirtle system"

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def date(self, year, month, day):
      date = datetime.date(int(year), int(month), int(day))
      data = {"year": year, "month": month, "day": day, "weekday": date.weekday()}
      return data 
    
    @cherrypy.expose
    def update(self, name="unknown"):
      return "Hello " + name
    
    @cherrypy.expose
    def jsonupdate(self):
      cl = cherrypy.request.headers['Content-Length']
      rawbody = cherrypy.request.body.read(int(cl))
      body = simplejson.loads(rawbody)
      # do_something_with(body)
      return "\n".join(map(lambda x: x.upper(), body["names"]))
    
    @cherrypy.expose
    def mako(self):
      mylookup = TemplateLookup(directories=['html'])
      mytemplate = mylookup.get_template('shedinja.html')
      d = dict(first="foo", second="bar", third="baz", param1="A", param2="B", param3="C", param4="D")
      #return mytemplate.render(first="foo", second="bar", third="baz")
      return mytemplate.render(first="foo", second="bar", third="baz", param1="A", param2="B", param3="C", param4="D")

    @cherrypy.expose
    def homeHandler(self, *args, **kwargs):
      print kwargs

      s = ""

      for k in kwargs.keys():
        if kwargs[k]:
          s = s + "%s : %s\n" % (k, kwargs[k])
      return s

cherrypy.quickstart(squiver(), config="cherrypy.conf")

