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

"""Common test utilities"""

import os
import tempfile


def get_test_tmpdir():
    """Get default test temp dir."""
    tmpdir = os.environ.get('TEST_TMPDIR', tempfile.gettempdir())
    return tmpdir


def mkdtemp():
    """mkdtemp wrapper that respects TEST_TMPDIR"""
    return tempfile.mkdtemp(dir=get_test_tmpdir())


def temp_file(contents, suffix=''):
    """Create a self-deleting temp file with the given content"""
    tmpdir = get_test_tmpdir()
    t = tempfile.NamedTemporaryFile(suffix=suffix, dir=tmpdir)
    t.write(contents)
    t.flush()
    return t
