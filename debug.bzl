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

def dump(obj, obj_name):
    """Debugging method that recursively prints object fields to stderr

    Args:
      obj: Object to dump
      obj_name: Name to print for that object

    Example Usage:
    ```
    load("debug", "dump")
    ...
    dump(ctx, "ctx")
    ```

    Example Output:
    ```
    WARNING: /code/rrrrr/subpar/debug.bzl:11:5:
    ctx[ctx]:
        action[string]: <getattr(action) failed>
        attr[struct]:
            _action_listener[list]: []
            _compiler[RuleConfiguredTarget]:
                data_runfiles[runfiles]:
    ```
    """

    s = '\n' + _dumpstr(obj, obj_name)
    print(s)

def _dumpstr(root_obj, root_obj_name):
    """Helper method for dump() to just generate the string

    Some fields always raise errors if we getattr() on them.  We
    manually blacklist them here.  Other fields raise errors only if
    we getattr() without a default.  Those are handled below.

    A bug was filed against Bazel, but it got fixed in a way that
    didn't actually fix this.

    """
    BLACKLIST = [
        "InputFileConfiguredTarget.output_group",
        "Label.Label",
        "Label.relative",
        "License.to_json",
        "RuleConfiguredTarget.output_group",
        "ctx.action",
        "ctx.check_placeholders",
        "ctx.empty_action",
        "ctx.expand",
        "ctx.expand_location",
        "ctx.expand_make_variables",
        "ctx.file_action",
        "ctx.middle_man",
        "ctx.new_file",
        "ctx.resolve_command",
        "ctx.rule",
        "ctx.runfiles",
        "ctx.template_action",
        "ctx.tokenize",
        "fragments.apple",
        "fragments.cpp",
        "fragments.java",
        "fragments.jvm",
        "fragments.objc",
        "runfiles.symlinks",
        "struct.output_licenses",
        "struct.to_json",
        "struct.to_proto",
    ]
    MAXLINES = 4000
    ROOT_MAXDEPTH = 5

    # List of printable lines
    lines = []

    # Bazel doesn't allow a function to recursively call itself, so
    # use an explicit stack
    stack = [(root_obj, root_obj_name, 0, ROOT_MAXDEPTH)]
    # No while() in Bazel, so use for loop over large range
    for _ in range(MAXLINES):
        if len(stack) == 0:
            break
        obj, obj_name, indent, maxdepth = stack.pop()

        obj_type = type(obj)
        indent_str = ' '*indent
        line = '{indent_str}{obj_name}[{obj_type}]:'.format(
            indent_str=indent_str, obj_name=obj_name, obj_type=obj_type)

        if maxdepth == 0 or obj_type in ['dict', 'list', 'set', 'string']:
            # Dump value as string, inline
            line += ' ' + str(obj)
        else:
            # Dump all of value's fields on separate lines
            attrs = dir(obj)
            # Push each field to stack in reverse order, so they pop
            # in sorted order
            for attr in reversed(attrs):
                if "%s.%s" % (obj_type, attr) in BLACKLIST:
                    value = '<blacklisted attr (%s)>' % attr
                else:
                    value = getattr(obj, attr, '<getattr(%s) failed>' % attr)
                stack.append((value, attr, indent+4, maxdepth-1))
        lines.append(line)
    return '\n'.join(lines)
