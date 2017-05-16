# -*- coding: utf-8 -*-


class CatchFormatsError(Exception):
    '''catch-all exception for CatchFormats.'''

class MissingPropertyInInputAnnotation(CatchFormatsError):
    '''mandatory property not present.'''

class InvalidPropertyTypeInInputAnnotation(CatchFormatsError):
    '''not the expected json type (ex: list instead of  object).'''

class UnsupportedJsonContextError(CatchFormatsError):
    '''wa context present, but unsupported.'''


class AnnotatorJSError(CatchFormatsError):
    '''error related to annotatorjs formatting.'''

class MissingPropertyInAnnotatorJSInputError(AnnotatorJSError):
    '''expected property not present in annotatorjs input.'''

class UnknownAnnotatorJSMediaTypeError(AnnotatorJSError):
    '''media type != comment, text, video, image.'''






