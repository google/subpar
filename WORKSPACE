workspace(name = "subpar")

# These version vars aren't consumed by anything but are good to know for
# documentation / compatibility purposes.
#
# Because of use of `PyInfo` provider.
MIN_BAZEL_VERSION = "0.23.0"
# Because tests require --incompatible_use_python_toolchains.
MIN_BAZEL_VERSION_FOR_TESTS = "0.25.0"

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

# Not actually referenced anywhere, but must be marked as a separate
# repository so that things like "bazel test //..." don't get confused
# by the BUILD file in docs/.  This is a hack, and Bazel still gets
# confused by the docs/bazel-* symlinks.
local_repository(
    name = "docs",
    path = "docs",
)
