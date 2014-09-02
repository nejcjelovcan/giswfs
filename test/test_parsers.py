import os
import pytest
from bs4 import BeautifulSoup
from pprint import pprint

from giswfs import parsers

FIXTURES = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures')

def openHtml(name):
    f = open(os.path.join(FIXTURES, '%s.html'%name))
    content = f.read()
    f.close()
    return content

def test_listParser():
    parser = parsers.ListParser()
    soup = BeautifulSoup(openHtml('list'))
    data = parser.parse(soup)

    assert len(data) == 192
    assert data[0].get('name') == u'Absolutna najni\u017eja temperatura zraka s povratno dobo 50 let'
    assert data[191].get('id') == 191

    return data

def test_datasetParser():
    parser = parsers.DatasetParser()
    soup = BeautifulSoup(openHtml('dataset'))
    data = parser.parse(soup)
    
    pprint(data)
    assert data.get('urlDownload') == 'http://gis.arso.gov.si/geoserver/ows?SERVICE=WFS&REQUEST=GetFeature&VERSION=1.1.0&TYPENAME=arso%3ACLC_2012_SI&PROPERTYNAME=SHAPE&OUTPUTFORMAT=SHAPE-ZIP&format_options=charset%3AUTF-8'
    assert data.get('urlMetadata') == 'http://gis.arso.gov.si/geoportal/catalog/search/resource/details.page?uuid=%7B59AA1565-B116-4D13-ADE0-3A5176F24369%7D'
    assert data.get('attributes')[5].get('id') == 'LABEL3'