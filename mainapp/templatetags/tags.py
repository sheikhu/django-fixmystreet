from django import template
import re
import json
import settings
from django.conf import settings


register = template.Library()

MENU_DEFS = { 'submit' : { 'exact': [ '/','/reports/new', '/reports/' ], 
                           'match' : [],
                           'startswith':[],  
                           'exclude' : []
                         },
              'view' : { 'exact': [],
                         'match' : ['/wards/\d+', '/reports/\d+' ],
                         'startswith' : ['/cities','/wards'],
                         'exclude':[] 
                        }
            }

def is_match( path, pattern ):
    if MENU_DEFS.has_key(pattern):
        menudef = MENU_DEFS[pattern]
        if path in menudef[ 'exact' ]:
            return True
        for match in menudef['startswith']:
            if path.startswith(match) and not path in menudef['exclude']:
                return True
        for match in menudef['match']:
            if re.match(match,path):
                return True
        return False 
    if pattern in path:
        return True
    return False
    
@register.simple_tag
def fmsmenu_active(request, pattern ):
    if is_match(request.path, pattern ):
        return 'active'
    return ''

@register.simple_tag
def map_scripts():
    return '''
    <script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js"></script>
    <script src="%(media)sOpenLayers-2.11/OpenLayers.js"></script>
    <script src="%(media)sjs/fixmystreetmap.js"></script>
    ''' % {'media':settings.MEDIA_URL}

@register.simple_tag
def addthis_scripts():
    return '<script src="http://s7.addthis.com/js/250/addthis_widget.js?pub=' + settings.ADD_THIS_KEY + '"></script>'

@register.simple_tag
def report_to_json(report):
    return json.dumps(report_to_array(report))

def report_to_array(report):
    return {
        "id": report.id,
        "point": {
                "x": report.point.x,
                "y": report.point.y,
        },
        "is_fixed":report.is_fixed
    }
