workspace(name = "subpar")

# Used by integration tests
local_repository(
    name = "test_workspace",
    path = "tests/test_workspace",
)
local_repository(
    name = "pypi__portpicker_1_2_0",
    path = "third_party/pypi__portpicker_1_2_0",
)
local_repository(
    name = "pypi__yapf_0_19_0",
    path = "third_party/pypi__yapf_0_19_0",
)

git_repository(
    name = "io_bazel_rules_python",
    remote = "https://github.com/bazelbuild/rules_python.git",
    commit = "e003509e52a116f6431883f6a77115ec0d1a323f",
)

load("@io_bazel_rules_python//python:pip.bzl", "pip_repositories")

pip_repositories()

load("@io_bazel_rules_python//python:pip.bzl", "pip_import")

pip_import(
   name = "runtime_test_deps",
   requirements = "//runtime:requirements.txt",
)

load("@runtime_test_deps//:requirements.bzl", "pip_install")
pip_install()

# Not actually referenced anywhere, but must be marked as a separate
# repository so that things like "bazel test //..." don't get confused
# by the BUILD file in docs/.  This is a hack, and Bazel still gets
# confused by the docs/bazel-* symlinks.
local_repository(
    name = "docs",
    path = "docs",
)
