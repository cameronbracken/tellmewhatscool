#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import _mysql
import sys


con = None

try:

    con = _mysql.connect('localhost', 'bracken_tmwc', 
        'iknowwhatscool', 'bracken_tmwc')
        
    con.query("SELECT VERSION()")
    result = con.use_result()
    
    print "MySQL version: %s" % \
        result.fetch_row()[0]
    
except _mysql.Error, e:
  
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

finally:
    
    if con:
        con.close()
