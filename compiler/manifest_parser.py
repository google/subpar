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

"""Read Bazel manifest files.

The format is described in
https://github.com/bazelbuild/bazel/blob/master/src/main/tools/build-runfiles.cc

We assume manifest files are utf-8 encoded.

"""
import io

from subpar.compiler import error


def parse(manifest_filename):
    """Parse a Bazel manifest file.

    Args:
        manifest_filename: Path to file created by Bazel

    Returns:
        dictionary: key is stored_path, value is local_path.

    Data will be read from each `local_path` and stored in the
    zipfile under the corresponding `stored_path`.  local_paths
    may appear more than once, stored_paths may not. A
    local_path of None means a zero-length empty file.

    Raises:
        Error, IOError, SystemError

    """
    manifest = {}
    with io.open(manifest_filename, 'rt', encoding='utf8') as f:
        lineno = 0
        for line in f:
            # Split line into fields
            lineno += 1
            line = line.rstrip('\n')
            fields = line.split(' ')

            # Parse fields
            stored_path = fields[0]
            if len(fields) == 1 or (len(fields) == 2 and not fields[1]):
                # line like 'foo\n' or 'foo \n'
                local_path = None
            elif len(fields) == 2 and fields[1]:
                # line like 'foo bar\n'
                local_path = fields[1]
            else:
                raise error.Error('Syntax error at line %d in [%s]: %s' %
                                  (lineno, manifest_filename, repr(line)))

            # Ensure no collisions
            if stored_path in manifest:
                raise error.Error(
                    ('Configuration error at line %d in [%s]: file [%s] '
                     'specified more than once') %
                    (lineno, manifest_filename, stored_path))
            manifest[stored_path] = local_path
    return manifest
