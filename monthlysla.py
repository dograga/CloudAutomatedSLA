#!/usr/bin/python
import pandas as pd
import numpy as np
import logit
import sys
from datetime import timedelta
import datetime
from calendar import monthrange


logfile="/root/sla/log/monthlyreport_check.log"
log=logit.logit(logfile)

def getMonthdays(year,month):
    days=monthrange(year, month)[1]
    return days

def getLastmonthyear():
    today = datetime.date.today()
    first = today.replace(day=1)
    lastMonthdate = first - datetime.timedelta(days=1)
    lastMonth=int(lastMonthdate.strftime("%m"))
    lastYear=int(lastMonthdate.strftime("%Y"))
    return lastMonth,lastYear

def executesql(sql):
    msg="Executing SQL :"+sql
    log.logadd(msg,"info")
    try:
        [[ Execute SQL ]]
    except Exception as e:
         msg="Failed to execute :"+sql
         return 0
         log.logadd(msg,"error")
         log.logadd(e.message,"error")


def insertcszone():
   sql=[[ select zones from cloud uptime table]]
   [[execute sql]]
   rows = cursor.fetchall()
   for row in rows:
      zone=row[0]
      sql="insert [[ Monthly SLA Table fields zone, SLA%, Month, Year  ]](zone,sla,month,year) values('"+row[0]+"',0,"+str(lastMonth)+","+str(lastYear)+")"
      [[ execute sql ]]

(lastMonth,lastYear)=getLastmonthyear()
sql="select cszone,durationmin from [[ Cloud incident tracker table]] where month(cast(downtimestart as date))="+str(lastMonth)+" and year(cast(downtimestart as date))="+str(lastYear)
print sql
cnxn=[[ get DB connection ]]
df = pd.read_sql_query(sql, cnxn)
print df
dfa=df.groupby(['cszone']).sum()
dfa.reset_index(inplace=True)
print dfa
days=getMonthdays(lastYear,lastMonth)
minMonth=days*24*60  ## total mins in month to caculate SLA
sqls=[]
sql="delete from [[monthly cloud sla table]] where month="+str(lastMonth)+" and year="+str(lastYear)     ## delete old entries for same year & month from table
sqls.append(sql)
insertcszone()
for row in dfa.values:
   sla=round((minMonth-float(row[1]))*100/minMonth,2)
   sql="update [[monthly cloud sla table]] set sla="+str(sla)+" where month="+str(lastMonth)+" and year="+str(lastYear)+" and cszone='"+row[0]+"'"
   sqls.append(sql)
for sql in sqls:
   print sql
   out=executesql(sql)
