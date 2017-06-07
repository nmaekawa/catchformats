import json
from pyld import jsonld

from .errors import  MissingPropertyInInputAnnotation
from .errors import  InvalidPropertyTypeInInputAnnotation
from .errors import  UnsupportedJsonContextError


CATCH_CONTEXT_IRI = 'http://catch-dev.harvardx.harvard.edu/catch-context.jsonld'
MIRADOR_CONTEXT_IRI = 'http://iiif.io/api/presentation/2/context.json'


WA_MANDATORY_PROPS = {
    # `schema_version`, `permissions`, `platform` not mandatory
    'anno': ['type',  'body', 'target', 'creator'],
    'body': ['type', 'items'],
    'body_items': ['type', 'purpose', 'value'],  # `format` not mandatory
    'target': ['type', 'items'],
    'target_items': ['type', 'source'],  # `format` not mandatory
    'creator': ['id', 'name'],
    'platform': ['name', 'contextId', 'collectionId', 'target_source_id'],
}
WA_NOT_FOR_CREATE_PROPS = {
    'anno': ['created', 'modified', 'creator', 'permissions'],
    'permissions': ['can_read', 'can_update', 'can_delete', 'can_admin'],
}

def validate_annotation_mandatory(wa):
    '''minimal validation, for generic web annotation.'''
    wa_id = wa.get('id', 'unknown')

    validate_anno_dict(WA_MANDATORY_PROPS, 'anno', wa, wa_id)
    validate_anno_dict(WA_MANDATORY_PROPS, 'creator', wa['creator'], wa_id)
    validate_anno_list_or_dict(WA_MANDATORY_PROPS, 'body', wa['body'], wa_id)
    validate_anno_list_or_dict(WA_MANDATORY_PROPS, 'target', wa['target'], wa_id)
    return wa

def validate_annotation_not_for_create(wa):
    '''it has to have `creator`, `created`, `modified`, `permissions`.'''
    wa_id = wa.get('id', 'unknown')

    validate_anno_dict(WA_NOT_FOR_CREATE_PROPS, 'anno', wa, wa_id)
    validate_anno_dict(WA_NOT_FOR_CREATE_PROPS, 'permissions', wa['permissions'], wa_id)
    return wa

def validate_annotation(wa):
    '''when creating, might not have `creator`, `created`, `modified`.'''
    validate_annotation_mandatory(wa)
    validate_annotation_not_for_create(wa)
    return wa


def validate_anno_dict(prop_set, prop, obj, wa_id):
    '''check for keys in dict.'''
    if not isinstance(obj, dict):
        raise InvalidPropertyTypeInInputAnnotation(
            'expected dict for {} in anno({}), found ({})'.format(
                prop, wa_id, type(obj)))

    for mandatory in prop_set[prop]:
        if mandatory not in obj:
            msg = 'expected ({}) in {} present in anno({})'.format(
                    mandatory, prop, wa_id)
            raise MissingPropertyInInputAnnotation(msg)
    return obj


def validate_anno_list_of_dicts(prop_set, prop, obj, wa_id):
    '''for props that have items list, like `body`, `target`, `selector`...'''
    if not isinstance(obj, list):
        raise InvalidPropertyTypeInInputAnnotation(
            'expected list for {}.items in anno({}), found ({})'.format(
                prop, wa_id, type(obj)))

    for it in obj:
        for mandatory in prop_set[prop]:
            if mandatory not in it:
                raise MissingPropertyInInputAnnotation(
                    'expected ({}) present in {}.items in anno({})'.format(
                        mandatory, prop, wa_id))
    return obj


def validate_anno_list_or_dict(prop_set, prop, obj, wa_id):
    if isinstance(obj, dict):
        validate_anno_dict(prop_set, prop, obj, wa_id)
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
        prop_set, '_'.join([prop, 'items']), obj['items'], wa_id)

    return obj


def expand_compact_for_context(wa, context):
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
        translated = jsonld.compact(expanded, context)
    except Exception as e:
        msg = 'translation for context({}) of anno({}) failed: {}'.format(
            CATCH_CONTEXT_IRI, wa['id'], str(e))
        raise e

    return translated


