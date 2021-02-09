#!/usr/bin/env python3

import yaml
from github import Github

def offset2line(srcfile, offset):
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

def post_comment(filename, line, message, diagname):
	print("Post a comment to {} at {}, with message {} and [{}]".format(filename, line, message, diagname))

	g = Github("2e29c5c9c3431c58b9be50042490586fdb440db5")
	repo = g.get_repo("jxiong/backtrace")
	pr = repo.get_pull(5)
	commits = pr.get_commits()
	pr.create_review_comment("{} [{}]".format(message, diagname), commits[1],  filename, 3)

def main(gitdir, clang_tidy_output):
	with open("output") as f:
		data = yaml.load(f, Loader=yaml.CLoader)
		for diag in data["Diagnostics"]:
			message = diag["DiagnosticMessage"]["Message"]
			diagname = diag["DiagnosticName"]
			for note in diag["Notes"]:
				if not note["FilePath"].startswith(gitdir):
					continue
				filename = note["FilePath"]
				offset = note["FileOffset"]
			post_comment(filename.split(gitdir)[1], offset2line(filename, offset), message, diagname)

if __name__ == '__main__':
	main("/home/jxiong/srcs/backtrace/", "output")
