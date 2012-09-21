#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import sys

con = None
data_file = 'review_data.csv'

try:

    f = open(data_file,'r')
    lines = f.readlines()
    
    con = mdb.connect('localhost', 'bracken_tmwc', 
        'iknowwhatscool', 'bracken_tmwc');
    
    
    query = 'insert into ratings (site,score,album,artist,label,year,flag,url,reviewer,date_retrieved,date_released,date_reviewed) values ('
    cur = con.cursor()
    for i in reversed(len(lines)):
        cur.execute(query + lines[i].strip() + ');')
    
except mdb.Error, e:
  
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)
    
finally:    
        
    if con:    
        con.close()
