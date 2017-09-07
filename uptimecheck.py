#!/usr/bin/python
import time
import csapi
from datetime import datetime
from datetime import timedelta
import sys
from threading import Thread
from pyVim.connect import SmartConnect, Disconnect
from pytz import timezone
import logit


logfile=""  ## logfile location
log=logit.logit(logfile)

runfrequency=3    ## interval (min) for script execution to calculate failure duration

class cloudsla():
'''
   Class with modules to check uptime and update DB with status
   Any failure more than threshold (1/2/3) will be recorded in tracker table
   DB Tables required -- Cloud Status Table, Cloud Incident Tracker, Vcenter Hostname & Cloud Zone Map table
'''
    def __init__(self):
       #self.log=logit.logit(logfile)
       self.tzone=timezone('US/Pacific')
       d=datetime.now(self.tzone)
       self.updatedate=d.strftime("%a %b %d %H:%M:%S %Y %Z")
       failcount=2           ## Failure count threshold above which SLA will be calculated
       self.failedzones={}
       sql="select zone,lastupdated,failurecount,comment from cloud_status  where failurecount>"+str(failcount)  ##Find all cloud region where failure breached threshold
       cursor=self.executesql(sql)
       if cursor.rowcount:
           rows=cursor.fetchall()
           for row in rows:
               self.failedzones[row[0]]=[row[1],int(row[2]),str(row[3])]
               print self.failedzones

    def executesql(self,sql):
        #print "Executing SQL : {}".format(sql)
        msg="Executing SQL : "+sql
        log.logadd(msg,"info")
        try:
            [[ Execute SQL]]
        except Exception as e:
            msg="Failed to execute {}"+sql
            log.logadd(msg,"error")
            msg=e.message+str(e.args)
            log.logadd(msg,"error")

    def csstatus(self):
        api = csapi.CloudStack()
        log.logadd("Attempting to access Cloudstack API","info")
        request = {'available': 'true'}
        result = api.listZones(request)
        if result:
            state=True
        else:
            state=False
        return state

    def allsitesdown(self,comment):
        sql="update cloud_status set status='DOWN',failurecount=failurecount+1,lastupdated='"+str(self.updatedate)+"',comment='"+comment+"'"
        try:
            self.executesql(sql)
        except:
            print "Failed to execute sql"
        sys.exit()

    def updateslatracker(self,zone):
        downduration=self.failedzones[zone][1]*runfrequency
        downtimeend=datetime.strptime(self.failedzones[zone][0],"%a %b %d %H:%M:%S %Y %Z")
        downtimestart=downtimeend-timedelta(minutes=downduration)
        comment=self.failedzones[zone][2]
             ##changing to date format for db format
        downtimeend=downtimeend.strftime('%Y-%m-%d %H:%M:%S')
        downtimestart=downtimestart.strftime('%Y-%m-%d %H:%M:%S')
        msg="Downtime End: "+str(self.failedzones[zone][0])+" FailureCount: "+str(self.failedzones[zone][1])+"DowntimeStart="+downtimestart
        log.logadd(msg,"info")
        try:
           sql="insert into cloud_downtime_tracker(zone,downtimestart,downtimeend,comment,durationmin) values ('"+zone+"','"+str(downtimestart)+"','"+str(downtimeend)+"','"+comment+"',"+str(downduration)+")"
           print sql
           self.executesql(sql)
        except Exception as e:
           #print("Caught exception : " + str(e))
           msg="Caught exception : " + str(e)
           log.logadd(msg,"error")
           msg="Failed to append to tracker"
           log.logadd(msg,"error")


    def vcenterChecks(self,vc,zone):
        state=True
        comment=""
        user='' ## vcenter username
        passwd='' ## vcenter password
        port=443
        status="UP"
        try:
            si = SmartConnect(
               host=vc,
               user=user,
               pwd=passwd,
               port=port)
            msg="Attempting vcenter check "+vc
            log.logadd(msg,"info")
            if zone in self.failedzones:      ## Update downtime tracker if uptime followed by failure
                self.updateslatracker(zone)
            sql="update cloud_status set status='UP',failurecount=0,lastupdated='"+str(self.updatedate)+"',comment='"+comment+"' where zone='"+zone+"'"
        except Exception as e:
            msg="Caught exception : " + str(e)
            log.logadd(msg,"error")
            msg="Vcenter Failed "+vc
            log.logadd(msg,"error")
            comment=msg
            sql="update cloud_status set status='DOWN',failurecount=failurecount+1,lastupdated='"+str(self.updatedate)+"',comment='"+comment+"' where zone='"+zone+"'"
        self.executesql(sql)
        try:
            Disconnect(vc)
        except:
            log.logadd("Failed to disconnect","info")

def main():
    log.logadd("Service Uptime Check","info")
    startTime=datetime.now()
    s=cloudsla()

    [[ Add Code for cloud/API check above cloud orchestration(Cloudstack/OpenStack etc..) ]]

    comment=""
    ## Cloudstack Status.. use openstack or any other orchestration API check
    state=s.csstatus()
    if not state:
         comment="Cloudstack Down"
         s.allsitesdown(comment)    ## All sites down if cloudstack is centralized service

    #print "Cloudstack up lets check vcenter"
    sql= [[ select vcenter & zone from db ]]
    rows = cursor.fetchall()
    jobs=[]
    for row in rows:
        vc=row[0]
        zone=row[1]
        p = Thread(target=s.vcenterChecks, args=(vc,zone,))
        jobs.append(p)
        p.start()
    for j in jobs:
         j.join()
    diff=datetime.now() - startTime
    msg="Completed in "+str(diff)
    log.logadd(msg,"info")

if __name__=="__main__":
    main()
