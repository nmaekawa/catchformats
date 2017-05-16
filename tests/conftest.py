# -*- coding: utf-8 -*-
import json
from pyld import jsonld
import os
import pytest

CATCH_CONTEXT = 'http://catch-dev.harvardx.harvard.edu/catch-context.jsonld'


here = os.path.abspath(os.path.dirname(__file__))


def readfile_into_jsonobj(filepath):
    with open(filepath, 'r') as f:
        context = f.read()
    return json.loads(context)


@pytest.fixture(scope='function')
def wa_objs():
    filename = os.path.join(here, 'files/wa_sample.json')
    return readfile_into_jsonobj(filename)


@pytest.fixture(scope='function')
def mirador_objs():
    filename = os.path.join(here, 'files/mirador_sample.json')
    mir = []
    objs = readfile_into_jsonobj(filename)
    for x in objs:
        context = x['@context']
        comp = jsonld.compact(x, context)
        expa = jsonld.expand(comp)
        trans = jsonld.compact(expa, CATCH_CONTEXT)
        trans['created'] = ''
        trans['modified'] = ''
        trans['creator'] = {
            'id': '987654321',
            'name': 'clarice_lispector'
        }
        trans['permissions'] = {
            'can_read': [],
            'can_update': ['clarice_lispector'],
            'can_delete': ['clarice_lispector'],
            'can_admin': ['clarice_lispector'],
        }
        mir.append(trans)
    return mir

@pytest.fixture(scope='function')
def annojs_objs():
    filename = os.path.join(here, 'files/annojs_sample.json')
    return readfile_into_jsonobj(filename)

@pytest.fixture(scope='function')
def annojs_db():
    filename = os.path.join(here, 'files/annotatorjs_large_sample.json')
    return readfile_into_jsonobj(filename)
