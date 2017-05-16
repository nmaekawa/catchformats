"""formats from annotatorjs to catch webannotation.  """

import json
import sys

from .webannotation_validator import CATCH_CONTEXT_IRI
from .errors import MissingPropertyInAnnotatorJSInputError
from .errors import UnknownAnnotatorJSMediaTypeError


TEMP_ID = 'not_available'


def annojs_to_annotation(annojs):
    '''formats input `annojs` from annotatorjs into catch webannotation.

        TODO: reference to annotatorjs format
    '''
    try:
        media = annojs['media']
        target_source = str(annojs['uri'])
    except KeyError as e:
        raise MissingPropertyInAnnotatorJSInputError(
            'anno({}): expected property not found - {}'.format(
                anno_id, str(e)))

    anno_id = str(annojs['id']) if 'id' in annojs else TEMP_ID
    wa = {
        '@context': CATCH_CONTEXT_IRI,
        'id': anno_id,
        'type': 'Annotation',
        'schema_version': 'catch v1.0',
        'created': annojs['created'],
        'modified': annojs['updated'],
        'creator':  {
            'id': annojs['user']['id'],
            'name': annojs['user']['name'],
        },
        'permissions': {
            'can_read': annojs['permissions']['read'],
            'can_update': annojs['permissions']['update'],
            'can_delete': annojs['permissions']['delete'],
            'can_admin': annojs['permissions']['admin'],
        },
        'platform': {
            'platform_name': 'hxat v1.0',
            'context_id': annojs['contextId'] \
                    if 'contextId' in annojs else 'unknown',
            'collection_id': annojs['collectionId'] \
                    if 'collectionId' in annojs else 'unknown',
            'target_source_id': target_source,
        },
    }

    wa['body'] = format_body(anno_id, annojs)

    if media == 'comment':
        wa['target'] = format_target_reply(anno_id, annojs)
    elif media == 'text':
        wa['target'] = format_target_text(anno_id, annojs)
    elif media == 'video':
        wa['target'] = format_target_video(anno_id, annojs)
    elif media == 'image':
        wa['target'] = format_target_image(anno_id, annojs)
    else:
        raise UnknownAnnotatorJSMediaTypeError(
            'anno({}): unable to process media({})'.format(anno_id, media))

    if (len(wa['target']['items']) <= 0):
        raise MissingPropertyInAnnotatorJSInputError(
            'no targets in anno({}), expected 1 or more'.format(anno_id))

    if wa['id'] == TEMP_ID:
        del wa['id']  # wasn't present, originally, to-be-created anno?
    return wa


def format_body(anno_id, annojs):
    body_text = annojs['text'] if 'text' in annojs else ''
    body = {
        'type': 'List',
        'items': [{
            'type': 'TextualBody',
            'purpose': 'replying' \
                    if annojs['media'] == 'comment' else 'commenting',
            'value': body_text,
        }],
    }
    tags = annojs['tags'] if 'tags' in annojs else []
    for tag in tags:
        body['items'].append({
            'type': 'TextualBody',
            'purpose': 'tagging',
            'value': tag,
        })
    return body


def format_target_reply(anno_id, annojs):
    target = {'type': 'List', 'items': []}
    if 'parent' in annojs and str(annojs['parent']) != '0':
        target['items'].append({
            'type': 'Annotation',
            'format': 'text/html',
            'source': str(annojs['parent']),  #TODO: have to make it a url???
        })
    else:
        raise MissingPropertyInAnnotatorJSInputError((
            'anno({}): expected `parent` present and != 0 for '
            '`media = comment`').format(anno_id))
    return target


def format_target_text(anno_id, annojs):
    target = {
        'type': 'List',
        'items': [{
            'type': 'Text',
            'format': 'text/html',
            'source': str(annojs['uri']),
        }]}

    # can have multiple selectors, ex: non-consecutive parts of text!
    selector = {'type': 'List', 'items': []}
    try:
        ranges = annojs['ranges']
    except KeyError as e:
        raise MissingPropertyInAnnotatorJSInputError(
            'anno({}): expected `ranges` property for `text` media'.format(
                anno_id))
    for r in ranges:
        selector['items'].append({
            'type': 'RangeSelector',
            'startSelector': {'type':'XPathSelector', 'value': r['start']},
            'endSelector': {'type':'XPathSelector', 'value': r['end']},
            'refinedBy': [{
                'type': 'TextPositionSelector',
                'start': r['startOffset'],
                'end': r['endOffset'],
            }],
        })
    if 'quote' in annojs and annojs['quote']:
        if len(selector['items']) > 0:   # text with only quote? no ranges?
            selector['type'] = 'Choice'  # also, trusts that when quote and
                                         # ranges, then single range
        selector['items'].append(
            {'type': 'TextQuoteSelector', 'exact': annojs['quote']})

    if selector['items']:
        target['items'][0]['selector'] = selector

    return target


def format_target_video(anno_id, annojs):
    try:
        target = {
        'type': 'List',
        'items': [{
            'type': 'Video',
            'format': 'video/{}'.format(annojs['target']['ext'].lower()),
            'source': str(annojs['uri']),
            'selector': {
                'type': 'List',
                'items': [{
                    'type': 'FragmentSelector',
                    'conformsTo': 'http://www.w3.org/TR/media-frags/',
                    'value': 't={0},{1}'.format(
                        annojs['rangeTime']['start'], annojs['rangeTime']['end']),
                    'refinedBy': {
                        'type': 'CssSelector',
                        'value': '#{}'.format(annojs['target']['container'])},
                }]
            }
        }]
        }
    except KeyError as e:
        raise MissingPropertyInAnnotatorJSInputError(
            'anno({}): missing property in target_video({})'.format(
                anno_id, str(e)))
    return target


def format_target_image(anno_id, annojs):
    target = {'type': 'List', 'items': []}
    try:
        if isinstance(annojs['rangePosition'], list):
            rangePositionList = annojs['rangePosition']
        else:
            rangePositionList = [annojs['rangePosition']]
    except KeyError as e:
        raise MissingPropertyInAnnotatorJSInputError(
            'anno({}): missing rangePosition in  media="image"'.format(anno_id))

    selector = {'type': 'List', 'items': []}
    for pos in rangePositionList:
        if isinstance(pos, dict):
            # legacy strategy
            selector['items'].append(
                strategy_legacy_for_target_selector(annojs)
            )
        else:  # 2.1 strategy
            selector['items'].append(
                strategy_2_1_for_target_selector(annojs)
            )
        if len(selector['items']) > 1:
            selector['type'] = 'Choice'  # dual strategy

        target['items'].append({
                'type': 'Image',
                'source': str(annojs['uri']),
                'selector': selector
        })
        if 'thumb' in annojs and annojs['thumb']:
            target['items'].append({
                'type': 'Thumbnail',
                'source': str(annojs['thumb']),
                'format': 'image/jpg',  # guessing
            })
            target['type'] = 'Choice'

    return target


def strategy_legacy_for_target_selector(annojs):
    pos = annojs['rangePosition']
    value = 'xywh={},{},{},{}'.format(
            pos['x'], pos['y'], pos['width'], pos['height'])
    selector = {
        'type': 'FragmentSelector',
        'conformsTo': 'http://www.w3.org/TR/media-frags/',
        'value': value,
    }
    return selector


def strategy_2_1_for_target_selector(annojs):
    return {
        'type': 'SvgSelector',
        'value': annojs['rangePosition'],
    }
