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

"""Represent various types of content that can be stored in a .par file

See: http://www.pkware.com/documents/casestudies/APPNOTE.TXT

TODO: Timestamp normalization
TODO: Python source compilation
TODO: ELF binary stripping
"""

import os


class StoredResource(object):
    """A local resource which can be committed to a par file.

    Args:
        stored_filename: Relative path to store content under
    """

    def __init__(self, stored_filename):
        assert not os.path.isabs(stored_filename)
        self.stored_filename = stored_filename

    def store(self, unused_zip_file):
        """Write resource to zip file"""
        raise NotImplementedError


class StoredFile(StoredResource):
    """One file that will be stored in the final archive."""

    def __init__(self, stored_filename, local_filename):
        StoredResource.__init__(self, stored_filename)
        self.local_filename = local_filename

    def store(self, zip_file):
        zip_file.write(self.local_filename, self.stored_filename)


class StoredContent(StoredResource):
    """Literal byte string to store in a par file."""

    def __init__(self, stored_filename, content):
        StoredResource.__init__(self, stored_filename)
        self.content = content

    def store(self, zip_file):
        zip_file.writestr(self.stored_filename, self.content)


class EmptyFile(StoredContent):
    """An empty file included in the par file, usually an __init__.py file."""

    def __init__(self, stored_filename):
        StoredContent.__init__(self, stored_filename, b'')
