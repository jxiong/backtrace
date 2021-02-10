#!/bin/bash

topdir=$(readlink -f `dirname $0`/..)
build_dir=${topdir}/build
mkdir -p ${build_dir} && cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -B ${build_dir}

base=$(git merge-base refs/remotes/origin/main HEAD)
git diff -r --no-commit-id --diff-filter=d ${base}..HEAD > diff
cat diff | clang-tidy-diff -p1 -checks='*' -path ${build_dir} -export-fixes clang-tidy-output -- -Wall

reponame=$(basename `git rev-parse --show-toplevel`)
env > env.out
echo "PR: ${CHANGE_ID} REPO: `basename ${GIT_URL} .git`"
${topdir}/ci/generate-output.py --repo jxiong/backtrace --srcdir $(realpath .) --diff diff --tidy clang-tidy-output --pr ${CHANGE_ID}
