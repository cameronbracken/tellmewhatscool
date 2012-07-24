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

def main(argv=None):
    tmwc = TellMeWhatsCool()
    tmwc.get_review_data(['pitchfork'])
    tmwc.format_review_data()
    tmwc.send_email()

class TellMeWhatsCool():
    
    def __init__(self):
        self.data = dict()
    
    def get_review_data(self,sources):
        for source in sources:
            try:
                # get the blob of data from a review site given the name
                self.data[source] = getattr(self, 'get_' + source + '_review_data')()
            except Exception:
                print 'Unknown Review Site.'
    
    
    def format_review_data(self):
        """
        Iterate through the review data, make a giant string out of all of it.
        """
        x = ''
        for info in self.data.itervalues():            
            x = x + info['name'] + ' Daily Summary\n\n'
            for i in range(info['nvalues']):
                x = x + '  ' + info['score'][i] +' - '+ info['artist'][i] + ' - ' + info['album'][i]
                if info['flag'][i]:
                    x = x + ' *' + info['flagcontent'][i] + '*'
                x = x + '\n      ' + info['label'][i] + ', ' + info['year'][i]
		x = x + '\n      ' + info['url'] + info['links'][i] + '\n'
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
        
        self.make_mime_message(self.body)
        
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.ehlo()
        s.starttls()
        s.ehlo()

        s.login(os.environ['TMWC_EMAIL'],os.environ['TMWC_PASS'])
        s.sendmail(self.msg['From'],self.msg['To'],self.msg.as_string())
        s.close()
    
    def get_pitchfork_review_data(self):
        import urllib2
        from lxml import etree

        url = 'http://pitchfork.com'

        nvalues = 5
        info = dict(
            name = 'Pitchfork',
            score = [],
            album = [],
            artist = [],
            label = [],
            year =  [],
            flag = [],
            flagcontent = [],
            nvalues = nvalues,
	    links = [],
	    url = url
        )
        response = urllib2.urlopen('http://pitchfork.com')
        html = response.read()
        tree = etree.HTML(html)
        r = unique(tree.xpath("//div[@class='review-detail']/div/a"))

        links = list()
        for i in range(len(r)):
            links.append(r[i].values()[0])
        links = unique(links)[:nvalues]

        for i in range(nvalues):
	    info['links'].append(links[i])
            response = urllib2.urlopen(url + links[i])
            html = response.read()
            tree = etree.HTML(html)
 
            # if the artist name is not a link then it is probably various
	    # TODO: more than one artist (splits), currently returns first artist only
            try:
                info['artist'].append(tree.xpath("//ul[@class='review-meta']/li/div/h1/a")[0].text)
            except:
                info['artist'].append(tree.xpath("//ul[@class='review-meta']/li/div/h1")[0].text)

            info['album'].append(tree.xpath("//ul[@class='review-meta']/li/div/h2")[0].text)
            xx = tree.xpath("//ul[@class='review-meta']/li/div/h3")[0].text
            info['label'].append(xx.partition(';')[0].strip())
            info['year'].append(xx.partition(';')[2].strip())
            info['score'].append(tree.xpath("//div[@class='info']/span")[0].text.strip())
            info['flagcontent'].append(tree.xpath("//div[@class='bnm-label']")[0].text.strip())
            if info['flagcontent'][0] == '':
                info['flag'].append(False)
            else:
                info['flag'].append(True)
            #import pdb; pdb.set_trace()

        return(info)


def unique(inlist, keepstr=True):
    typ = type(inlist)
    if not typ == list:
        inlist = list(inlist)
    i = 0
    while i < len(inlist):
        try:
            del inlist[inlist.index(inlist[i], i + 1)]
        except:
            i += 1
    if not typ in (str, unicode):
        inlist = typ(inlist)
    else:
        if keepstr:
            inlist = ''.join(inlist)
    return inlist

if __name__ == "__main__":
    main()
