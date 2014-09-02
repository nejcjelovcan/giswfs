import os
import requests
import json
from bs4 import BeautifulSoup
from collections import OrderedDict
from dogpile.cache import make_region

from dataset import Dataset, GisWfsException
import parsers

class WfsScraper(object):
    """
        :O What's happening at gis? Drugs?
                                        _Anonymous_
        
        To change cache settings modify ../config.json (or instantiate with config dict)
        Will fetch list when instantiated for the first time

        scraper = WfsScraper()
        print scraper.datasets[0].get('name')
        gmlFilename = scraper.datasets[0].getFile(format='gml')
    """
    
    URL_LIST = "http://gis.arso.gov.si/wfs_web/faces/WFSLayersList.jspx"

    def __init__(self, config=None):
        basedir = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../'))
        if not config:
            fconfig = open(os.path.join(basedir, 'config.json'), 'r')
            config = json.load(fconfig)
            fconfig.close()
        self.config = config
        self.fileDir = os.path.join(basedir, config.get('scraper.files', 'files/'))
        try: os.mkdir(self.fileDir)
        except OSError: pass
        self.region = make_region()
        self.region.configure_from_config(config, 'cache.')
        self.oracleStateToken = '1'
        self.setSession()
        self.fireUp()

    def fireUp(self):
        if not self.region.get('dataset_0'):
            datasets = self.fetch()
            for i in range(len(datasets)):
                self.region.set('dataset_%s'%i, OrderedDict(datasets[i]))
        
        i = 0
        self.datasets = []
        dataset = self.region.get('dataset_%s'%i)
        while dataset:
            self.datasets.append(Dataset(self, dataset))
            i += 1
            dataset = Dataset(self, self.region.get('dataset_%s'%i))

    def setSession(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Host":"gis.arso.gov.si",
            "Cache-Control":"max-age=0",
            "Origin":"http://gis.arso.gov.si",
            "Referer":self.URL_LIST,
            "User-Agent":"Mozilla/5.0",
            "Accept":"text/html,application/xhtml+xml,application/xml",
            "Accept-Language":"en-US,en;q=0.8,sl;q=0.6",
        })

    def fetch(self):
        response = self.session.get(self.URL_LIST)
        soup = BeautifulSoup(response.content)
        parser = parsers.ListParser()
        datasets = []
        if parser.container(soup):
            datasets = map(lambda d: Dataset(self, d), parser.parse(soup))
        else:
            raise GisWfsException('Unexpected list response')
        
        return datasets
