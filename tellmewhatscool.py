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
    p4k = get_pitchfork_review_data()
    p4k['text'] = format_review_data(p4k)
    p4k_msg = make_msg(p4k)
    send_email(p4k_msg)

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

def get_pitchfork_review_data(dl_dir = 'dl'):
    import urllib2
    import os
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
        nvalues = nvalues
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
        response = urllib2.urlopen(url + links[i])
        html = response.read()
        tree = etree.HTML(html)
        
        info['artist'].append(tree.xpath("//ul[@class='review-meta']/li/div/h1/a")[0].text)
        info['album'].append(tree.xpath("//ul[@class='review-meta']/li/div/h2")[0].text)
        xx = tree.xpath("//ul[@class='review-meta']/li/div/h3")[0].text
        info['label'].append(xx.partition(';')[0].strip())
        info['year'].append(xx.partition(';')[2].strip())
        info['score'].append(tree.xpath("//div[@class='info']/span")[0].text.strip())
    
    return(info)

def format_review_data(info):
    x = info['name'] + ' Daily Summary\n\n'
    for i in range(info['nvalues']):
        x = x + '  ' + info['score'][i] +' - '+ info['artist'][i] + ' - ' + info['album'][i] + \
            '\n      ' + info['label'][i] + ', ' + info['year'][i] + '' + '\n\n'
    return(x)

def make_msg(info):
    from email.MIMEText import MIMEText
    from datetime import datetime
    now = datetime.now()
    
    msg = MIMEText(info['text'], 'plain', 'utf-8')
    msg['Subject'] = 'Daily Review Summary - ' + now.strftime("%B %m, %Y")
    msg['From'] = 'Tell Me What\'s Cool <tellmewhatscool@gmail.com>'
    msg['To'] = 'cameron.bracken@gmail.com'
    
    return(msg)

def send_email(msg):
    import smtplib
    import os
    
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.ehlo()

    s.login(os.environ['TMWC_EMAIL'],os.environ['TMWC_PASS'])
    s.sendmail(msg['From'],msg['To'],msg.as_string())

if __name__ == "__main__":
    main()
