from django import template
import re

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


