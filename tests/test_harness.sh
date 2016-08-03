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

ZIPFILE="$1"
FILELIST="$2"
TMP_ZIPFILE="$TEST_TMPDIR"/$(basename "$ZIPFILE")

# Compare list of files in zipfile with expected list
diff \
  <(unzip -l "$ZIPFILE" | awk '{print $NF}' | head -n -2 | tail -n +4) \
  "$FILELIST" \
  || die 'FATAL: zipfile contents do not match expected'

# Execute .par file in place
"$ZIPFILE"

# Copy .par file to tmp dir so that .runfiles is not present and run again
cp "$ZIPFILE" "$TMP_ZIPFILE"
"$TMP_ZIPFILE"
