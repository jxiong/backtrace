#!/usr/bin/env python3

import argparse
import os
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
				pos = pos + 1
			if pos != offset:
				raise RuntimeError("Offset is greater than file length")
		return line

	def post_comment(self, filename, line, message, diagname):
		print("Post a comment to {} at {}, with message {} and [{}]".format(filename, line, message, diagname))

		self.pull_request.create_review_comment("{} [{}]".format(message, diagname), self.commit,  filename, 3)

	def run(self):
		data = yaml.load(self.clang_tidy_output, Loader=yaml.CLoader)
		for diag in data["Diagnostics"]:
			message = diag["DiagnosticMessage"]["Message"]
			diagname = diag["DiagnosticName"]
			for note in diag["Notes"]:
				if not note["FilePath"].startswith(self.topdir):
					continue
				filename = note["FilePath"]
				offset = note["FileOffset"]

			relative_filename = filename.split(self.topdir)[1].strip('/')
			offset = self.offset2line(filename, offset)
			self.post_comment(relative_filename, offset, message, diagname)

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
