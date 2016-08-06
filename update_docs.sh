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

bazel build //docs/...
unzip -d docs/ -o bazel-bin/docs/docs-md-skydoc.zip
unzip -d docs/ -o bazel-bin/docs/docs-html-skydoc.zip
perl -i -pe 's|href="/css/main.css"|href="css/main.css"|' docs/*.html
