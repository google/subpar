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

# docs/ is a separate Bazel workspace from the rest of subpar
cd docs
bazel build //...

# Copy generated files back into source tree
unzip -d . -o bazel-bin/docs-md-skydoc.zip
unzip -d . -o bazel-bin/docs-html-skydoc.zip

# Skydoc puts the generated files in a subdir because of the separate
# workspaces.  Move the files back to docs/ and rewrite paths.
mv external/subpar/* .
rmdir external/subpar
rmdir external
perl -i -pe 's{./external/subpar/}{./}g' *.md *.html

# The symlinks in docs/bazel-* confuse Bazel, so we delete them after
# we're done.
bazel clean
