# -*- coding: utf-8 -*-
from rest_framework.parsers import JSONParser

from .conversion import dict_walk_json_to_python


class JSONToPythonParser(JSONParser):
    """Parses JSON-serialized data, using Python objects and conventions."""

    def parse(self, stream, media_type=None, parser_context=None):
        data = super(JSONToPythonParser, self).parse(stream, media_type=media_type, parser_context=parser_context)
        return dict_walk_json_to_python(data)
