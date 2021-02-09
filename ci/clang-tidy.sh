#!/bin/bash

# Find the merge base compared to master.
base=$(git merge-base refs/remotes/origin/main HEAD)
# Create an empty array that will contain all the filepaths of files modified.
modified_filepaths=()

# To properly handle file names with spaces, we have to do some bash magic.
# We set the Internal Field Separator to nothing and read line by line.
while IFS='' read -r line
do
  # For each line of the git output, we call `realpath` to get the absolute path of the file.
  absolute_filepath=$(realpath "$line")
  extension=${absolute_filepath##*.}
  [ "$extension" != "cc" ] && continue

  # Append the absolute filepath.
  modified_filepaths+=("$absolute_filepath")

# `git diff-tree` outputs all the files that differ between the different commits.
# By specifying `--diff-filter=d`, it doesn't report deleted files.
done < <(git diff-tree --no-commit-id --diff-filter=d --name-only -r "$base" HEAD)

[ -z "${modified_filepaths}" ] && { echo "no files modified"; exit 0; }

topdir=$(readlink -f `dirname $0`/..)
build_dir=${topdir}/build
mkdir -p ${build_dir} && cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ${build_dir}

git diff -r --no-commit-id --diff-filter=d ${base}..HEAD > diff
cat diff | clang-tidy-diff -p1 -path ${build_dir} -export-fixes clang-tidy-output -- -Wall

reponame=$(basename `git rev-parse --show-toplevel`)
env > env.out
#${topdir}/ci/generate-output.py

