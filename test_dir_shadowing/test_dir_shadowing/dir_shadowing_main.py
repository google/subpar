# Copyright 2017 Google Inc. All Rights Reserved.
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

"""Integration test library for Subpar

Regression test for https://github.com/google/subpar/issues/47
"""

import pkgutil

from test_dir_shadowing import dir_shadowing_lib


def main():
    print('In dir_shadowing_main.py main()')
    dir_shadowing_lib.lib()
    # Test resource extraction
    dat = pkgutil.get_data('test_dir_shadowing', 'dir_shadowing_main_dat.txt')
    assert (dat == b'Dummy data file for dir_shadowing_main.py\n'), dat


if __name__ == '__main__':
    main()
