# Integration tests for Subpar.
#
# The package_a/ and package_b/ subdirectories which are separate
# Bazel packages.  The other directories are separate Python packages
# but not separate Bazel packages.

package(default_visibility = ["//tests:__subpackages__"])

load("//:subpar.bzl", "par_binary")

# Utility targets
sh_library(
    name = "test_harness",
    srcs = ["test_harness.sh"],
)

# Targets used by tests below
par_binary(
    name = "package_c/c",
    srcs = ["package_c/c.py"],
    deps = ["//tests/package_b:b"],
)

par_binary(
    name = "package_d/d",
    srcs = ["package_d/d.py"],
    imports = [
        "package_b",
        "package_c",
    ],
    deps = [
        "//tests:package_c/c",
        "//tests/package_b:b",
    ],
)

par_binary(
    name = "package_e/e",
    srcs = ["package_e/e.py"],
    data = [
        "@test_workspace//:data_file.txt",
    ],
)

# Test targets
sh_test(
    name = "basic_test",
    size = "small",
    srcs = ["test_harness.sh"],
    args = [
        "tests/package_a/a.par",
        "tests/package_a/a_filelist.txt",
    ],
    data = [
        "//tests/package_a:a.par",
        "//tests/package_a:a_filelist.txt",
    ],
)

sh_test(
    name = "direct_dependency_test",
    size = "small",
    srcs = ["test_harness.sh"],
    args = [
        "tests/package_b/b.par",
        "tests/package_b/b_filelist.txt",
    ],
    data = [
        "//tests/package_b:b.par",
        "//tests/package_b:b_filelist.txt",
    ],
)

sh_test(
    name = "indirect_dependency_test",
    size = "small",
    srcs = ["test_harness.sh"],
    args = [
        "tests/package_c/c.par",
        "tests/package_c/c_filelist.txt",
    ],
    data = [
        "//tests:package_c/c.par",
        "//tests:package_c/c_filelist.txt",
    ],
)

sh_test(
    name = "import_root_test",
    size = "small",
    srcs = ["test_harness.sh"],
    args = [
        "tests/package_d/d.par",
        "tests/package_d/d_filelist.txt",
    ],
    data = [
        "//tests:package_d/d.par",
        "//tests:package_d/d_filelist.txt",
    ],
)

sh_test(
    name = "external_workspace_test",
    size = "small",
    srcs = ["test_harness.sh"],
    args = [
        "tests/package_e/e.par",
        "tests/package_e/e_filelist.txt",
    ],
    data = [
        "//tests:package_e/e.par",
        "//tests:package_e/e_filelist.txt",
    ],
)
