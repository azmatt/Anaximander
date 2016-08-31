#Takes the CSV database download from http://opencellid.org/ (Free with API), creates a SQLite database called "cellTowers.sqlite" and inserts the downloaded data into the Database
#The Schema for the database is as follows: radio, mcc, net, area, cell,unit, lon,lat, range, samples, changeable, created, updated, averageSignal
#As of 8/2016 the size of the SQLITE database is approximately 2.6 GB


import csv
import sqlite3

con = sqlite3.Connection('cellTowers.sqlite')
cur = con.cursor()
cur.execute('CREATE TABLE "towers" ("radio" varchar(12), "mcc" varchar(12), "net" varchar(12),"area" varchar(12),"cell" varchar(12),"unit" varchar(12),"lon" varchar(12),"lat" varchar(12),"range" varchar(12),"samples" varchar(12),"changeable" varchar(12),"created" varchar(12),"updated" varchar(12),"averageSignal" varchar(12));')

f = open('cell_towers.csv')
csv_reader = csv.reader(f, delimiter=',')

cur.executemany('INSERT INTO towers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', csv_reader)
cur.close()
con.commit()
con.close()
f.close()