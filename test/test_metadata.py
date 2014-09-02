import pytest
from bs4 import BeautifulSoup

from giswfs import metadata
from test_parsers import openHtml

def test_fgdcBody():
    parser = metadata.FgdcBodyParser()
    soup = BeautifulSoup(openHtml('metadata_fgdcBody'))
    data = parser.parse(soup)

    assert data.get('Keywords').get('Theme').get('Theme Keyword')[1] == 'podnebje'
    assert data.get('Description').get('Abstract')\
        .startswith(u'Karta prikazuje podnebne zna\u010dilnosti Slovenije z vidika najni\u017eje temperature zraka')
    assert data.get('Metadata Reference Information').get('Metadata Contact')\
        .get('Contact Information').get('Hours') == '10.00-12.00'

    return data

def test_isoBody():
    parser = metadata.IsoBodyParser()
    soup = BeautifulSoup(openHtml('metadata_iso_body'))
    data = parser.parse(soup)

    assert data.get('Povzetek')\
        .startswith('Gre za bazo pokrovnosti tal za leto 2012. Baza podatkov CLC 2012 predstavlja pokrovnost tal')
    assert data.get('Osnovne informacije za citiranje vira').get('Datum').get('Datum') == '2014-04-29'

    return data

def test_tablesInSpans():
    parser = metadata.TablesInSpansParser()
    soup = BeautifulSoup(openHtml('metadata_tablesInSpans'))
    data = parser.parse(soup)

    assert data.get(u'Meja obmo\u010dja zbirke podatkov').get(u'Meja obmo\u010dja v metrih (Gauss Krueger)')\
        .get(u'Ju\u017ena meja') == '32799.981691'
    assert data.get('Osnovne informacije').get('Namen')\
        .startswith(u'Podatkovni niz prikazuje Aglomeracije (obmo\u010dja poselitve) v R Sloveniji glede na')

    return data
