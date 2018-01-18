# Copyright 2018 Google Inc. All Rights Reserved.
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

"""Integration test program for Subpar

Tests file extraction functionality (zip_safe=False)
"""

import os
import pkgutil
import sys


def main():
    print('In extract.py main()')

    # Test that imports are from real files on disk.  Slightly tricky
    # to test, since the 'subpar' package is imported before we
    # extract and setup sys.path, so we can't "import subpar.test.something"
    import extract_helper
    assert os.path.isfile(extract_helper.__file__), (
        extract_helper.__file__, sys.path)
    import extract_helper_package
    assert os.path.isfile(extract_helper_package.__file__), (
        extract_helper_package.__file__, sys.path)

    # Test resource extraction
    dat = pkgutil.get_data('extract_helper_package', 'extract_dat.txt')
    assert (dat == b'Dummy data file for extract.py\n'), dat


if __name__ == '__main__':
    main()
