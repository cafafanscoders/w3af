"""
xunit.py

Copyright 2012 Andres Riancho

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
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
"""
try:
    import re2 as re
except ImportError:
    import re
else:
    re.set_fallback_notification(re.FALLBACK_WARNING)

import xunitparser

from nose.tools import nottest


def parse_xunit(fname):
    """
    :param fname: The filename which contains the xunit results generated by
                  nosetests (when running tests or collecting them).
    """
    ts, tr = xunitparser.parse(open(fname))
    return ts, tr


@nottest
def normalize_test_names(test_suite):
    """
    Tests which are generated on the fly have names like:
        foo.bar.spam(<foo.bar.spam instance at 0x837d680>,)
        
    Because of the on the fly generation, the 0x837d680 changes each time you
    collect/run the test. We don't want that, and don't care about the address
    so we replace them with 0xfffffff
    
    :param test_suite: As returned by xunitparser.parse
    """
    for test in test_suite._tests:
        test.methodname = re.sub('0x(.*?)>', '0xfffffff>', test.methodname)
