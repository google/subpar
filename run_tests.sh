#!/bin/bash

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

set -euo pipefail

PYTHON2=$(which python)
if [ -z "${PYTHON2}" ]; then
  PYTHON2=$(which python2)
fi
PYTHON3=$(which python3)

# Make sure 'python' is actually Python 2.  Some distributions
# incorrectly have 'python' as Python 3.
#
# See PEP 394: The "python" Command on Unix-Like Systems
#   https://www.python.org/dev/peps/pep-0394/
if [ -n "${PYTHON2}" ]; then
  VERSION=$("${PYTHON2}" -V 2>&1)
  if ! expr match "${VERSION}" "Python 2." >/dev/null ; then
    PYTHON2=
  fi
fi

# Must have at least one Python interpreter to test
if [ -z "${PYTHON2}" -a -z "${PYTHON3}" ]; then
  echo "ERROR: Could not find Python 2 or 3 interpreter on $PATH" 1>&2
  exit 1
fi

# Run tests
if [ -n "${PYTHON2}" ]; then
  echo "Found Python 2 at ${PYTHON2}"
  bazel test --define subpar_test_python_version=2 --python_path="${PYTHON2}" --test_output=errors //...
fi

if [ -n "${PYTHON3}" ]; then
  echo "Found Python 3 at ${PYTHON3}"
  bazel test --define subpar_test_python_version=3 --python_path="${PYTHON3}" --test_output=errors //...
fi
