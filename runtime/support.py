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

"""Runtime support code for executables created by Subpar.

1. Third-party modules require some PYTHONPATH manipulation.

2. Python can natively import python modules from a zip archive, but
   C extension modules require some help.

3. Resources stored in a .par file may need to be exposed as OS-level
   files instead of Python File objects.

We try a succession of different strategies until we find one that
works.

TODO: Strategy: FUSE filesystem
TODO: Strategy: dlopen_with_offset
TODO: Strategy: extract all files to a temp dir
TODO: Strategy: Do nothing if archive doesn't have any C extension modules

"""

import os
import sys
import warnings


def _log(msg):
    """Print a debugging message in the same format as python -vv output"""
    if sys.flags.verbose:
        sys.stderr.write(msg)
        sys.stderr.write('\n')


def _find_archive():
    """Find the path to the currently executing .par file"""
    main = sys.modules.get('__main__')
    if not main:
        _log('# __main__ module not found')
        return None
    main_file = getattr(main, '__file__', None)
    if not main_file:
        _log('# __main__.__file__ not set')
        return None
    archive_path = os.path.dirname(main_file)
    if archive_path == '':
        _log('# unexpected __main__.__file__ is %s' % main_file)
        return None
    return archive_path


def setup(import_roots=None):
    """Initialize subpar run-time support"""
    # Add third-party library entries to sys.path
    archive_path = _find_archive()
    if not archive_path:
        warnings.warn('Failed to initialize .par file runtime support',
                      ImportWarning)
        return

    # We try to match to order of Bazel's stub
    for import_root in reversed(import_roots or []):
        new_path = os.path.join(archive_path, import_root)
        _log('# adding %s to sys.path' % new_path)
        sys.path.insert(1, new_path)
