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

function die {
  echo "$*" 1>&2
  exit 1
}

# Find various tools in environment
PYTHON2=$(which python||true)
if [ -z "${PYTHON2}" ]; then
  PYTHON2=$(which python2)
fi

# Make sure 'python' is actually Python 2.  Some distributions
# incorrectly have 'python' as Python 3.
#
# See PEP 394: The "python" Command on Unix-Like Systems
#   https://www.python.org/dev/peps/pep-0394/
if [ -n "${PYTHON2}" ]; then
  VERSION=$("${PYTHON2}" -V 2>&1)
  if ! expr "${VERSION}" : "Python 2." >/dev/null ; then
    PYTHON2=
  fi
fi

PYTHON3=$(which python3||true)

VIRTUALENV=$(which virtualenv) || die "virtualenv not installed"
VIRTUALENVDIR=$(dirname $0)/.env
# Virtualenv `activate` needs $PS1 set
PS1='$ '

# Must have at least one Python interpreter to test
if [ -z "${PYTHON2}" -a -z "${PYTHON3}" ]; then
  die "Could not find Python 2 or 3 interpreter on $PATH"
fi

# Run test matrix
for PYTHON_INTERPRETER in "${PYTHON2}" "${PYTHON3}"; do
  if [ -z "${PYTHON_INTERPRETER}" ] ; then
    continue;
  fi

  if [ "${PYTHON_INTERPRETER}" = "${PYTHON3}" ]; then
    BAZEL_TEST="bazel test --define subpar_test_python_version=3"
  else
    BAZEL_TEST="bazel test"
  fi

  echo "Testing ${PYTHON_INTERPRETER}"
  bazel clean
  ${BAZEL_TEST} --python_path="${PYTHON_INTERPRETER}" --test_output=errors //...

  if [ -n "${VIRTUALENV}" ]; then
    echo "Testing bare virtualenv"
    rm -rf "${VIRTUALENVDIR}"
    "${VIRTUALENV}" \
      -p "${PYTHON_INTERPRETER}" \
      --no-setuptools --no-pip --no-wheel \
      "${VIRTUALENVDIR}"
    source "${VIRTUALENVDIR}"/bin/activate
    bazel clean
    ${BAZEL_TEST} --python_path=$(which python) --test_output=errors //...
    deactivate

    for REQUIREMENTS in tests/requirements-test-*.txt; do
      echo "Testing virtualenv ${REQUIREMENTS}"
      rm -rf "${VIRTUALENVDIR}"
      "${VIRTUALENV}" \
        -p "${PYTHON_INTERPRETER}" \
        "${VIRTUALENVDIR}"
      source "${VIRTUALENVDIR}"/bin/activate
      pip install -r "${REQUIREMENTS}"
      bazel clean
      ${BAZEL_TEST} --python_path=$(which python) --test_output=errors //...
      deactivate
    done
  fi
done
