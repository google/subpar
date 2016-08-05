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

"""Integration test program B for Subpar

Test direct dependency on test program A and test library A.
"""

import pkgutil

# Test package import from another package
from subpar.tests.package_a import a
from subpar.tests.package_a import a_lib


def main():
    a.main()
    a_lib.lib()
    print('In b.py main()')
    # Test resource extraction
    b_dat = pkgutil.get_data('subpar.tests.package_b', 'b_dat.txt')
    assert (b_dat == b'Dummy data file for b.py\n'), b_dat


if __name__ == '__main__':
    main()
