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

echo "TEST_SRCDIR=${TEST_SRCDIR}"
echo "pwd is $(pwd)"
echo "PWD is ${PWD}"

function die { echo "$*" >&1; exit 1; }

[ -n "$TEST_SRCDIR" ] \
  || die 'FATAL: $TEST_SRCDIR not set in '$0' (run this test under Bazel)'
[ -n "$TEST_TMPDIR" ] \
  || die 'FATAL: $TEST_TMPDIR not set in '$0' (run this test under Bazel)'

if [ "$1" == "--par" ]; then
  PAR=1
  EXECUTABLE="$2"
  FILELIST="$3"
else
  PAR=0
  EXECUTABLE="$1"
  FILELIST=""
fi
TMP_EXECUTABLE="$TEST_TMPDIR"/$(basename "$EXECUTABLE")

# Compare list of files in zipfile with expected list
if [ "$PAR" -eq 1 ]; then
  # Exclude runfiles of the autodetecting toolchain. The test is still brittle
  # with respect to runfiles introduced by any other toolchain. When tests are
  # invoked by run_tests.sh, a custom toolchain with no runfiles is used.
  diff \
    <(unzip -l -q -q "$EXECUTABLE" | awk '{print $NF}' \
        | grep -v 'bazel_tools/tools/python/py.wrapper\.sh') \
    "$FILELIST" \
    || die 'FATAL: zipfile contents do not match expected'
fi

# Execute .par file in place
"$EXECUTABLE"

# Copy .par file to tmp dir so that .runfiles is not present and run again
if [ "$PAR" -eq 1 ]; then
  cp "$EXECUTABLE" "$TMP_EXECUTABLE"
  "$TMP_EXECUTABLE"
fi
