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
    name = "package_extract/extract",
    srcs = [
        "package_extract/extract.py",
        "package_extract/extract_helper.py",
        "package_extract/extract_helper_package/__init__.py",
    ],
    data = ["package_extract/extract_helper_package/extract_dat.txt"],
    imports = ["package_extract"],
    main = "package_extract/extract.py",
    srcs_version = "PY2AND3",
    zip_safe = False,
)

par_binary(
    name = "package_import_roots/import_roots",
    srcs = ["package_import_roots/import_roots.py"],
    imports = ["package_import_roots"],
    main = "package_import_roots/import_roots.py",
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
    name = "package_pkg_resources/main",
    srcs = [
        "package_pkg_resources/main.py",
    ],
    data = [
        "@pypi__portpicker_1_2_0//:files",
        "@pypi__yapf_0_19_0//:files",
    ],
    main = "package_pkg_resources/main.py",
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
            path,
        ],
        data = [
            label,
        ],
    ),
    # Test .par file with harness
    sh_test(
        name = "%s_test" % name,
        size = "small",
        srcs = ["test_harness.sh"],
        args = [
            "--par",
            "%s.par" % path,
        ] + select({
            "subpar_test_python_version_3": ["%s_PY3_filelist.txt" % path],
            "//conditions:default": ["%s_PY2_filelist.txt" % path],
        }),
        data = [
            "%s.par" % label,
        ] + select({
            "subpar_test_python_version_3": ["%s_PY3_filelist.txt" % label],
            "//conditions:default": ["%s_PY2_filelist.txt" % label],
        }),
    ),
) for name, label, path in [
    ("basic", "//tests/package_a:a", "tests/package_a/a"),
    (
        "dir_shadowing",
        "//test_dir_shadowing:test_dir_shadowing_main",
        "test_dir_shadowing/test_dir_shadowing_main",
    ),
    ("direct_dependency", "//tests/package_b:b", "tests/package_b/b"),
    ("external_workspace", "//tests:package_e/e", "tests/package_e/e"),
    ("extract", "//tests:package_extract/extract", "tests/package_extract/extract"),
    ("import_root", "//tests:package_d/d", "tests/package_d/d"),
    (
        "import_roots",
        "//tests:package_import_roots/import_roots",
        "tests/package_import_roots/import_roots",
    ),
    ("indirect_dependency", "//tests:package_c/c", "tests/package_c/c"),
    ("main_boilerplate", "//tests:package_g/g", "tests/package_g/g"),
    ("pkg_resources", "//tests:package_pkg_resources/main", "tests/package_pkg_resources/main"),
    ("shadow", "//tests:package_shadow/main", "tests/package_shadow/main"),
    ("version", "//tests:package_f/f", "tests/package_f/f"),
]]

# Test target in external workspace
sh_test(
    name = "test_compiler_label_wrapper",
    srcs = ["test_compiler_label_wrapper.sh"],
    data = [
        "@test_workspace//:test_compiler_label.par",
    ],
)
