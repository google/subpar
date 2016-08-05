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
[par_binary(
    name = "package_c/c_%s" % version,
    srcs = ["package_c/c.py"],
    default_python_version = version,
    main = "package_c/c.py",
    srcs_version = "PY2AND3",
    deps = ["//tests/package_b:b_%s" % version],
) for version in [
    "PY2",
    "PY3",
]]

[par_binary(
    name = "package_d/d_%s" % version,
    srcs = ["package_d/d.py"],
    default_python_version = version,
    imports = [
        "package_b",
        "package_c",
    ],
    main = "package_d/d.py",
    srcs_version = "PY2AND3",
    deps = [
        "//tests:package_c/c_%s" % version,
        "//tests/package_b:b_%s" % version,
    ],
) for version in [
    "PY2",
    "PY3",
]]

[par_binary(
    name = "package_e/e_%s" % version,
    srcs = ["package_e/e.py"],
    data = [
        "@test_workspace//:data_file.txt",
    ],
    default_python_version = version,
    main = "package_e/e.py",
    srcs_version = "PY2AND3",
) for version in [
    "PY2",
    "PY3",
]]

par_binary(
    name = "package_f/f_PY2",
    srcs = ["package_f/f_PY2.py"],
)

par_binary(
    name = "package_f/f_PY3",
    srcs = ["package_f/f_PY3.py"],
    default_python_version = "PY3",
    srcs_version = "PY2AND3",
)

[par_binary(
    name = "package_g/g_%s" % version,
    srcs = ["package_g/g.py"],
    default_python_version = version,
    main = "package_g/g.py",
    srcs_version = "PY2AND3",
) for version in [
    "PY2",
    "PY3",
]]

# Test targets
[sh_test(
    name = "%s_%s" % (name, version),
    size = "small",
    srcs = ["test_harness.sh"],
    args = [
        "tests%s_%s.par" % (path, version),
        "tests%s_%s_filelist.txt" % (path, version),
    ],
    data = [
        "//tests%s_%s.par" % (label, version),
        "//tests%s_%s_filelist.txt" % (label, version),
    ],
) for name, label, path in [
    ("basic_test", "/package_a:a", "/package_a/a"),
    ("direct_dependency_test", "/package_b:b", "/package_b/b"),
    ("indirect_dependency_test", ":package_c/c", "/package_c/c"),
    ("import_root_test", ":package_d/d", "/package_d/d"),
    ("external_workspace_test", ":package_e/e", "/package_e/e"),
    ("version_test", ":package_f/f", "/package_f/f"),
    ("main_boilerplate_test", ":package_g/g", "/package_g/g"),
] for version in [
    "PY2",
    "PY3",
]]
