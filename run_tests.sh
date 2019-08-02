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

# This sets up the toolchain hook to run tests for the given version of Python
# whose interpreter is located at the given absolute path.
#
# $1 may be either "PY2" or "PY3". If it is PY2, then the Python 2 runtime is
# set to the path in $2, and the Python 3 runtime is set to the default value
# given by $PYTHON3. If $1 is PY3, then $2 is the Python 3 runtime and the
# Python 2 runtime is given by $PYTHON2.
#
# The PYVER constant is also set to $1. It is consumed at loading time by
# //tests:BUILD.
#
# Note that even though tests are only run for one version of Python at a time,
# we still need to provide both runtimes in the toolchain for the sake of
# tools. In particular, the par compiler itself requires PY2, even if the par
# that we are compiling uses PY3.
function set_toolchain_hook {
  pyver=$1
  if [ $pyver == "PY3" ]; then
    py2_path="$PYTHON2"
    py3_path="$2"
  else
    py2_path="$2"
    py3_path="$PYTHON3"
  fi

  cat > toolchain_test_hook.bzl << EOF
load("@rules_python//python:defs.bzl", "py_runtime", "py_runtime_pair")

PYVER = "$pyver"

def define_toolchain_for_testing():
    py_runtime(
        name = "py2_runtime",
        interpreter_path = "$py2_path",
        python_version = "PY2",
    )

    py_runtime(
        name = "py3_runtime",
        interpreter_path = "$py3_path",
        python_version = "PY3",
    )

    py_runtime_pair(
        name = "runtime_pair_for_testing",
        py2_runtime = ":py2_runtime",
        py3_runtime = ":py3_runtime",
        visibility = ["//visibility:public"],
    )

    native.toolchain(
        name = "toolchain_for_testing",
        toolchain = ":runtime_pair_for_testing",
        toolchain_type = "@bazel_tools//tools/python:toolchain_type",
        visibility = ["//visibility:public"],
    )
EOF
}

# Clear the toolchain hook back to its original no-op contents.
#
# If the test exits abnormally and this function isn't run, we may be left with
# a modified version of this file in our source tree.
function clear_toolchain_hook {
  cat > toolchain_test_hook.bzl << EOF
PYVER = "PY3"

def define_toolchain_for_testing():
    pass
EOF
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

# Must have both Python interpreters to test.
if [ -z "${PYTHON2}" ]; then
  die "Could not find Python 2 on $PATH"
fi
if [ -z "${PYTHON3}" ]; then
  die "Could not find Python 3 on $PATH"
fi

# Must be able to locate toolchain_test_hook.bzl. This will fail if cwd is not
# the root of the subpar workspace.
if [ ! -f "toolchain_test_hook.bzl" ]; then
  die "Could not locate toolchain_test_hook.bzl (are we in the workspace root?)"
fi

# Run test matrix
for PYTHON_INTERPRETER in "${PYTHON2}" "${PYTHON3}"; do
  if [ -z "${PYTHON_INTERPRETER}" ] ; then
    continue;
  fi

  BAZEL_TEST="bazel test --test_output=errors \
--incompatible_use_python_toolchains \
--extra_toolchains=//tests:toolchain_for_testing"
  if [ "${PYTHON_INTERPRETER}" = "${PYTHON3}" ]; then
    PYVER="PY3"
  else
    PYVER="PY2"
  fi

  echo "Testing ${PYTHON_INTERPRETER}"
  bazel clean
  set_toolchain_hook "$PYVER" "$PYTHON_INTERPRETER"
  ${BAZEL_TEST} //...

  if [ -n "${VIRTUALENV}" ]; then
    echo "Testing bare virtualenv"
    rm -rf "${VIRTUALENVDIR}"
    "${VIRTUALENV}" \
      -p "${PYTHON_INTERPRETER}" \
      --no-setuptools --no-pip --no-wheel \
      "${VIRTUALENVDIR}"
    source "${VIRTUALENVDIR}"/bin/activate
    bazel clean
    set_toolchain_hook $PYVER $(which python)
    ${BAZEL_TEST} //...
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
      set_toolchain_hook $PYVER $(which python)
      ${BAZEL_TEST} //...
      deactivate
    done
  fi
done

clear_toolchain_hook
