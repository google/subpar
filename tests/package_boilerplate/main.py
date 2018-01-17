#!/usr/bin/env python3
# -*- coding: latin-1

# Test module docstring before boilerplate insertion
"""Integration test program for Subpar.

Test bootstrap interaction with __future__ imports and source file encodings.
"""

# Test __future__ imports
from __future__ import print_function


# Test the source file encoding specification above.  See PEP 263 for
# details.  In the line below, this source file contains a byte
# sequence that is valid latin-1 but not valid utf-8.  Specifically,
# between the two single quotes is a single byte 0xE4 (latin-1
# encoding of LATIN SMALL LETTER A WITH DIAERESIS), and _not_ the
# two-byte UTF-8 sequence 0xC3 0xA4.
latin_1_bytes = u'ä'
assert len(latin_1_bytes) == 1
assert ord(latin_1_bytes[0]) == 0xE4
