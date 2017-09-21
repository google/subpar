workspace(name = "subpar")

# Used by integration tests
local_repository(
    name = "test_workspace",
    path = __workspace_dir__ + "/tests/test_workspace",
)

# Not actually referenced anywhere, but must be marked as a separate
# repository so that things like "bazel test //..." don't get confused
# by the BUILD file in docs/.  This is a hack, and Bazel still gets
# confused by the docs/bazel-* symlinks.
local_repository(
    name = "docs",
    path = "docs",
)
