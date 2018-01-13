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

import argparse
import unittest

from subpar.compiler import cli
from subpar.compiler import error
from subpar.compiler import test_utils


class CliTest(unittest.TestCase):

    def test_bool_from_string(self):
        self.assertIs(cli.bool_from_string('True'), True)
        self.assertIs(cli.bool_from_string('False'), False)
        with self.assertRaises(argparse.ArgumentTypeError):
            cli.bool_from_string('')
        with self.assertRaises(argparse.ArgumentTypeError):
            cli.bool_from_string('Yes')

    def test_make_command_line_parser(self):
        parser = cli.make_command_line_parser()
        args = parser.parse_args([
            '--manifest_file=bar',
            '--manifest_root=bazz',
            '--outputpar=baz',
            '--stub_file=quux',
            '--zip_safe=False',
            'foo',
        ])
        self.assertEqual(args.manifest_file, 'bar')

    def test_stub(self):
        valid_cases = [
            # Empty list
            [b"""
  python_imports = ''
PYTHON_BINARY = '/usr/bin/python'
""",
             ([], '/usr/bin/python')],
            # Single import
            [b"""
  python_imports = 'myworkspace/spam/eggs'
PYTHON_BINARY = '/usr/bin/python'
""",
             (['myworkspace/spam/eggs'], '/usr/bin/python')],
            # Multiple imports
            [b"""
  python_imports = 'myworkspace/spam/eggs:otherworkspace'
PYTHON_BINARY = '/usr/bin/python'
""",
             (['myworkspace/spam/eggs', 'otherworkspace'], '/usr/bin/python')],
            # Relative path to interpreter
            [b"""
  python_imports = ''
PYTHON_BINARY = 'mydir/python'
""",
             ([], 'mydir/python')],
            # Search for interpreter on $PATH
            [b"""
  python_imports = ''
PYTHON_BINARY = 'python'
""",
             ([], '/usr/bin/env python')],
        ]
        for content, expected in valid_cases:
            with test_utils.temp_file(content) as stub_file:
                actual = cli.parse_stub(stub_file.name)
                self.assertEqual(actual, expected)

        invalid_cases = [
            b'',
            b'\n\n',
            # No interpreter
            b"  python_imports = 'myworkspace/spam/eggs'",
            # No imports
            b"PYTHON_BINARY = 'python'\n",
            # Interpreter is label
            b"""
  python_imports = ''
PYTHON_BINARY = '//mypackage:python'
""",
            ]
        for content in invalid_cases:
            with test_utils.temp_file(content) as stub_file:
                with self.assertRaises(error.Error):
                    cli.parse_stub(stub_file.name)


if __name__ == '__main__':
    unittest.main()
