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

"""Integration test program for Subpar.

Test that pkg_resources correctly identifies distribution packages
inside a .par file.
"""


def main():
    print('In pkg_resources test main()')
    try:
        import pkg_resources
    except ImportError:
        print('Skipping test, pkg_resources module is not available')
        return

    ws = pkg_resources.working_set

    # Informational for debugging
    distributions = list(ws)
    print('Resources found: %s' % distributions)

    # Check for the packages we provided metadata for.  There will
    # also be metadata for whatever other packages happen to be
    # installed in the current Python interpreter.
    for spec in ['portpicker==1.2.0', 'yapf==0.19.0']:
        dist = ws.find(pkg_resources.Requirement.parse(spec))
        assert dist, (spec, distributions)


if __name__ == '__main__':
    main()
