import cherrypy
import datetime
import time
import simplejson
from mako.template import Template
from mako.lookup import TemplateLookup
from datetime import datetime as dt

class db:
  def load(self, filename):
    data = simplejson.load(open("data/"+filename))
    return data["records"]

  def add(self, filename, record):
    data = simplejson.load(open("data/"+filename))
    index = data["index"]
    data["records"].append(record)
    data["index"] += 1
    simplejson.dump(data, open("data/"+filename, "w"))

  def edit(self, filename, index, record):
    data = simplejson.load(open("data/"+filename))
    data["records"][index] = record
    simplejson.dump(data, open("data/"+filename, "w"))

  def getLocations(self):
    return self.load("locations")

  def getParameters(self):
    return self.load("parameters")

  def getRecords(self, location):
    return self.load(location)

class squiver:
    mydb = db()
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
    @cherrypy.tools.json_out()
    def from_db_monthly(self, location, year=2013):
      params = self.mydb.getParameters()
      outdict = {}
      for param in params:
        outdict[param["name"]] = []
      for month in xrange(12):
        data = self.from_db_daily(location, year, month)
        for key in data.keys():
          if key not in outdict:
            continue
          outdict[key].append(sum(data[key]) / 31.0)
      return outdict

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def from_db_daily(self, location, year=2013, month=5):
      params = self.mydb.getParameters()
      data = self.mydb.getRecords(location)
      outdict = {}
      for param in params:
        outdict[param["name"]] = [0]*31
      for datum in data:
        for key in datum["values"].keys():
          if key not in outdict:
            continue
          ts = dt.fromtimestamp(datum["timestamp"])
          if ts.year == year and ts.month == month:
            outdict[key][ts.day] = datum["values"][key]
      return outdict
    
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
    def home(self):
      params = self.mydb.getLocations()
      mylookup = TemplateLookup(directories=['html'])
      mytemplate = mylookup.get_template('home.html')
      return mytemplate.render(parameters=params)

    # parameter form submit page
    @cherrypy.expose
    def input(self):
      mylookup = TemplateLookup(directories=['html'])
      mytemplate = mylookup.get_template('input.html')
      params = map(lambda x:x["name"], self.mydb.getParameters())
      return mytemplate.render(parameters=params)

    # graph view page
    @cherrypy.expose
    def view(self):
      mylookup = TemplateLookup(directories=['html'])
      mytemplate = mylookup.get_template('view.html')
      l = [1,2,3,4,5,1,2,3,4,5]
      p1 = str(l)
      p2 = str(l[::-1])
      p5 = p4 = p3 = p1
      return mytemplate.render(lat="0.263671", lng="36.818847", title="Nairobi Water Lines Booster Pump Station", param1="Taste", param2="pH", param3="Color", param4="Solids Amount", param5="Temperature", paramdata1=p1, paramdata2=p2, paramdata3=p3, paramdata4=p4, paramdata5=p5, param_lbl1="1", param_lbl2="2", param_lbl3="3", param_lbl4="4", param_lbl5="5")
    
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

    # Stuff you get when someone submits
    @cherrypy.expose
    def addRecordHandler(self, *args, **kwargs):
      print kwargs
      params = map(lambda x:x["name"], self.mydb.getParameters())
      record = {}
      record["timestamp"] = time.time()
      record["values"] = {}
      print kwargs
      for param in params:
        if param in kwargs:
          record["values"][param] = kwargs[param]
      print kwargs
      print kwargs["location"]
      self.mydb.add(kwargs["location"], record)
      raise cherrypy.HTTPRedirect("home/")
      return """<html><body><h1>Success</h1></body></html>"""

cherrypy.quickstart(squiver(), config="cherrypy.conf")

