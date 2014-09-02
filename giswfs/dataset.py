import os
import re
import json
import urllib
import urlparse
import requests
import hashlib
from bs4 import BeautifulSoup
from collections import OrderedDict

from metadata import metadataParsers
import parsers

class GisWfsException(Exception): pass

class Dataset(OrderedDict):
    """
        Lazy dataset

        __getitem__ description|attributes|urlMetadata|urlDownload
        will trigger an info request if not yet set

        __getitem__ metadata
        will trigger metadata request if not yet set
    """

    DATASET_POST = {
        "selectKeyword":0,
        "table4:rangeStart":0,
        "listOfLayersTable:selected":0,
        "listOfLayersTable:rangeStart":0,
        "oracle.adf.faces.FORM":"form1",
        "oracle.adf.faces.STATE_TOKEN":1,
        "event":"",
        "partial":"",
    }
    RE_SLUG = re.compile('[^a-zA-Z0-9\s]')

    def __init__(self, scraper, dct=None):
        super(Dataset, self).__init__()
        self.scraper = scraper
        if dct: self.update(dct)

    def __getitem__(self, item):
        "Lazy requests for info and metadata"
        if item in ('description', 'urlMetadata', 'urlDownload', 'attributes'):
            if item not in self: self.fetchInfo()
        elif item in ('metadata',):
            if item not in self: self.fetchMetadata()
        return super(Dataset, self).__getitem__(item)

    def __repr__(self):
        return 'DatasetDict:%s'%json.dumps(OrderedDict(self), indent=2)

    def fetchInfo(self, metadata=False):
        "Fetch description, attributes and urls"
        jsessid = self.scraper.session.cookies.get_dict().get('JSESSIONID', None)
        if not jsessid:
            print 'Listing first to get session ID...'
            self.scraper.fetch()

        jsessid = self.scraper.session.cookies.get_dict().get('JSESSIONID', '')
        if jsessid:
            url = '%s;jsessionid=%s'%(self.scraper.URL_LIST, jsessid)

        print 'Getting dataset...'

        data = dict()
        data.update(self.DATASET_POST)
        data.update({
            'oracle.adf.faces.STATE_TOKEN': '1',
            'source': 'listOfLayersTable:%s:clLayerNameLink'%self['id']
        })
        response = self.scraper.session.post(url, data)
        soup = BeautifulSoup(response.content)

        parser = parsers.DatasetParser()
        if parser.container(soup):
            self.update(parser.parse(soup))
        else:
            raise GisWfsException('Unexpected dataset response')

        if not self.get('urlMetadata'):
            print 'No metadata URL could be parsed for dataset'
        if not self.get('urlDownload'):
            raise GisWfsException('No download URL could be parsed for dataset')

        self.scraper.region.set('dataset_%s'%self['id'], OrderedDict(self))

    def fetchMetadata(self):
        "Fetch metadata"
        if self['urlMetadata']:
            print 'Getting metadata', self['urlMetadata']
            response = self.scraper.session.get(self['urlMetadata'])
            soup = BeautifulSoup(response.content)

            for parser in metadataParsers:
                el = parser.container(soup)
                if el:
                    print 'Seems like this is the right metadata parser: %s'%type(parser)
                    self['metadata'] = parser.parse(soup)
                    self['metadata']['_giswfs_parser'] = type(parser).__name__
                    self.scraper.region.set('dataset_%s'%self['id'], OrderedDict(self))
                    return

            self['metadata'] = OrderedDict()
            self.scraper.region.set('dataset_%s'%self['id'], OrderedDict(self))

    def getSlug(self, spaces=False):
        slug = self.RE_SLUG.sub('', self['name'])
        if not spaces: return slug.replace(' ', '')
        return slug

    def getUrl(self, format='gml', attributes=None):
        "Return filename and url for given gml and attributes (all attributes if none given)"
        purl = urlparse.urlparse(self['urlDownload'])
        qs = urlparse.parse_qs(purl.query)

        if format in ('gml', 'gml2'): format = 'GML2'
        else: format = 'SHAPE-ZIP'
        qs['OUTPUTFORMAT'] = [format]
        
        if not attributes: attributes = map(lambda attr: attr.get('id'), self.get('attributes', []))
        if 'PROPERTYNAME' in qs: attributes = [qs['PROPERTYNAME'][0]]+attributes
        qs['PROPERTYNAME'] = [','.join(attributes)]

        turl = tuple(purl)
        url = urlparse.urlunparse(turl[0:4]+(urllib.urlencode([(k,v[0]) for k,v in qs.items()]),)+('',))
        fn = '%d_%s_%s.%s'%(self['id'], self.getSlug().lower()[:48],
            hashlib.sha1(url).hexdigest()[:8], 'gml' if format == 'GML2' else 'zip')
        return fn, url

    def getFile(self, format='gml', attributes=None):
        "Download file for given format and attributes (all attributes if none given). Returns filename"
        fn, url = self.getUrl(format=format, attributes=attributes)

        fn = os.path.join(self.scraper.fileDir, fn)
        if not os.path.exists(fn):
            f = open(fn, 'wb')
            print 'Fetching file %s'%url
            response = requests.get(url, stream=True)

            if not response.ok:
                f.close()
                raise GisWfsException('Unexpected download response')

            for block in response.iter_content(1024):
                if not block:
                    break
                f.write(block)
            f.close()        

        return fn