#!/usr/bin/python2

# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import StringIO
import sys
import unittest

from subpar.runtime import support


class SupportTest(unittest.TestCase):

    def test_log(self):
        old_stderr = sys.stderr
        try:
            mock_stderr = StringIO.StringIO()
            sys.stderr = mock_stderr
            # pylint: disable=protected-access,no-self-use
            support._log("Test Log Message")
            if sys.flags.verbose:
                expected = "Test Log Message\n"
            else:
                expected = ""
            self.assertEqual(mock_stderr.getvalue(), expected)
        finally:
            sys.stderr = old_stderr

    def test_find_archive(self):
        # pylint: disable=protected-access
        path = support._find_archive()
        self.assertNotEqual(path, None)

    def test_setup(self):
        support.setup(import_roots=['some_root'])
        last_entry = sys.path[-1]
        self.assertTrue(last_entry.endswith('subpar/runtime/some_root'))


if __name__ == '__main__':
    unittest.main()
