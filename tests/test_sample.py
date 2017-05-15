# -*- coding: utf-8 -*-
import pytest
from catchformats.webannotation_validator import validate_annotation

def test_pass():
        assert True, "dummy sample test"

@pytest.mark.usefixtures('wa_objs')
def test_wa_validate_ok(wa_objs):
    for media in ['image', 'text', 'video', 'reply']:
        x = validate_annotation(wa_objs[media])
        assert(x == wa_objs[media])

@pytest.mark.ignore('not supported yet.')
@pytest.mark.usefixtures('mirador_objs')
def test_mirador_validate_ok(mirador_objs):
    # note: mirador sents body and target as list!
    for oa in mirador_objs:
        x = validate_annotation(oa)
        assert x == oa





