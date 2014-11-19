# -*- coding: utf-8 -*-
from rest_framework.renderers import JSONRenderer

from .conversion import dict_walk_python_to_json


class PythonToJSONRenderer(JSONRenderer):
    """Renderer which serializes to JSON, using JSON conventions."""

    def render(self, data, *args, **kwargs):
        prepared_data = dict_walk_python_to_json(data)
        return super(PythonToJSONRenderer, self).render(prepared_data, *args, **kwargs)
