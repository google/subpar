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
            '--output_par=baz',
            '--stub_file=quux',
            '--zip_safe=False',
            '--import_root=root1',
            '--import_root=root2',
            'foo',
        ])
        self.assertEqual(args.manifest_file, 'bar')
        self.assertEqual(args.manifest_root, 'bazz')
        self.assertEqual(args.output_par, 'baz')
        self.assertEqual(args.stub_file, 'quux')
        self.assertEqual(args.zip_safe, False)
        self.assertEqual(args.import_roots, ['root1', 'root2'])
        self.assertEqual(args.main_filename, 'foo')

    def test_make_command_line_parser_for_interprerter(self):
        parser = cli.make_command_line_parser()
        args = parser.parse_args([
            '--manifest_file=bar',
            '--manifest_root=bazz',
            '--output_par=baz',
            '--stub_file=quux',
            '--zip_safe=False',
            '--interpreter=foobar',
            'foo',
        ])
        self.assertEqual(args.interpreter, 'foobar')

    def test_stub(self):
        valid_cases = [
            # Absolute path to interpreter
            [b"""
PYTHON_BINARY = '/usr/bin/python'
""",
             '/usr/bin/python'],
            # Search for interpreter on $PATH
            [b"""
PYTHON_BINARY = 'python'
""",
             '/usr/bin/env python'],
            # Default toolchain wrapped python3 interpreter
            [b"""
PYTHON_BINARY = 'bazel_tools/tools/python/py3wrapper.sh'
""",
             '/usr/bin/env python3'],
            # Default toolchain wrapped python2 interpreter
            [b"""
PYTHON_BINARY = 'bazel_tools/tools/python/py2wrapper.sh'
""",
             '/usr/bin/env python2'],
        ]
        for content, expected in valid_cases:
            with test_utils.temp_file(content) as stub_file:
                actual = cli.parse_stub(stub_file.name)
                self.assertEqual(actual, expected)

        invalid_cases = [
            # No interpreter
            b'',
            b'\n\n',
            # Relative interpreter path
            b"PYTHON_BINARY = 'mydir/python'",
            # Interpreter is label
            b"""
PYTHON_BINARY = '//mypackage:python'
""",
            ]
        for content in invalid_cases:
            with test_utils.temp_file(content) as stub_file:
                with self.assertRaises(error.Error):
                    cli.parse_stub(stub_file.name)


if __name__ == '__main__':
    unittest.main()
