import json
from pyld import jsonld

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

class MissingPropertyInInputAnnotation(Exception):
    '''mandatory property not present.'''

class InvalidPropertyTypeInInputAnnotation(Exception):
    '''not the expected json type (ex: list instead of  object).'''

class UnsupportedJsonContextError(Exception):
    '''wa context present, but unsupported.'''


def validate_annotation(wa):
    if '@context' not in wa:
        raise MissingJsonLdContextError()

    if wa['@context'] == MIRADOR_CONTEXT_IRI:
        if 'id' in wa:
            wa_id = wa['id']
        else:
            wa_id = 'unknown'

        trans = expand_compact(wa)
        assert trans is not None

        validate_anno_props('anno', trans, wa_id)
        validate_anno_props('creator', trans['creator'], wa_id)
        validate_anno_props('permissions', trans['permissions'], wa_id)
        validate_anno_props('body', trans['body'], wa_id)
        validate_anno_prop_items('body_items', trans['body']['items'], wa_id)
        validate_anno_props('target', trans['target'], wa_id)
        validate_anno_prop_items('target_items', trans['target']['items'], wa_id)

        return trans

    elif wa['@context'] == CATCH_CONTEXT_IRI:  # it's catch webanno
        if 'id' in wa:
            wa_id = wa['id']
        else:
            wa_id = 'unknown'

        validate_anno_props('anno', wa, wa_id)
        validate_anno_props('creator', wa['creator'], wa_id)
        validate_anno_props('permissions', wa['permissions'], wa_id)
        validate_anno_props('body', wa['body'], wa_id)
        validate_anno_prop_items('body_items', wa['body']['items'], wa_id)
        validate_anno_props('target', wa['target'], wa_id)
        validate_anno_prop_items('target_items', wa['target']['items'], wa_id)

        return wa

    else:
        # different context flavor
        raise UnsupportedJsonLDContextError(
            'do not undenstand context({})'.format(wa['@context']))


def validate_anno_props(prop, obj, wa_id):
    '''check for keys in dict.'''
    print('prop: {}, keys: {}'.format(prop, obj.keys()))
    for mandatory in WA_MANDATORY_PROPS[prop]:
        if mandatory not in obj:
            msg = 'expected ({}) in {} present in anno({})'.format(
                    mandatory, prop, wa_id)
            raise MissingPropertyInInputAnnotation(msg)
    return obj


def validate_anno_prop_items(prop, obj, wa_id):
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


