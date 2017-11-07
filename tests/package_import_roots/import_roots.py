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

"""Integration test program for Subpar

Test that sys.path in a .par file has the same items as the Bazel stub.

Given a runfiles that looks like this:

    foo.runfiles/
        __main__/
            foo.py
        other_workspace/
            bar.py

or

    foo.runfiles/
        my_workspace/
            foo.py
        other_workspace/
            bar.py

The best way to import bar is by being explicit:

    == foo.py ==
    from other_workspace import bar

But Bazel sets up the path so that this also works:

    == foo.py ==
    import bar.py  # Don't do this

This is problematic for the import ambiguity and shadowing issues it
introduces.  But .par files also allow this behavior for consistency's
sake.

"""


def main():
    # This import only works if sys.path contains the 'subpar' directory
    import tests.package_import_roots
    assert tests.package_import_roots is not None
    print('In import_roots.py main()')


if __name__ == '__main__':
    main()
