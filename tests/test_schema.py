# -*- coding: utf-8 -*-
import json
import os
import pytest
from jsonschema import validate

from catchformats.webannotation_validator import validate_annotation
from catchformats.annotatorjs_formatter import annojs_to_annotation
from .conftest import here
from .conftest import readfile_into_jsonobj


@pytest.mark.usefixtures('wa_objs', 'wa_schema')
def test_wa_validate_ok(wa_objs, wa_schema):
    for media in ['image', 'text', 'video', 'reply']:
        validate(wa_objs[media], wa_schema)


@pytest.mark.usefixtures('wa_objs', 'wa_schema')
def test_wa_validate_invisible_var(wa_objs, wa_schema):
    for media in ['image', 'text', 'video', 'reply']:
        wa = wa_objs[media]
        wa['invisible'] = 'my extra var that should not matter.'
        wa['target']['items'][0]['my_custom_something'] = 12
        wa['platform']['custom_var'] = {'blah': 'bleh', 'bloft': 'pluct'}
        validate(wa, wa_schema)
        assert wa['platform']['custom_var']['blah'] == 'bleh'

@pytest.mark.usefixtures('wa_objs', 'wa_schema')
def test_wa_missing_props(wa_objs, wa_schema):
    for media in ['image', 'text', 'video', 'reply']:
        wa = wa_objs[media]
        del(wa['body'])
        assert wa.get('body', None) is None
        validate(wa, wa_schema)
        assert wa.get('body', None) is None

@pytest.mark.usefixtures('wa_schema')
def test_wa_validate_longer(wa_schema):
    filename = os.path.join(here, 'files/annojs_to_wa.json')
    lots = readfile_into_jsonobj(filename)
    for a in lots:
        validate(a, wa_schema)
