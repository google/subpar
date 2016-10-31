# Integration tests for Subpar.
#
# The package_a/ and package_b/ subdirectories which are separate
# Bazel packages.  The other directories are separate Python packages
# but not separate Bazel packages.

package(default_visibility = ["//tests:__subpackages__"])

exports_files([
    "__init__.py",
])

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
    deps = [
        "@test_workspace//:package_external_lib/external_lib",
    ],
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

[par_binary(
    name = "package_shadow/main_%s" % version,
    srcs = [
        "package_shadow/code/__init__.py",
        "package_shadow/code/shadowed.py",
        "package_shadow/main.py",
    ],
    default_python_version = version,
    imports = ["package_shadow"],
    main = "package_shadow/main.py",
    srcs_version = "PY2AND3",
) for version in [
    "PY2",
    "PY3",
]]

[par_binary(
    name = "package_import_roots/import_roots_%s" % version,
    srcs = [
        "package_import_roots/import_roots.py",
    ],
    default_python_version = version,
    imports = ["package_import_roots"],
    main = "package_import_roots/import_roots.py",
    srcs_version = "PY2AND3",
) for version in [
    "PY2",
    "PY3",
]]

# Test targets
[(
    # Run test without .par file as a control
    sh_test(
        name = "%s_%s_nopar_test" % (name, version),
        size = "small",
        srcs = ["test_harness.sh"],
        args = [
            "tests%s_%s" % (path, version),
        ],
        data = [
            "//tests%s_%s" % (label, version),
        ],
    ),
    # Test .par file with harness
    sh_test(
        name = "%s_%s_test" % (name, version),
        size = "small",
        srcs = ["test_harness.sh"],
        args = [
            "--par",
            "tests%s_%s.par" % (path, version),
            "tests%s_%s_filelist.txt" % (path, version),
        ],
        data = [
            "//tests%s_%s.par" % (label, version),
            "//tests%s_%s_filelist.txt" % (label, version),
        ],
    ),
) for name, label, path in [
    ("basic", "/package_a:a", "/package_a/a"),
    ("direct_dependency", "/package_b:b", "/package_b/b"),
    ("indirect_dependency", ":package_c/c", "/package_c/c"),
    ("import_root", ":package_d/d", "/package_d/d"),
    ("external_workspace", ":package_e/e", "/package_e/e"),
    ("version", ":package_f/f", "/package_f/f"),
    ("main_boilerplate", ":package_g/g", "/package_g/g"),
    ("shadow", ":package_shadow/main", "/package_shadow/main"),
    ("import_roots", ":package_import_roots/import_roots", "/package_import_roots/import_roots"),
] for version in [
    "PY2",
    "PY3",
]]
