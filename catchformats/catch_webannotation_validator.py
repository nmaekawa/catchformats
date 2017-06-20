
from jsonschema import validate
import jsonschema

from .annotatorjs_formatter import annojs_to_annotation
from .errors import  CatchFormatsError
from .errors import  AnnotatorJSError
from .webannotation_validator import expand_compact_for_context
from .webannotation_validator import validate_annotation
from .webannotation_validator import validate_annotation_mandatory
from .webannotation_validator import validate_annotation_not_for_create
from .webannotation_schema import CATCH_WEBANNOTATION_SCHEMA

CATCH_CONTEXT_IRI='http://catch-dev.harvardx.harvard.edu/catch-context.jsonld'


def validate_format_catcha(wa, mandatory_only=False):
    try:
        norm = expand_compact_for_context(wa, CATCH_CONTEXT_IRI)
        jsonschema.validate(norm, CATCH_WEBANNOTATION_SCHEMA)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error('jsonschema validation error',
                                            exc_info=True)
        raise e
    return norm


def validate_format_catchanno(wa, mandatory_only=False):
    if '@context' in wa:
        try:
            norm = expand_compact_for_context(wa, CATCH_CONTEXT_IRI)
        except Exception as e:
            # try to do more relaxed validation
            try:
                norm = validate_annotation_mandatory(wa)
                if not mandatory_only:
                    norm = validate_annotation_not_for_create(wa)
            except Exception as e:
                # TODO: log more meaninful message!
                raise CatchFormatsError(
                    'cannot format compact webannotation: {}'.format(e))

    else:  # no context, try annotatorjs
        try:
            norm = annojs_to_annotation(wa)
        except Exception as e:
            raise AnnotatorJSError(
                'cannot format from AnnotatorJS: {}'.format(e))

    # by now we have a webannotation
    import json
    print('-------------- norm({})'.format(json.dumps(norm)))
    try:
        validate(norm, CATCH_WEBANNOTATION_SCHEMA)
    except Exception as e:
        raise CatchFormatsError(
            'unable to validate input annotation: {}'.format(str(e)))
    return norm


def wa_are_similar(wa1, wa2):
    '''check that wa1 and wa2 are similar.'''
    # disregard times for created/modified
    for key in ['@context', 'id', 'type', 'schema_version',
                'creator', 'platform']:
        if wa1[key] != wa2[key]:
            print('key({}) is different'.format(key))
            return False

    for key in wa1['permissions']:
        if set(wa1['permissions'][key]) != set(wa2['permissions'][key]):
            print('permissions[{}] is different'.format(key))
            return False

    # body
    if wa1['body']['type'] != wa2['body']['type']:
        print('body type is different')
        return False
    body1 = sorted(wa1['body']['items'], key=lambda k: k['value'])
    body2 = sorted(wa2['body']['items'], key=lambda k: k['value'])
    if body1 != body2:
        print('body items are different')
        return False

    # target
    if wa1['target']['type'] != wa2['target']['type']:
        print('target type is different.')
        return False
    target1 = sorted(wa1['target']['items'], key=lambda k: k['source'])
    target2 = sorted(wa2['target']['items'], key=lambda k: k['source'])
    if target1 != target2:
        print('target items are different')
        return False

    return True

