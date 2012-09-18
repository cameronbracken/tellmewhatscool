import urllib2 
from lxml import etree
from datetime import datetime

def get_pitchfork_review_links(path):
    response = urllib2.urlopen(path)
    html = response.read()
    tree = etree.HTML(html)

    r = tree.xpath("//div[@id='main']/ul/li/ul/li/a")

    links = list()
    for i in range(len(r)):
        links.append(r[i].values()[0])
    #links = unique(links)[:nvalues]
    return(links)

def get_pitchfork_review_data(links):

    nvalues = len(links)
    url = 'http://pitchfork.com'
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
        url = url,
        reviewer = [],
        review_date = []
    )

    for i in range(nvalues):
        info['links'].append(links[i])
        response = urllib2.urlopen(url + links[i])
        html = response.read()
        tree = etree.HTML(html)

        # if the artist name is not a link then it is probably various
        # TODO: more than one artist (splits), currently returns first artist only
        # TODO: add date if year is missing
        try:
            info['artist'].append(tree.xpath("//ul[@class='review-meta']/li/div/h1/a")[0].text)
        except:
            info['artist'].append(tree.xpath("//ul[@class='review-meta']/li/div/h1")[0].text)

        info['album'].append(tree.xpath("//ul[@class='review-meta']/li/div/h2")[0].text)
        xx = tree.xpath("//ul[@class='review-meta']/li/div/h3")[0].text
        info['label'].append(xx.partition(';')[0].strip())
        info['year'].append(xx.partition(';')[2].strip())
        info['reviewer'].append(tree.xpath("//address")[0].text)
        info['review_date'].append(datetime.strptime(tree.xpath("//h4/span")[0].text, '%B %d, %Y'))
        info['score'].append(tree.xpath("//div[@class='info']/span")[0].text.strip())
        info['flagcontent'].append(tree.xpath("//div[@class='bnm-label']")[0].text.strip())
        if info['flagcontent'][0] == '':
            info['flag'].append(False)
        else:
            info['flag'].append(True)
    return(info)

path = 'http://pitchfork.com/reviews/albums/670/'

links = get_pitchfork_review_links(path)
info = get_pitchfork_review_data(links)