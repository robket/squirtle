import cherrypy
import datetime
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
    data["records"][index + 1] = record
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
    def mako(self):
      mylookup = TemplateLookup(directories=['html'])
      mytemplate = mylookup.get_template('shedinja.html')
      d = dict(first="foo", second="bar", third="baz", param1="A", param2="B", param3="C", param4="D")
      #return mytemplate.render(first="foo", second="bar", third="baz")
      return mytemplate.render(first="foo", second="bar", third="baz", param1="A", param2="B", param3="C", param4="D")

    # Stuff you get when someone submits
    @cherrypy.expose
    def addRecordHandler(self, *args, **kwargs):
      print kwargs

      s = ""

      for k in kwargs.keys():
        if kwargs[k]:
          s = s + "%s : %s\n" % (k, kwargs[k])
      return s

cherrypy.quickstart(squiver(), config="cherrypy.conf")

