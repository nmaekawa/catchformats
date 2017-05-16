import json
from pyld import jsonld

from .errors import  MissingPropertyInInputAnnotation
from .errors import  InvalidPropertyTypeInInputAnnotation
from .errors import  UnsupportedJsonContextError


CATCH_CONTEXT_IRI = 'http://catch-dev.harvardx.harvard.edu/catch-context.jsonld'
MIRADOR_CONTEXT_IRI = 'http://iiif.io/api/presentation/2/context.json'


WA_MANDATORY_PROPS = {
    # `schema_version`, `permissions`, `platform` not mandatory
    'anno': ['type',  'created', 'modified', 'creator', 'body', 'target'],
    'creator': ['id', 'name'],
    'body': ['type', 'items'],
    'body_items': ['type', 'purpose', 'value'],  # `format` not mandatory
    'target': ['type', 'items'],
    'target_items': ['type', 'source'],  # `format` not mandatory
    'permissions': ['can_read', 'can_update', 'can_delete', 'can_admin'],
    'platform': ['name', 'contextId', 'collectionId', 'target_source_id'],
}


def validate_annotation(wa):
    '''minimal validation, for generic web annotation.'''
    wa_id = wa['id'] if 'id' in wa else 'unknown'

    validate_anno_dict('anno', wa, wa_id)
    validate_anno_dict('creator', wa['creator'], wa_id)
    validate_anno_dict('permissions', wa['permissions'], wa_id)
    validate_anno_list_or_dict('body', wa['body'], wa_id)
    validate_anno_list_or_dict('target', wa['target'], wa_id)
    return wa


def validate_anno_dict(prop, obj, wa_id):
    '''check for keys in dict.'''
    if not isinstance(obj, dict):
        raise InvalidPropertyTypeInInputAnnotation(
            'expected dict for {} in anno({}), found ({})'.format(
                prop, wa_id, type(obj)))

    for mandatory in WA_MANDATORY_PROPS[prop]:
        if mandatory not in obj:
            msg = 'expected ({}) in {} present in anno({})'.format(
                    mandatory, prop, wa_id)
            raise MissingPropertyInInputAnnotation(msg)
    return obj


def validate_anno_list_of_dicts(prop, obj, wa_id):
    '''for props that have items list, like `body`, `target`, `selector`...'''
    if not isinstance(obj, list):
        raise InvalidPropertyTypeInInputAnnotation(
            'expected list for {}.items in anno({}), found ({})'.format(
                prop, wa_id, type(obj)))

    for it in obj:
        for mandatory in WA_MANDATORY_PROPS[prop]:
            if mandatory not in it:
                raise MissingPropertyInInputAnnotation(
                    'expected ({}) present in {}.items in anno({})'.format(
                        mandatory, prop, wa_id))
    return obj


def validate_anno_list_or_dict(prop, obj, wa_id):
    if isinstance(obj, dict):
        validate_anno_dict(prop, obj, wa_id)
        if isinstance(obj['items'], list):
            pass
    elif isinstance(obj, list):
        # BEWARE: changing input object
        obj = {'type': 'List', 'items': obj}
    else:
        raise InvalidPropertyTypeInInputAnnotation(
            'expected list or dict for {} in anno({}), found({})'.format(
                prop, wa_id, type(obj)))

    validate_anno_list_of_dicts(
        '_'.join([prop, 'items']), obj['items'], wa_id)

    return obj


def expand_compact(wa):
    '''assumes anno has @context.'''
    context = wa['@context']
    try:
        compacted = jsonld.compact(wa, context)
    except Exception as e:
        msg = 'compaction for context({}) of anno({}) failed: {}'.format(
            context, wa['id'], str(e))
        raise e

    try:
        expanded = jsonld.expand(compacted)
    except Exception as e:
        msg = 'expansion for context({}) of anno({}) failed: {}'.format(
            context, wa['id'], str(e))
        raise e

    try:
        translated = jsonld.compact(expanded, CATCH_CONTEXT_IRI)
    except Exception as e:
        msg = 'translation for context({}) of anno({}) failed: {}'.format(
            CATCH_CONTEXT_IRI, wa['id'], str(e))
        raise e

    return translated


