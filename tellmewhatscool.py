#!/usr/bin/env python2.7
# encoding: utf-8
"""
tellmewhatscool.py

Created by Cameron Bracken on 2012-03-11.
Copyright (c) 2012 __Tell Me What's Cool__. All rights reserved.
"""

help_message = '''
TMWC_PASS=<gmail pass>
TMWC_EMAIL=<gmail account>
export TMWC_EMAIL
export TMWC_PASS
'''

import cgi
import cgitb; cgitb.enable()  # for troubleshooting


def main(argv=None):
    tmwc = TellMeWhatsCool()
    tmwc.get_review_data(['pitchfork'])
    tmwc.format_review_data()
    tmwc.get_queries()
    tmwc.send_queries()
    sent = tmwc.send_email()
    #print "Content-type: text/html"
    #print 
    if(sent):
        print "Sent."
    else:
        print "No new reviews today."

class TellMeWhatsCool():
    
    def __init__(self):
        self.data = dict()
        self.queries = dict()
    
    def get_review_data(self,sources):
        for source in sources:
            try:
                # get the blob of data from a review site given the name
                self.data[source] = getattr(self, 'get_' + source + '_review_data')()
            except:
                print 'No new ' + source + ' data.'

    def get_queries(self):
        sources = self.data.keys()
        for source in sources:
            try:
                # get the blob of data from a review site given the name
                self.queries[source] = getattr(self, 'get_' + source + '_queries')()
            except:
                print 'Error building queries.'

    def get_pitchfork_queries(self):
        q = []
        from datetime import datetime
        now = datetime.now()
        info = self.data['pitchfork']

        for i in range(len(info)):
            q.append('')
            q[i] = 'insert into ratings (site, score, album, artist, label, '
            q[i] = q[i] + 'flag, url, date_retrieved, date_released, date_reviewed) values ('
            q[i] = q[i] + "'" + info[i]['name'] + "',"
            q[i] = q[i] + info[i]['score'] + ","
            q[i] = q[i] + "'" + info[i]['album'].replace("\\",'\\\\').replace("'","\\'") + "',"
            q[i] = q[i] + "'" + info[i]['artist'].replace("\\",'\\\\').replace("'","\\'") + "',"
            q[i] = q[i] + "'" + info[i]['label'].replace("\\",'\\\\').replace("'","\\'") + "',"
            #q[i] = q[i] + "'" + info[i]['year'] + "',"
            q[i] = q[i] + "'" + info[i]['flagcontent'] + "',"
            q[i] = q[i] + "'" + info[i]['url'] + info[i]['link'] + "',"
            q[i] = q[i] + "'" + now.strftime("%Y-%m-%d") + "',"
            q[i] = q[i] + "'" + now.strftime("%Y-%m-%d") + "',"
            q[i] = q[i] + "'" + now.strftime("%Y-%m-%d") + "');"
        return(q)
    
    def send_queries(self):
        import MySQLdb as mdb
        import sys

        con = None
        con = mdb.connect('localhost', 'bracken_tmwc', 
                'iknowwhatscool', 'bracken_tmwc');
        cur = con.cursor()

        for queries in self.queries.itervalues():            
            for i in range(len(queries)):
                
                try:
                    #import pdb; pdb.set_trace() 
                    cur.execute(queries[i])
                except mdb.Error, e:
                    print "Error %d: %s" % (e.args[0],e.args[1])
        if con:    
            con.close()
    
    def format_review_data(self):
        """
        Iterate through the review data, make a giant string out of all of it.
        """
        x = ''
        for info in self.data.itervalues():            
            x = x + info[0]['name'] + ' Daily Summary\n\n'
            for i in range(len(info)):
                x = x + '  ' + info[i]['score'] +' - '+ info[i]['artist'] + ' - ' + info[i]['album']
                if info[i]['flag']:
                    x = x + ' *' + info[i]['flagcontent'] + '*'
                x = x + '\n      ' + info[i]['label'] + ', ' + info[i]['release_date'].strftime("%Y-%m-%d")
                x = x + '\n      ' + info[i]['url'] + info[i]['link'] + '\n'
                x = x + '\n'
        self.body = x

    def make_mime_message(self,body):
        from email.MIMEText import MIMEText
        from datetime import datetime
        now = datetime.now()
        
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = 'Daily Review Summary - ' + now.strftime("%B %d, %Y")
        msg['From'] = 'Tell Me What\'s Cool <tellmewhatscool@gmail.com>'
        msg['To'] = 'cameron.bracken@gmail.com'
        
        self.msg = msg
    
    def send_email(self):
        import smtplib
        import os
        
        should_send = (self.body != '')
	
        #import pdb; pdb.set_trace() 
        
        if(should_send):
            self.make_mime_message(self.body)
        
            s = smtplib.SMTP("smtp.gmail.com", 587)
            s.ehlo()
            s.starttls()
            s.ehlo()

            s.login(os.environ['TMWC_EMAIL'],os.environ['TMWC_PASS'])
            s.sendmail(self.msg['From'],self.msg['To'],self.msg.as_string())
            s.close()

        return(should_send)

    def get_pitchfork_review_links(self,limit):
        import urllib2
        from lxml import etree
        path = 'http://pitchfork.com/reviews/albums/'
        response = urllib2.urlopen(path)
        html = response.read()
        tree = etree.HTML(html)

        r = tree.xpath("//div[@id='main']/ul/li/ul/li/a")

        links = list()
        for i in range(limit):
            links.append(r[i].values()[0])
        #links = unique(links)[:nvalues]
        return(links)

    def get_single_pitchfork_review(self,link):
        import urllib2
        from lxml import etree
        from datetime import datetime

        url = 'http://pitchfork.com'
        info = dict(
            name = 'Pitchfork',
            score = '',
            album = '',
            artist = '',
            label = '',
            flag = False,
            flagcontent = '',
            link = link,
            url = url,
            reviewer = '',
            review_date = '',
            release_date = ''
        )
        
        response = urllib2.urlopen(url + link)
        html = response.read()
        tree = etree.HTML(html)

        # if the artist name is not a link then it is probably various
        # TODO: more than one artist (splits), currently returns first artist only
        # TODO: add date if year is missing
        try:
            info['artist'] = tree.xpath("//ul[@class='review-meta']/li/div/h1/a")[0].text
        except:
            info['artist'] = tree.xpath("//ul[@class='review-meta']/li/div/h1")[0].text

        info['album'] = tree.xpath("//ul[@class='review-meta']/li/div/h2")[0].text
        xx = tree.xpath("//ul[@class='review-meta']/li/div/h3")[0].text
    
        info['reviewer'] = tree.xpath("//address")[0].text
        info['review_date'] = datetime.strptime(tree.xpath("//h4/span")[0].text, '%B %d, %Y')
        info['label'] = xx.partition(';')[0].strip()

            # if the year is year1/year2 then this is a reissue, need to change the release date
        year = xx.partition(';')[2].strip()
        if len(year) > 4:
            info['release_date'] = datetime.strptime(year.partition('/')[2].strip()+'-01-01',"%Y-%m-%d")
        else:
            info['release_date'] = info['review_date']

        info['score'] = tree.xpath("//div[@class='info']/span")[0].text.strip()
        info['flagcontent'] = tree.xpath("//div[@class='bnm-label']")[0].text.strip()
        if info['flagcontent'] == '':
            info['flag'] = False
        else:
            info['flag'] = True
        return(info)

    def get_pitchfork_review_data(self):
        import urllib2

        links = self.get_pitchfork_review_links(5)

        info = []
        for i in range(len(links)):
            info.append(self.get_single_pitchfork_review(links[i]))
        return(info)

if __name__ == "__main__":
    main()
