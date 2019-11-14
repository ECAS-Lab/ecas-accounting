ECAS accounting
=
The following guide shows how to compute some accounting metrics starting from the information about resource usage tracked by the Ophidia server on a user basis.

Quick start
------------------
1. Install the **PostgreSQL** DBSM
By default, PostgreSQL will create a Linux user named *postgres* to access the database software
2. Access the PostgreSQL Shell, create a new database and connect to it
	```
	su - postgres
	createdb accounting
	psql accounting
	```
3. Create the ***workflow*** and ***task*** tables
	```
	CREATE TABLE workflow (timestamp TIMESTAMP, idworkflow integer, name varchar, username varchar, ip_address varchar, client_address varchar, “#tasks” smallint, “#success_tasks” smallint, duration decimal);
	```
	```
	CREATE TABLE task (timestamp TIMESTAMP, idtask integer, idworkflow integer, operator varchar, “#cores” smallint, success_flag smallint, duration decimal);
	```

4. Import data from the ***workflow*** and ***task*** log files
	```
	\copy workflow (timestamp, idworkflow, name,username, ip_address, client_address, "#tasks", "#success_tasks", duration) from '/path/to/accounting_workflow_log_file' HEADER delimiter E'\t' CSV;
	```		
	```
	\copy task (timestamp, idtask, idworkflow, operator, "#cores", success_flag, duration) from '/path/to/accounting_task_log_file' HEADER delimiter E'\t' CSV;
	```
5. Run the following queries
	* **Total number of active users**
		```
		SELECT COUNT(DISTINCT(username)) FROM workflow w,task t WHERE w.idworkflow=t.idworkflow;
		```
	* **Total number of executed tasks**
		```
		SELECT COUNT(*) FROM task;
		```
  
	* **N most used operators**
		```
		SELECT operator, COUNT(*) FROM task GROUP BY operator ORDER BY COUNT(*) DESC LIMIT <N>;
		```
  
	* **Total number of cores/hour used**
		```
		SELECT round(SUM(duration/3600*"#cores")::numeric,3) AS "total cores/hours" FROM task WHERE duration IS NOT NULL AND duration<100000;
		```

	* **Cumulative execution time per operator**
		```
		SELECT operator, SUM(duration) FROM task WHERE duration IS NOT NULL AND duration<100000 GROUP BY operator ORDER BY SUM(duration) DESC;
		```

	* **Total number of workflows, operators and cores/hour per user**
		```
		SELECT 'Username ' || ROW_NUMBER() OVER (Order by w.username) AS Username, COUNT(DISTINCT(w.idworkflow)) as workflows, count(t.idtask) AS operators, round(SUM(t.duration/3600*t."#cores")::numeric,3) AS corehours FROM workflow w,task t WHERE w.idworkflow = t.idworkflow AND t.duration<100000 AND t.idtask IS NOT NULL GROUP BY(w.username);
		```

	* **Total number of workflows, operators and cores per user**
		```
		**SELECT 'Username ' || ROW_NUMBER() OVER (Order by w.username) AS Username, COUNT(DISTINCT(w.idworkflow)) as workflows, count(t.idworkflow) AS operators, SUM(t."#cores") AS tot_cores FROM workflow w,task t WHERE w.idworkflow = t.idworkflow GROUP BY(w.username);**
		```

	* **Total number of users, workflows, operators and cores/hour**
		```
		SELECT COUNT(DISTINCT(w.username)) as tot_users, COUNT(DISTINCT(w.idworkflow)) as tot_workflows, COUNT(t.idtask) as tot_operators, round(SUM(t.duration/3600*t."#cores")::numeric,3) AS corehours FROM workflow w INNER JOIN task t ON w.idworkflow=t.idworkflow WHERE t.duration<100000 AND t.idtask IS NOT NULL;
		```
	 * **Total number of users, workflows, operators and cores**
		```
		SELECT COUNT(DISTINCT(w.username)) as tot_users, COUNT(DISTINCT(w.idworkflow)) as tot_workflows, COUNT(t.idworkflow) as tot_operators, SUM(t."#cores") AS tot_cores FROM workflow w INNER JOIN task t ON w.idworkflow=t.idworkflow;
		```


NOTE: It is possible to export data by defining a view of a query and exporting it in CSV format. For example:
```
CREATE TABLE metric1 AS (SELECT 'Username ' || ROW_NUMBER() OVER (Order by w.username) AS Username, COUNT(DISTINCT(w.idworkflow)) as workflows, count(t.idtask) AS operators, round(SUM(t.duration/3600*t."#cores")::numeric,3) AS corehours FROM workflow w,task t WHERE w.idworkflow = t.idworkflow AND t.duration<100000 AND t.idtask IS NOT NULL GROUP BY(w.username));
```
```
COPY metric1 TO '/path/to/csv/file' DELIMITER ',' CSV HEADER;
```
In this way each metric can be easily displayed using pie charts, bar charts, tables, and so on,
by exploiting the matplotlib and Pandas libraries available in the Python ecosystem.

In addition to the above metrics, it is possible to extract information about the registered users and their geographic distribution by simply querying the registration information.
