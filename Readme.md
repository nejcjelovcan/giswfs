Parser za seznam zemljevidov na http://gis.arso.gov.si/wfs_web/faces/WFSLayersList.jspx


Vse podatke privzeto shranjuje na disku in zahtevke na gis.arso.gov.si dela le, če podatkov še ni. Nastavitve za cache in destinacijo prenosov datotek so v config.json.

### Namestitev
```
git clone ...
pip install -r requirements
```

### Uporaba

```
from giswfs import WfsScraper
scraper = WfsScraper()          # prenese se seznam zbirk

scraper.datasets                # list objektov Dataset(OrderedDict)
dataset = scraper.datasets[0]

dataset['name']
> Absolutna najnižja temperatura zraka s povratno dobo 50 let

gmlFilename = dataset.getFile(format='gml')   # zahtevek za prenos datoteke
> ./files/0_absolutnanajnizjatemperatura_3d7f0e38.gml
```

### Dataset OrderedDict

Ključ | Opis
------------ | -------------
dataset['name'] | ime vira
dataset['description'] | opis podatkov
dataset['urlDownload'] | povezava za prenos
dataset['urlMetadata'] | povezava do metapodatkov (ni nujno, da obstaja)
dataset['attributes'] | seznam atributov (id in description) (pri zemljevidu potresnih opazovalnic so to recimo ime, inštrument, nadmorska višina...)
dataset['metadata'] | drevo metapodatkov (ni nujno, da obstaja, shema je odvisna od formata - '_giswfs_parser' pove, kater parser je bil najbolj primeren)

* **dataset.getFile(format='gml', attributes=None)**<br/>
    prenese in vrne ime datoteke<br/>
    format je lahko 'gml', ali 'shp' (.zip shp, shx in dst datotek)<br/>
    attributes je lahko seznam id-jev atributov (dataset['attributes']), sicer vzame vse
