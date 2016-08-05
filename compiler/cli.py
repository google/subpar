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

"""Command line interface to subpar compiler"""

import argparse
import io
import os
import re

from subpar.compiler import error
from subpar.compiler import python_archive


def make_command_line_parser():
    """Return an object that can parse this program's command line"""
    parser = argparse.ArgumentParser(
        description='Subpar Python Executable Builder')

    parser.add_argument(
        'main_filename',
        help='Python source file to use as main entry point')

    parser.add_argument(
        '--manifest_file',
        help='File listing all files to be included in this parfile. This is ' +
        'typically generated by bazel in a target\'s .runfiles_manifest file.',
        required=True)
    parser.add_argument(
        '--manifest_root',
        help='Root directory of all relative paths in manifest file.',
        default=os.getcwd())
    parser.add_argument(
        '--outputpar',
        help='Filename of generated par file.',
        required=True)
    parser.add_argument(
        '--stub_file',
        help='Read imports and interpreter path from the specified stub file',
        required=True)
    return parser


def parse_stub(stub_filename):
    """Parse the imports and interpreter path from a py_binary() stub.

    We assume the stub is utf-8 encoded.

    TODO(b/29227737): Remove this once we can access imports from skylark.

    Returns (list of relative paths, path to Python interpreter)
    """
    imports_regex = re.compile(r'''^  python_imports = '([^']*)'$''')
    interpreter_regex = re.compile(r'''^PYTHON_BINARY = '([^']*)'$''')
    import_roots = None
    interpreter = None
    with io.open(stub_filename, 'rt', encoding='utf8') as stub_file:
        for line in stub_file:
            importers_match = imports_regex.match(line)
            if importers_match:
                import_roots = importers_match.group(1).split(':')
                # Filter out empty paths
                import_roots = [x for x in import_roots if x]
            interpreter_match = interpreter_regex.match(line)
            if interpreter_match:
                interpreter = interpreter_match.group(1)
    if import_roots is None or not interpreter:
        raise error.Error('Failed to parse stub file [%s]' % stub_filename)

    # Match the search logic in stub_template.txt
    if interpreter.startswith('//'):
        raise error.Error('Python interpreter must not be a label [%s]' %
                          stub_filename)
    elif interpreter.startswith('/'):
        pass
    elif '/' in interpreter:
        pass
    else:
        interpreter = '/usr/bin/env %s' % interpreter

    return (import_roots, interpreter)


def main(argv):
    """Command line interface to Subpar"""
    parser = make_command_line_parser()
    args = parser.parse_args(argv[1:])

    # Parse information from stub file that's too hard to compute in Skylark
    import_roots, interpreter = parse_stub(args.stub_file)

    par = python_archive.PythonArchive(
        main_filename=args.main_filename,
        import_roots=import_roots,
        interpreter=interpreter,
        output_filename=args.outputpar,
        manifest_filename=args.manifest_file,
        manifest_root=args.manifest_root,
    )
    par.create()
