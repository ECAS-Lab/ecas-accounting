#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# to run I executed:
# yes | cp accounting.py /tmp/ & sudo -u postgres python /tmp/accounting.py
# and make sure that accounting.py and /tmp/accounting.py identical 
#
# 
# Fabrizio Antonio
# Regina Kwee 
#
# Corona times, 2020 

import os, sys
import psycopg2

# Define database connection parameters
host=""
user="postgres"
password=""
dbname="accounting"
port=5432

# Define log files paths

task_4fields_path=""
task_5fields_path=""
workflow_7fields_path=""
workflow_9fields_path=""

con = psycopg2.connect( host=host, user=user, password=password, dbname=dbname, port=port )

# DROP TABLES
try:
  cur=con.cursor()
  cur.execute('DROP TABLE workflow;')
  cur.execute('DROP TABLE task;')
#  cur.close()
#  con.commit()
except Exception as error: print error

# CREATE TABLES
cur = con.cursor()
Q = 'CREATE TABLE workflow (timestamp TIMESTAMP, idworkflow integer, name varchar, username varchar, ip_address varchar, client_address varchar, "#tasks" smallint, "#success_tasks" smallint, duration decimal);'
cur.execute(Q)
cur.close()

cur = con.cursor()
Q = 'CREATE TABLE task (timestamp TIMESTAMP, idtask integer, idworkflow integer, operator varchar, "#cores" smallint, success_flag smallint, duration decimal);'
cur.execute(Q)
cur.close()
con.commit()
 


# LOAD DATA

# FIRST FILE
print "first file", task_4fields_path
f = open(task_4fields_path)
cur = con.cursor() 
cur.copy_from(f, 'task', columns=('idworkflow','operator', '"#cores"', 'success_flag'), sep="\t")
con.commit()
cur.close()

# SECOND FILE
print "second file", task_7fields_path
f = open(task_7fields_path)
cur = con.cursor()
cur.copy_from(f, 'task', columns=('timestamp', 'idtask', 'idworkflow', 'operator', '"#cores"', 'success_flag','duration'), sep="\t")
con.commit()
cur.close()

print "third file"
# THIRD FILE
f = open(workflow_5fields_path)
cur = con.cursor()
cur.copy_from(f, 'workflow', columns=('idworkflow','username','ip_address','"#tasks"','"#success_tasks"'), sep="\t")
con.commit()
cur.close()

# FOURTH FILE
print "fourth file ", workflow_9fields_path 
f = open(workflow_9fields_path)
cur = con.cursor()
cur.copy_from(f, 'workflow', columns=('timestamp', 'idworkflow', 'name,username', 'ip_address', 'client_address', '"#tasks"', '"#success_tasks"','duration'), sep="\t")
con.commit()
cur.close()


con.close()


# QUERIES:
# - ACTIVE USERS M1-M17 (BASELINE)
# - ACTIVE USERS M18-M26 (PERIOD 3)
# - TOTAL JOBS M1-M17 (BASELINE)
# - TOTAL JOBS M18-M26 (PERIOD 3)
# - CORES HOURS M1-M17 (BASELINE)
# - CORES HOURS M18-M26 (PERIOD 3)
QUERIES = ["SELECT COUNT(DISTINCT(username)) FROM workflow w,task t WHERE w.idworkflow=t.idworkflow AND (w.timestamp IS NULL OR w.timestamp < '2019-06-01');", "SELECT COUNT(DISTINCT(username)) FROM workflow w,task t WHERE w.idworkflow=t.idworkflow AND w.timestamp IS NOT NULL AND w.timestamp >= '2019-06-01' AND w.timestamp < '2020-03-01';", "SELECT COUNT(*) FROM task WHERE timestamp IS NULL OR timestamp < '2019-06-01';", "SELECT COUNT(*) FROM task WHERE timestamp IS NOT NULL AND timestamp >= '2019-06-01' AND timestamp < '2020-03-01';", "SELECT round(SUM(duration/3600*\"#cores\")::numeric,3) AS \"total cores_hours\" FROM task WHERE duration IS NOT NULL AND duration<100000 AND timestamp IS NOT NULL AND timestamp < '2019-06-01';", "SELECT round(SUM(duration/3600*\"#cores\")::numeric,3) AS \"total cores_hours\" FROM task WHERE duration IS NOT NULL AND duration<100000 AND timestamp IS NOT NULL AND timestamp >= '2019-06-01' AND timestamp < '2020-03-01';"]

conn = psycopg2.connect( host=host, user=user, password=password, dbname=dbname, port=port )

n=1
for q in QUERIES:
	
	print("QUERY",n,":",q)
	cur = conn.cursor()
	cur.execute(q)
	print(cur.fetchone()[0])
	print("\n")
	cur.close()
	n+=1
conn.close()







