try:
    import re2 as re
except ImportError:
    import re
else:
    re.set_fallback_notification(re.FALLBACK_WARNING)

#URL_RE = ('((http|https):[A-Za-z0-9/](([A-Za-z0-9$_.+!*(),;/?:@&~=-])|%'
#    '[A-Fa-f0-9]{2})+(#([a-zA-Z0-9][a-zA-Z0-9$_.+!*(),;/?:@&~=%-]*))?)')
URL_RE = re.compile('((http|https)://([\w:@\-\./]*?)[^ \0\n\r\t"\'<>]*)', re.U)

RELATIVE_URL_RE = re.compile(
    '((:?[/]{1,2}[\w\-~\.%]+)+\.\w{2,4}(((\?)([\w\-~\.%]*=[\w\-~\.%]*)){1}'
    '((&)([\w\-~\.%]*=[\w\-~\.%]*))*)?)', re.U)