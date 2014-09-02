from collections import OrderedDict

class Parser(object):
    def container(self, el): raise NotImplementedError()
    def parse(self, el): raise NotImplementedError()

class ListParser(Parser):
    def container(self, el):
        # @TODO check that it doesn't look like dataset response
        return el.find('form', {'name': 'form1'})

    def parse(self, el):
        datasets = []
        form = self.container(el)
        for td in form.findAll('td', 'x2n'):
            a = td.find('a', 'xl')
            if a:
                dataset = OrderedDict()
                dataset['id'] = int(dict(a.attrs).get('id').split(':')[1])
                dataset['name'] = a.text
                datasets.append(dataset)
        return datasets

class DatasetParser(Parser):
    def container(self, el):
        # @TODO check that it doesn't look like list response
        return el.find('form', {'name': 'form1'})

    def parsePanel(self, el, data):
        data['urlDownload'] = el.find('a', {'id': 'form1:goLink1'}).attrs.get('href').replace('charset%3AWINDOWS-1250', 'charset%3AUTF-8')
        data['urlMetadata'] = el.find('a', {'id': 'form1:goLink2'}).attrs.get('href')
        data['description'] = el.find('span', {'id': 'form1:outputFormatted1'}).text

    def parseAttributes(self, el, data):
        for tr in el.find('table', 'x2f'):
            tds = tr.findAll('td')
            if len(tds) == 3:
                data.append(OrderedDict(id=tds[1].find('span').text, description=tds[2].find('span').text))

    def parse(self, el):
        data = OrderedDict()
        self.parsePanel(el.find('div', {'id': 'form1:panelGroup3'}), data)
        data['attributes'] = []
        self.parseAttributes(el.find('table', {'id': 'form1:panelHorizontal1'}), data['attributes'])
        return data

