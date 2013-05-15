import cherrypy
import datetime
import simplejson
from mako.template import Template
from mako.lookup import TemplateLookup

class db:
  def load(filename):
    data = simplejson.load(open("data/"+filename))
    return data["records"]

  def add(filename, record):
    data = simplejson.load(open("data/"+filename))
    index = data["index"]
    data["records"][index + 1] = record
    simplejson.dump(data, open("data/"+filename, "w"))

  def edit(filename, index, record):
    data = simplejson.load(open("data/"+filename))
    data["records"][index] = record
    simplejson.dump(data, open("data/"+filename, "w"))

  def getLocations():
    return load("locations")

  def getParameters():
    return load("parameters")

  def getRecords(location):
    return load(location)

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

    # parameter form submit page
    @cherrypy.expose
    def input(self):
      mylookup = TemplateLookup(directories=['html'])
      mytemplate = mylookup.get_template('input.html')
      return mytemplate.render()

    # graph view page
    @cherrypy.expose
    def view(self):
      mylookup = TemplateLookup(directories=['html'])
      mytemplate = mylookup.get_template('view.html')
      return mytemplate.render(lat="-33.922308", lng="18.417655", title="The Title")
    
    @cherrypy.expose
    def mako(self):
      mylookup = TemplateLookup(directories=['html'])
      mytemplate = mylookup.get_template('shedinja.html')
      d = dict(first="foo", second="bar", third="baz", param1="A", param2="B", param3="C", param4="D")
      #return mytemplate.render(first="foo", second="bar", third="baz")
      l = [1,2,3,4,5,1,2,3,4,5]
      p1 = str(l)
      p2 = str(l[::-1])
      p5 = p4 = p3 = p1
      return mytemplate.render(first="foo", second="bar", third="baz", param1="A", param2="B", param3="C", param4="D", param5="Q", paramdata1=p1, paramdata2=p2, paramdata3=p3, paramdata4=p4, paramdata5=p5)

    @cherrypy.expose
    def homeHandler(self, *args, **kwargs):
      print kwargs

      s = ""

      for k in kwargs.keys():
        if kwargs[k]:
          s = s + "%s : %s\n" % (k, kwargs[k])
      return s

cherrypy.quickstart(squiver(), config="cherrypy.conf")

