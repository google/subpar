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

"""Integration test program A for Subpar.

Test a variety of difficult or erroneous import scenarios.

"""

import pkgutil
import sys

# Import some things in various ways
import subpar
from subpar import tests as tests1
import subpar.tests as tests2    # noqa
assert tests1 is tests2, (tests1, tests2)

# Test importing __main__ under its package qualified name.
#
# Check that we handle it the same way Python does (i.e. poorly)
if __name__ == '__main__':
    imported_qualified_a = False
    # pylint: disable=reimported,import-self
    import subpar.tests.package_a.a
    assert imported_qualified_a
    assert subpar.tests.package_a.a is not sys.modules['__main__']
else:
    # We are maybe inside recusive import
    assert __name__ == 'subpar.tests.package_a.a', __name__
    assert sys.modules.get(__name__) is not None
    # Tell __main__ that we got here
    if hasattr(sys.modules['__main__'], 'imported_qualified_a'):
        sys.modules['__main__'].imported_qualified_a = True

    # Import parent package
    import subpar.tests.package_a
    from .. import package_a
    assert subpar.tests.package_a is package_a

    # Containing package doesn't have a reference to this module yet
    assert (not hasattr(package_a, 'a')), package_a

    # Test that neither of these work, because we're in the middle of
    # importing 'subpar.tests.package_a.a', so the module object for
    # 'subpar.tests.package_a' doesn't have a variable called 'a' yet.
    try:
        # pylint: disable=import-self
        from . import a as a1
        # This was fixed in Python 3.5
        if (sys.version_info.major, sys.version_info.minor) < (3, 5):
            raise AssertionError('This shouldn\'t have worked: %r' % a1)
    except ImportError as e:
        assert 'cannot import name' in str(e), e
    try:
        # pylint: disable=import-self
        import subpar.tests.package_a.a as a2
        raise AssertionError('This shouldn\'t have worked: %r' % a2)
    except AttributeError as e:
        assert "has no attribute 'a'" in str(e), e


def main():
    print('In a.py main()')
    # Test resource extraction
    a_dat = pkgutil.get_data('subpar.tests.package_a', 'a_dat.txt')
    assert (a_dat == b'Dummy data file for a.py\n'), a_dat


if __name__ == '__main__':
    main()
