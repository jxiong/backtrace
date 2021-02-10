#!/usr/bin/env python3

import argparse
import os
import re
import yaml
from github import Github

class PostComment(object):
    def __init__(self, reponame, prid, topdir, diff, clang_tidy_output):
        self.reponame = reponame
        self.prid = prid
        self.topdir = topdir
        self.diff_file = diff
        self.clang_tidy_output = clang_tidy_output

        github = Github(os.getenv('TOKEN'))
        repo = github.get_repo(self.reponame)

        self.pull_request = repo.get_pull(prid)
        commits = self.pull_request.get_commits()
        self.commit = commits[0]

        self.lines_by_file = {}

    def handle_patch(self):
        filename = None
        for line in self.diff_file.readlines():
            match = re.search('^\+\+\+\ \"?(.*?/){1}([^ \t\n\"]*)', line)
            if match:
                filename = match.group(2)
            if filename is None:
                continue
    
            if not re.match('^.*\.(cpp|cc|c\+\+|cxx|c|cl|h|hpp|m|mm|inc)$', filename, re.IGNORECASE):
                continue
    
            match = re.search('^@@.*\+(\d+)(,(\d+))?', line)
            if match:
                start_line = int(match.group(1))
                line_count = 1
                if match.group(3):
                    line_count = int(match.group(3))
                if line_count == 0:
                    continue
                end_line = start_line + line_count - 1
                self.lines_by_file.setdefault(filename, []).append([start_line, end_line])

    def offset2line(self, srcfile, offset):
        line = 1
        with open(srcfile, "r") as fd:
            pos = 0
            while pos < offset:
                byte = fd.read(1)
                if byte == '':
                    break
                if byte == '\n':
                    line += 1
                pos += 1
            if pos != offset:
                raise RuntimeError("Offset is greater than file length")
        return line

    def post_comment(self, filename, line, message, diagname, pos):
        print("Post a comment to {} at {}, with message {} and [{}]".format(filename, line, message, diagname))

        self.pull_request.create_review_comment("[{}]: {}".format(diagname, message), self.commit,  filename, pos)

    def run(self):
        self.handle_patch()
        data = yaml.load(self.clang_tidy_output, Loader=yaml.CLoader)
        for diag in data["Diagnostics"]:
            filepath = diag["DiagnosticMessage"]["FilePath"]
            if not filepath.startswith(self.topdir):
                continue

            offset = diag["DiagnosticMessage"]["FileOffset"]
            message = diag["DiagnosticMessage"]["Message"]
            diagname = diag["DiagnosticName"]

            '''
            for note in diag["Notes"]:
                if not note["FilePath"].startswith(self.topdir):
                    continue
                filename = note["FilePath"]
                offset = note["FileOffset"]
            '''

            line = self.offset2line(filepath, offset)
            filename = filepath.split(self.topdir)[1].strip('/')
            if not filename in self.lines_by_file.keys():
                continue

            for lines in self.lines_by_file[filename]:
                if line > lines[0] and line < lines[1]:
                    self.post_comment(filename, offset, message, diagname, line - lines[0] + 2)
                    break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="post comment to github by clang tidy warning")
    parser.add_argument("--repo", help="specify repo name", required=True)
    parser.add_argument("--pr", help="specify pull request", type=int, required=True)
    parser.add_argument("--srcdir", help="directory of this repository", type=str, required=True)
    parser.add_argument("--diff", help="location of diff file", type=open, required=True)
    parser.add_argument("--tidy", help="tidy output", type=open, required=True)
    args = parser.parse_args()

    pc = PostComment(args.repo, args.pr, args.srcdir, args.diff, args.tidy)
    pc.run()
