import pymysql
import collections
import simplejson as json
import uuid
import decimal

class databases:

    def __init__(self):
        self.arr=[]

    def getMetricValues(self, UUID, config): 
        conn = pymysql.connect(host=config.get("host"), port=config.get("port"), user=config.get("user"), passwd=config.get("passwd"), db=config.get("db"))
        cur = conn.cursor()
        select_tuple = (UUID)
        cur.execute("SELECT pm.MetricId,pm.ProjectGUID,mt.Metric,ct.CategoryName,pm.BeforeDevOpsHrs, pm.BeforeDevOpsCost, pm.AfterDevOpsHrs, pm.AfterDevOpsCost, pm.ReadOnly FROM ProjectMetricDetails pm JOIN Metrics mt ON pm.MetricId = mt.MetricId JOIN Categories ct ON mt.CategoryCd = ct.CategoryCd WHERE pm.ProjectGUID = %s", select_tuple)
        data = cur.fetchall()
        cur.close()
        conn.close()
        #Converting data into json
        metrics_list = []
        for row in data :
            d = collections.OrderedDict()
            d['Metricid']  = row[0]
            d['ProjectGUID']   = row[1]
            d['Metric']  = row[2]
            d['CategoryName']   = row[3]
            d['BeforeDevOpsHrs']  = row[4]
            d['BeforeDevOpsCost']   = row[5]
            d['AfterDevOpsHrs']  = row[6]
            d['AfterDevOpsCost']   = row[7]
            d['ReadOnly'] = row[8]
            metrics_list.append(d)
        return json.dumps(metrics_list, use_decimal=True)

    def insertProjectDetails(self,projectname, clientname, industrygroup, worklocation, config):
        conn = pymysql.connect(host=config.get("host"), port=config.get("port"), user=config.get("user"), passwd=config.get("passwd"), db=config.get("db"))
        cur = conn.cursor()
        myuuid = uuid.uuid1()
        insertQuery="INSERT INTO Projects (`UserId`, `ProjectGUID`, `ProjectName`, `ClientName`, `IndustryGroup`,`WorkLocaation`) VALUES (%s,%s,%s,%s,%s,%s)"
        insert_tuple = (1,str(myuuid),projectname, clientname, industrygroup, worklocation)
        cur.execute(insertQuery, insert_tuple)
        conn.commit()
        self.callDefaultInsertProjectMetricValues(myuuid, config)
        return str(myuuid)

    def callDefaultInsertProjectMetricValues(self,uuid, config):
        conn = pymysql.connect(host=config.get("host"), port=config.get("port"), user=config.get("user"), passwd=config.get("passwd"), db=config.get("db"))
        cur = conn.cursor()
        args=[str(uuid)]
        cur.callproc('InsertDefaultProjectMetricDetails',args)
        conn.commit()
    
    def updateMetricValues(self,metricdata, UUID, config):
        conn = pymysql.connect(host=config.get("host"), port=config.get("port"), user=config.get("user"), passwd=config.get("passwd"), db=config.get("db"))
        cur = conn.cursor()
        for data in metricdata:
            updatequery = "UPDATE ProjectMetricDetails SET BeforeDevOpsHrs = %s, BeforeDevOpsCost = %s, AfterDevOpsHrs = %s, AfterDevOpsCost = %s, ReadOnly = %s WHERE ProjectGUID = %s AND MetricId = %s"
            args = (data.get('BeforeDevOpsHrs'), data.get('BeforeDevOpsCost'), data.get('AfterDevOpsHrs'), data.get('AfterDevOpsCost'), data.get('ReadOnly'), UUID, data.get('Metricid'))
            cur.execute(updatequery, args)
        conn.commit()
        self.calculateFinalMetrics(UUID, config)

    def calculateFinalMetrics(self, UUID, config):
        conn = pymysql.connect(host=config.get("host"), port=config.get("port"), user=config.get("user"), passwd=config.get("passwd"), db=config.get("db"))
        cur = conn.cursor()
        args=[UUID]
        cur.callproc('CalculateFinalMetrics', args)
        conn.commit()
    
    def getCalculatedProjects(self, config): 
        conn = pymysql.connect(host=config.get("host"), port=config.get("port"), user=config.get("user"), passwd=config.get("passwd"), db=config.get("db"))
        cur = conn.cursor()
        cur.execute("Select pr.ProjectGUID, pr.ProjectName, pr.ClientName, pr.IndustryGroup, pr.WorkLocaation, met.TotalHoursSaved, met.TotalCostSaved, met.TotalResourcesSaved from ProjectCalculations met JOIN Projects pr ON pr.ProjectGUID = met.ProjectGUID")
        data = cur.fetchall()
        cur.close()
        conn.close()
        #Converting data into json
        metrics_list = []
        for row in data :
            d = collections.OrderedDict()
            d['ProjectGUID']  = row[0]
            d['ProjectName']   = row[1]
            d['ClientName']  = row[2]
            d['IndustryGroup']   = row[3]
            d['WorkLocation']  = row[4]
            d['TotalHoursSaved']   = row[5]
            d['TotalCostSaved']  = row[6]
            d['TotalResourcesSaved']   = row[7]
            metrics_list.append(d)
        return json.dumps(metrics_list, use_decimal=True)

    def deleteProject(self, UUID, config):
        conn = pymysql.connect(host=config.get("host"), port=config.get("port"), user=config.get("user"), passwd=config.get("passwd"), db=config.get("db"))
        cur = conn.cursor()
        cur.execute("Delete from ProjectCalculations where ProjectGUID = %s", UUID)
        cur.execute("Delete from ProjectMetricDetails where ProjectGUID = %s", UUID)
        cur.execute("Delete from Projects where ProjectGUID = %s", UUID)
        conn.commit()
        return "Success"
        




       



  


