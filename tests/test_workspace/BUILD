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

load("@rules_python//python:defs.bzl", "py_library")
load("@subpar//:subpar.bzl", "par_binary")

package(default_visibility = ["//visibility:public"])

exports_files(["data_file.txt"])

# Part of the tests:external_workspace test
py_library(
    name = "package_external_lib/external_lib",
    srcs = [
        # This intentionally DOES NOT have __init__.py listed
        "package_external_lib/external_lib.py",
    ],
    srcs_version = "PY2AND3",
)

# Test that we can actually compile a par_binary outside the subpar workspace.
par_binary(
    name = "test_compiler_label",
    srcs = ["test_compiler_label.py"],
    main = "test_compiler_label.py",
    srcs_version = "PY2AND3",
)
