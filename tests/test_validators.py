# -*- coding: utf-8 -*-
import json
import os
import pytest

from catchformats.webannotation_schema import CATCH_WEBANNOTATION_SCHEMA
from catchformats.webannotation_validator import validate_annotation
from catchformats.annotatorjs_formatter import annojs_to_annotation
from catchformats.catch_webannotation_validator import validate_format_catchanno
from catchformats.catch_webannotation_validator import validate_format_catcha
from .conftest import here

@pytest.mark.usefixtures('wa_objs')
def test_validate_json(wa_objs):
    import jsonschema

    for media in ['image', 'text', 'video', 'reply']:
        jsonschema.validate(wa_objs[media], CATCH_WEBANNOTATION_SCHEMA)


@pytest.mark.usefixtures('wa_objs')
def test_wa_validate_ok(wa_objs):
    for media in ['image', 'text', 'video', 'reply']:
        x = validate_annotation(wa_objs[media])
        z = validate_format_catchanno(x)
        assert(x == wa_objs[media])

@pytest.mark.skip('not supported yet.')
@pytest.mark.usefixtures('mirador_objs')
def test_mirador_validate_ok(mirador_objs):
    # note: mirador sents body and target as list!
    for oa in mirador_objs:
        x = validate_annotation(oa)
        assert x == oa

@pytest.mark.usefixtures('annojs_objs')
def test_annojs_format_ok(annojs_objs):
    for media in ['image', 'reply', 'text', 'video']:
        x = annojs_to_annotation(annojs_objs[media])
        y = validate_annotation(x)
        z = validate_format_catchanno(x)
        assert x == y

@pytest.mark.skip('skip')
@pytest.mark.usefixtures('annojs_db')
def test_annojs_db(annojs_db):
    outputfile = os.path.join(here, 'files/annojs_to_wa.json')

    with open(outputfile, 'w') as f:
        for a in annojs_db:
            x = annojs_to_annotation(a)
            f.write(json.dumps(x, indent=4))
    assert len(annojs_db) > 0

