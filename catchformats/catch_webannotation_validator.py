
from jsonschema import validate

from .annotatorjs_formatter import annojs_to_annotation
from .errors import  CatchFormatsError
from .errors import  AnnotatorJSError
from .webannotation_validator import expand_compact_for_context
from .webannotation_validator import validate_annotation
from .webannotation_schema import CATCH_WEBANNOTATION_SCHEMA


def validate_catch_webannotation(wa):
    if '@context' in wa:
        try:
            norm = expand_compact_for_context(wa, CATCH_CONTEXT_IRI)
        except Exception as e:
            # try to do more relaxed validation
            try:
                norm = validate_annotation(wa)
            except Exception as e:
                # TODO: log more meaninful message!
                raise CatchFormatsError('cannot format compact webannotation')

    else:  # no context, try annotatorjs
        try:
            norm = annojs_to_annotation(wa)
        except Exception as e:
            raise AnnotatorJSError('cannot format into AnnotatorJS')

    # by now we have a webannotation
    try:
        validate(norm, CATCH_WEBANNOTATION_SCHEMA)
    except Exception as e:
        raise CatchFormatsError('unable to validate input annotatation.')
    return norm

