import urllib2 
from lxml import etree
from datetime import datetime
links_file = 'review_links.csv'
data_file = 'review_data.csv'

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

    info = []
    for i in range(len(links)):
        info.append(get_single_pitchfork_review(links[i]))
    return(info)

def get_single_pitchfork_review(link):
    
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
        release_date = '',
        reissue = False
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
        info['reissue'] = 1
    else:
        info['release_date'] = info['review_date']
        info['reissue'] = 0

    info['score'] = tree.xpath("//div[@class='info']/span")[0].text.strip()
    info['flagcontent'] = tree.xpath("//div[@class='bnm-label']")[0].text.strip()
    if info['flagcontent'] == '':
        info['flag'] = False
    else:
        info['flag'] = True

    if info['flagcontent'] == 'Best New Reissue' or 'Box Set' in info['album'] or 'Reissue' in info['album']:
        info['reissue'] = 1

    if 'Deluxe Edition' in info['album'] or 'Anniversary Edition' in info['album'] or 'Collectors Edition' in info['album']:
        info['reissue'] = 1

    if 'reissues' in link:
        info['reissue'] = 1

    return(info)

def write_pitchfork_lines(info, f):
    now = datetime.now()
    for i in range(len(info)):
        line = ("'"+info[i]['name']+"'"+','+
            info[i]['score']+','+
            "'"+info[i]['album'].replace("\\",'\\\\').replace("'","\\'")+"'"+','+
            "'"+info[i]['artist'].replace("\\",'\\\\').replace("'","\\'")+"'"+','+
            "'"+info[i]['label'].replace("\\",'\\\\').replace("'","\\'")+"'"+','+
            #info[i]['year']+','+
            "'"+info[i]['flagcontent']+"'"+','+
            str(info[i]['reissue'])+','+
            "'"+info[i]['url']+info[i]['link']+"'"+','+
            "'"+info[i]['reviewer']+"'"+','+
            "'"+now.strftime("%Y-%m-%d")+"'"+','+
            "'"+info[i]['review_date'].strftime("%Y-%m-%d")+"'"+','+
            "'"+info[i]['review_date'].strftime("%Y-%m-%d")+"'"+'\n')
        f.write(line.encode('UTF8'))
        f.flush()
    #import pdb;pdb.set_trace() 

def write_pitchfork_line(info, f):
    now = datetime.now()
    line = ("'"+info['name']+"'"+','+
        info['score']+','+
        "'"+info['album'].replace("\\",'\\\\').replace("'","\\'")+"'"+','+
        "'"+info['artist'].replace("\\",'\\\\').replace("'","\\'")+"'"+','+
        "'"+info['label'].replace("\\",'\\\\').replace("'","\\'")+"'"+','+
        #info['year']+','+
        "'"+info['flagcontent']+"'"+','+
        str(info['reissue'])+','+
        "'"+info['url']+info['link']+"'"+','+
        "'"+info['reviewer']+"'"+','+
        "'"+now.strftime("%Y-%m-%d")+"'"+','+
        "'"+info['review_date'].strftime("%Y-%m-%d")+"'"+','+
        "'"+info['review_date'].strftime("%Y-%m-%d")+"'"+'\n')
    f.write(line.encode('UTF8'))
    f.flush()
    #import pdb;pdb.set_trace()

def write_lines(lines,f):
    f.write('\n'.join(lines))
    f.write('\n')

def save_pitchfork_links(links_file):
    flinks = open(links_file, 'w')
    for i in range(1,680):
        path = 'http://pitchfork.com/reviews/albums/' + str(i) +'/'
        try:
            #print i
            links = get_pitchfork_review_links(path)
            write_lines(links,flinks)
            flinks.flush()
        except:
            print 'Error on page: '+str(i)
    flinks.close()

#save_pitchfork_links(links_file)
flinks = open(links_file, 'r')
links = flinks.readlines()

fdata = open(data_file, 'w')
fdata.write('site,score,album,artist,label,year,flag,reissue,url,reviewer,date_retrieved,date_released,date_reviewed\n')

for i in range(len(links)):
    try:
        #print i
        info = get_single_pitchfork_review(links[i].strip())
        write_pitchfork_line(info,fdata)
    except:
        'Error on link:'+links[i]
fdata.close()
