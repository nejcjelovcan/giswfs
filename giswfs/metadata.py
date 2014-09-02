from collections import OrderedDict
from parsers import Parser

class FgdcBodyParser(Parser):
    "get nested metadata from <dl><dt> tree"
    
    def parseDl(self, el, data, key=None):
        if key:
            d = data[key] = OrderedDict()
            key = None
            self.parseLevel(el, d)
        else:
            self.parseLevel(el, data)

    def parseLevel(self, el, data):
        key = None
        for child in el:
            if isinstance(child, basestring): pass
            elif child.name == 'dl':
                self.parseDl(child, data, key)
            elif child.name == 'dt':
                for child in child:
                    isstr = isinstance(child, basestring)
                    if isstr or child.name in ('a', 'span'):
                        text = child.strip() if isstr else child.text.strip()
                        if text and key:
                            if key in ['Theme Keyword', 'Place Keyword']:
                                if key not in data: data[key] = []
                                data[key].append(text)
                            else:
                                data[key] = text
                            key = None
                    elif child.name == 'em':
                        key = child.text.strip(': ')
                    elif child.name == 'dl':
                        self.parseDl(child, data, key)
            elif child.name == 'hr': self.parseLevel(child, data)

    def container(self, el):
        return el.find('div', {'class': 'fgdcBody'})

    def parse(self, el):
        metadata = OrderedDict()
        self.parseLevel(self.container(el), metadata)
        return metadata

class IsoBodyParser(FgdcBodyParser):
    def container(self, el):
        return el.find('div', {'class': 'iso_body'})

class TablesInSpansParser(Parser):
    "We're dealing with a badass here"

    def parseParameterTable(self, el, data):
        for tr in el.find('tbody'):
            if isinstance(tr, basestring): pass
            else:
                key = tr.select('td.parameterLabel')[0].text.strip(': ')
                value = tr.select('td.parameterValue')[0].text
                data[key] = value

    def parseSections(self, el, data):
        key = None
        for child in el:
            if isinstance(child, basestring): pass
            elif child.name == 'span':
                attrs = OrderedDict(child.attrs)
                if 'section' in attrs.get('class', []):
                    key = child.find('span', {'class': 'sectionCaption'}).text.strip(': ')
                    data[key] = OrderedDict()
                    td = child.find('table', {'class': 'sectionBody'}).find('tbody').find('tr').find('td')
                    if td.find('span', {'class': 'section'}):
                        self.parseSections(td, data[key])
                    else:
                        parameterTable = td.find('table', {'class': 'parameters'})
                        if parameterTable:
                            data[key] = OrderedDict()
                            self.parseParameterTable(parameterTable, data[key])

    def container(self, el):
        return el.find('span', {'id': 'cmPlPgpPageBody'})

    def parse(self, el):
        metadata = OrderedDict()
        self.parseSections(self.container(el).findAll('form')[0], metadata)
        return metadata

metadataParsers = [FgdcBodyParser(), IsoBodyParser(), TablesInSpansParser()]