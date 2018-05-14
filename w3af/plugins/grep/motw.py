"""'
motw.py

Copyright 2007 Sharad Ganapathy

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
try:
    import re2 as re
except ImportError:
    import re
else:
    re.set_fallback_notification(re.FALLBACK_WARNING)

import w3af.core.controllers.output_manager as om
import w3af.core.data.kb.knowledge_base as kb

from w3af.core.controllers.plugins.grep_plugin import GrepPlugin
from w3af.core.controllers.core_helpers.fingerprint_404 import is_404
from w3af.core.data.kb.info import Info


class motw(GrepPlugin):
    """
    Identify whether the page is compliant to mark of the web.
    :author: Sharad Ganapathy sharadgana |at| gmail.com
    """
    def __init__(self):
        GrepPlugin.__init__(self)

        # The following regex matches a valid url as well as the text
        # about:internet. Also it validates the number in the parenthesis.
        # It should be a 4 digit number and must tell about the length of the
        # URL that follows
        regex = r"""<!--\s*saved from url=\(([\d]{4})\)(https?://([-\w\.]+)"""
        regex += r"""+(:\d+)?(/([\w/_\.]*(\?\S+)?)?)?|about:internet)\s{1}\-\->"""
        self._motw_re = re.compile(regex)

    def grep(self, request, response):
        """
        Plugin entry point, search for motw.

        :param request: The HTTP request object.
        :param response: The HTTP response object
        :return: None
        """
        if not response.is_text_or_html():
            return
        
        if is_404(response):
            return
        
        motw_match = self._motw_re.search(response.get_body())

        # Act based on finding/non-finding
        if motw_match:

            # This int() can't fail because the regex validated
            # the data before
            url_length_indicated = int(motw_match.group(1))
            url_length_actual = len(motw_match.group(2))
            
            if (url_length_indicated <= url_length_actual):
                desc = 'The URL: "%s" contains a valid mark of the web.'
                desc = desc % response.get_url()
                i = self.create_info(desc, response, motw_match)

            else:
                desc = 'The URL: "%s" will be executed in Local Machine'\
                       ' Zone security context because the indicated length'\
                       ' is greater than the actual URL length.'
                desc = desc % response.get_url() 
                i = self.create_info(desc, response, motw_match)
                i['local_machine'] = True
                
            kb.kb.append(self, 'motw', i)

    def create_info(self, desc, response, motw_match):
        i = Info('Mark of the web', desc, response.id, self.get_name())
        i.set_url(response.get_url())
        i.add_to_highlight(motw_match.group(0))
        return i

    def end(self):
        """
        This method is called when the plugin wont be used anymore.
        """
        # Print the results to the user
        pretty_msg = {}
        pretty_msg['motw'] = 'The following URLs contain a MOTW:'
        for motw_type in pretty_msg:
            inform = []
            for i in kb.kb.get('motw', motw_type):
                inform.append(i)

            if len(inform):
                om.out.information(pretty_msg[motw_type])
                for i in inform:
                    if 'local_machine' not in i:
                        om.out.information('- %s' % i.get_url())
                    else:
                        msg = '- %s [Executed in Local machine context]'
                        om.out.information(msg % i.get_url())

    def get_long_desc(self):
        """
        :return: A DETAILED description of the plugin functions and features.
        """
        return """
        This plugin will specify whether the page is compliant against the MOTW
        standard. The standard is explained in:
            - http://msdn2.microsoft.com/en-us/library/ms537628.aspx

        This plugin tests if the length of the URL specified by "(XYZW)" is
        lower, equal or greater than the length of the URL; and also reports the
        existence of this tag in the body of all analyzed pages.

        One configurable parameter exists:
            - withoutMOTW

        If "withoutMOTW" is enabled, the plugin will show all URLs that don't
        contain a MOTW.
        """
