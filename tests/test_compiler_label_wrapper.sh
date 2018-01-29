#!/bin/sh

set -eu

# Did the par file compile and run?
../test_workspace/test_compiler_label.par || exit 1

echo "Pass"
