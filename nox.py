# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import nox


@nox.session
def lint(session):
    # Flake8 under Python2 dies with a UnicodeDecodeError:
    # https://gitlab.com/pycqa/flake8/issues/324
    session.interpreter = 'python3'
    session.install('flake8', 'flake8-import-order')
    session.run(
        'flake8',
        '.',
    )
