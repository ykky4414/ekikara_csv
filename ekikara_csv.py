#! /usr/bin/env python
# -*- coding:utf-8 -*-

import urllib2
from lxml import etree
#from hoge import *

def load( url ):
    opener = urllib2.build_opener()
    return opener.open( url )
def gethour( row ):
    cands = row.xpath( 'td/span/span/text()' )
    assert len( cands ) == 1
    return int( cands[ 0 ] )
def getminutes( row ):
    return [ int( m ) for m in row.xpath( 'td/table/tbody/tr/td/span/span/span/a/text()' ) ]
def getdetail( row ):
    return row.xpath( 'td/table/tbody/tr/td/span/span/text()' )
def parsedetail( trees ):
    tmptree=trees.xpath( '//span[@class="m"]//text()' ) 
    kind=[]
    dest=[]
    flag=0
    for i in tmptree:
        line=i.strip().encode('utf-8')
        if line=="車種":
            flag=1
        elif line=="行先":
            flag=2
        elif line=="注意":
            flag=0
        if flag==1:
            kind.append(line.decode('utf-8'))
        elif flag==2:
            dest.append(line.decode('utf-8'))
    return [kind,dest]
def getdest(parseddestdetail):
    #input parsedetail()[1] > output [ destindex[], destdetail{} ]
    dictionary = { }
    index = []
    if len(parseddestdetail) >0:
        for i in parseddestdetail[1].split(','):
            for n in  i.split():
                if n.find( u"…")>0:
                    x = n.split( u"…")
                    dictionary[x[ 0].encode('utf-8')] = x[1].encode('utf-8')
                    index.append(x[ 0].encode('utf-8'))
        return [ index, dictionary ]
def getkind(parsedkinddetail):
    #input parsedetail()[0] > output [ kindindex[], kinddetail{} ]
    dictionary = { }
    index = []
    counter=0
    for i in parsedkinddetail:
        if i.find(u"…")>0:
            x=i.split(u"…")
            dictionary[x[0].encode('utf-8')]=x[1].encode('utf-8')
            index.append( x[0].encode('utf-8'))
    return  [ index, dictionary ]
def traindetail(detail,index,dictionary):
    for i in index:
        if detail.find( i.decode('utf-8') ) > -1:
            return dictionary[i]
    return dictionary[ index[0] ]

url='http://www.ekikara.jp/newdata/ekijikoku/1307061/down1_13111051.htm'

def maketriprow(url):
    tree = etree.parse( load(url), parser=etree.HTMLParser() )
    rows = tree.xpath( '//td[@class="lowBg01"]/table/tbody/tr/td[@class="lowBg06"]/..' )
    detail=parsedetail(tree)
    dest = getdest(detail[1])
    kind = getkind(detail[0])
    csv=[]
    for r in rows:
        hour=gethour(r)
        i=0
        for minu in getminutes(r):
            tempdetail = getdetail(r)[i]
            tempkind = traindetail( tempdetail, kind[0], kind[1])
            tempdest = traindetail( tempdetail, dest[0], dest[1])
            temptrip=['', tempkind, tempdest, hour, minu]
            csv.append( temptrip)
            i=i+1
    return csv


# filename (for save) , url
urllist=[ 
['test_oidw.csv','http://www.ekikara.jp/newdata/ekijikoku/1307061/down1_13111051.htm'],\
['test_oids.csv','http://www.ekikara.jp/newdata/ekijikoku/1307061/down1_13111051_sat.htm'],\
]

def writefile(filename, string):
    try :
        string=string.decode('utf-8')
    except AttributeError:
        pass
    fp=open(filename,'ab')
    try :
        fp.write(string.encode('utf-8'))
    except AttributeError:
        fp.write( str( string))
    fp.close()
def writecsv(filename,url):
    fp=open(filename,'w')
    fp.write('')
    for line in maketriprow( url ):
        #writefile(filename, 'Null')
        for i,j in enumerate(line[1:]):
            writefile(filename ,j)
            if i<len(line)-2:
                writefile(filename ,',')

        writefile(filename ,'\n' )
    fp.close()
for templist in urllist:
    writecsv(templist[0],templist[1])
