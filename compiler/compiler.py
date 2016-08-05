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

"""Main entry point for subpar compiler"""

import sys

from subpar.compiler import cli

if __name__ == '__main__':
    try:
        sys.exit(cli.main(sys.argv))
    except KeyboardInterrupt:
        # Don't print a stack trace, just exit silently
        sys.exit(1)
