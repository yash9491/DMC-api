from flask import Flask, jsonify, request
from database import databases
from flask_cors import CORS, cross_origin
import simplejson as json
import os

app = Flask(__name__)
cors = CORS(app)
APP_ROOT = os.path.dirname(os.path.abspath(__file__)) 
APP_STATIC = os.path.join(APP_ROOT, 'config')
configuration_json_path = os.path.join(APP_STATIC, "configuration.json")
config = json.loads(open(configuration_json_path).read())
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/api/addProjectDetails", methods=["Post"])
def addProjectDetails():
    projectdata = json.loads(request.data)
    projectname = projectdata[0].get('projectname')
    clientname = projectdata[0].get('clientname')
    industrygroup = projectdata[0].get('industrygroup')
    worklocation = projectdata[0].get('worklocation')
    db = databases()
    return db.insertProjectDetails(projectname, clientname, industrygroup, worklocation, config)
    
@app.route("/api/getMetricValues", methods=["Get"])
def getMetricValues():
    projectUUID = request.args.get('projectUUID')
    db = databases()
    return db.getMetricValues(projectUUID, config)

@app.route("/api/updateMetricValues", methods=["Post"])
def updateMetricValues():
    metricdata = json.loads(request.data, use_decimal=True)
    projectUUID = request.args.get('projectUUID')
    db = databases()
    db.updateMetricValues(metricdata, projectUUID, config)
    return "Helloooo"

@app.route("/api/getCalculatedProjects", methods=["Get"])
def getCalculatedProjects():
    db = databases()
    return db.getCalculatedProjects(config)

@app.route("/api/deleteProject", methods=["Delete"])
def deleteProject():
    projectUUID = request.args.get('projectUUID')
    db = databases()
    return db.deleteProject(projectUUID, config)

if __name__ == "__main__":
    app.run(debug=True)