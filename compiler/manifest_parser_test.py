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

import unittest

from subpar.compiler import error
from subpar.compiler import manifest_parser
from subpar.compiler import test_utils


class ManifestTest(unittest.TestCase):

    def test_parse_manifest_valid(self):
        valid = (
            # 1 field, no trailing space
            b'ccccc/__init__.py\n' +
            # 1 field, trailing space
            b'ccccc/ddddd/__init__.py \n' +
            # 2 fields
            b'ccccc/ddddd/eeeee /code/rrrrr/ccccc/ddddd/eeeee\n'
        )
        expected = {
            'ccccc/__init__.py': None,
            'ccccc/ddddd/__init__.py': None,
            'ccccc/ddddd/eeeee': '/code/rrrrr/ccccc/ddddd/eeeee',
        }
        with test_utils.temp_file(valid) as t:
            manifest = manifest_parser.parse(t.name)
            self.assertEqual(manifest, expected)

    def test_parse_manifest_invalid(self):
        invalids = [
            # Repeated name
            (b'ccccc/__init__.py \n' +
             b'ccccc/ddddd/__init__.py \n' +
             b'ccccc/__init__.py \n'),
            # Too many spaces
            b'ccccc/__init__.py foo bar\n',
            # Not enough spaces
            b'\n\n',
        ]
        for invalid in invalids:
            with test_utils.temp_file(invalid) as t:
                with self.assertRaises(error.Error):
                    manifest_parser.parse(t.name)


if __name__ == '__main__':
    unittest.main()
