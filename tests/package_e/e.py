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

"""Integration test program E for Subpar.

Test dependencies on files in external repositories

"""

# This will fail with ImportError if __init__.py files are missing or
# in incorrect places.
from test_workspace.package_external_lib import external_lib


def main():
    print('In e.py main()')
    external_lib.lib()


if __name__ == '__main__':
    main()
