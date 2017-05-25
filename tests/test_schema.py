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


@pytest.mark.usefixtures('wa_schema')
def test_wa_validate_longer(wa_schema):
    filename = os.path.join(here, 'files/annojs_to_wa.json')
    lots = readfile_into_jsonobj(filename)
    for a in lots:
        validate(a, wa_schema)
