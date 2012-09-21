#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys

con = None
data_file = 'review_data.csv'


f = open(data_file,'r')
lines = f.readlines()

con = mdb.connect('localhost', 'bracken_tmwc', 
    'iknowwhatscool', 'bracken_tmwc',charset='utf8');


query = 'insert into ratings (site,score,album,artist,label,year,flag,url,reviewer,date_retrieved,date_released,date_reviewed) values ('
cur = con.cursor()
for i in reversed(range(len(lines))):
    try:
        # skip first line
        if(i > 0):
            q = query + lines[i].strip() + ');'
            cur.execute(q)
    except mdb.Error, e:

        print "Error %d: %s" % (e.args[0],e.args[1])
        print q
        #sys.exit(1)
  
if con:
    con.close()
