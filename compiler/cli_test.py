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

import unittest

from subpar.compiler import cli
from subpar.compiler import error
from subpar.compiler import test_utils


class CliTest(unittest.TestCase):

    def test_make_command_line_parser(self):
        parser = cli.make_command_line_parser()
        args = parser.parse_args([
            '--imports_from_stub=quux',
            '--manifest_file=bar',
            '--manifest_root=bazz',
            '--outputpar=baz',
            'foo',
        ])
        self.assertEqual(args.manifest_file, 'bar')

    def test_parse_imports_from_stub(self):
        valid_cases = [
            ["  python_imports = ''",
             []],
            ["  python_imports = 'myworkspace/spam/eggs'",
             ['myworkspace/spam/eggs']],
            ["  python_imports = 'myworkspace/spam/eggs:otherworkspace'",
             ['myworkspace/spam/eggs', 'otherworkspace']],
        ]
        for content, expected in valid_cases:
            with test_utils.temp_file(content) as stub_file:
                actual = cli.parse_imports_from_stub(stub_file.name)
                self.assertEqual(actual, expected)

        invalid_cases = [
            '',
            '\n\n',
            '  python_imports=',
            ]
        for content in invalid_cases:
            with test_utils.temp_file(content) as stub_file:
                with self.assertRaises(error.Error):
                    cli.parse_imports_from_stub(stub_file.name)


if __name__ == '__main__':
    unittest.main()
