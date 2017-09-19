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

# Configurations
config_setting(
    name = "subpar_test_python_version_2",
    define_values = {
        "subpar_test_python_version": "2",
    },
)

config_setting(
    name = "subpar_test_python_version_3",
    define_values = {
        "subpar_test_python_version": "3",
    },
)

# Utility targets
sh_library(
    name = "test_harness",
    srcs = ["test_harness.sh"],
)

# Targets used by tests below
par_binary(
    name = "package_c/c",
    srcs = ["package_c/c.py"],
    main = "package_c/c.py",
    srcs_version = "PY2AND3",
    deps = ["//tests/package_b:b"],
)

par_binary(
    name = "package_d/d",
    srcs = ["package_d/d.py"],
    imports = [
        "package_b",
        "package_c",
    ],
    main = "package_d/d.py",
    srcs_version = "PY2AND3",
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
    main = "package_e/e.py",
    srcs_version = "PY2AND3",
    deps = [
        "@test_workspace//:package_external_lib/external_lib",
    ],
)

par_binary(
    name = "package_f/f",
    srcs = select({
        "subpar_test_python_version_3": ["package_f/f_PY3.py"],
        "//conditions:default": ["package_f/f_PY2.py"],
    }),
    main = select({
        "subpar_test_python_version_3": "package_f/f_PY3.py",
        "//conditions:default": "package_f/f_PY2.py",
    }),
)

par_binary(
    name = "package_g/g",
    srcs = ["package_g/g.py"],
    main = "package_g/g.py",
    srcs_version = "PY2AND3",
)

par_binary(
    name = "package_shadow/main",
    srcs = [
        "package_shadow/code/__init__.py",
        "package_shadow/code/shadowed.py",
        "package_shadow/main.py",
    ],
    imports = ["package_shadow"],
    main = "package_shadow/main.py",
    srcs_version = "PY2AND3",
)

par_binary(
    name = "package_import_roots/import_roots",
    srcs = [
        "package_import_roots/import_roots.py",
    ],
    imports = ["package_import_roots"],
    main = "package_import_roots/import_roots.py",
    srcs_version = "PY2AND3",
)

# Test targets
[(
    # Run test without .par file as a control
    sh_test(
        name = "%s_nopar_test" % name,
        size = "small",
        srcs = ["test_harness.sh"],
        args = [
            "tests%s" % path,
        ],
        data = [
            "//tests%s" % label,
        ],
    ),
    # Test .par file with harness
    sh_test(
        name = "%s_test" % name,
        size = "small",
        srcs = ["test_harness.sh"],
        args = [
            "--par",
            "tests%s.par" % path,
        ] + select({
            "subpar_test_python_version_3": ["tests%s_PY3_filelist.txt" % path],
            "//conditions:default": ["tests%s_PY2_filelist.txt" % path],
        }),
        data = [
            "//tests%s.par" % label,
        ] + select({
            "subpar_test_python_version_3": ["//tests%s_PY3_filelist.txt" % label],
            "//conditions:default": ["//tests%s_PY2_filelist.txt" % label],
        }),
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
]]
