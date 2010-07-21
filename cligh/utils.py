#!/usr/bin/python
import re
import subprocess
import sys

# Helper functions.
def print_error(message):
	"""Display an error message."""
	sys.stderr.write(message)

def die(message):
	"""Terminate, displaying an error message."""
	print_error(message)
	sys.exit(1)

def read_git_config(key):
	"""Read a value from git's configuration files."""
	cmd = ['git', 'config']
	cmd.append(key)
	output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()
	return output[0].strip()

def get_username_and_token():
	"""Get the github username and API token."""
	username = read_git_config('github.user')
	if not username:
		die("""Error: unable to determine your github username.
Please make sure that it is included in the configuration file ~/.gitconfig.
""")

	token = read_git_config('github.token')
	if not token:
		die("""Error: unable to determine your github API token.
Please make sure that it is included in the configuration file ~/.gitconfig.
""")
	return (username, token)

def read_user_input(prompt, validator_func):
	"""Read and validate user input."""
	user_text = ''
	valid_input = False
	while not valid_input:
		sys.stdout.write('%s: ' % prompt)
		sys.stdout.flush()
		user_text = sys.stdin.readline()
		if not user_text:
			die('Could not read input from the user; unable to proceed.')
		user_text = user_text[0:-1] # Snip off the newline.
		if validator_func(user_text):
			valid_input = True
	return user_text

def get_repository_name(name):
	"""Get the name of the repository to work on.
Either we return the "name" argument (if it is a non-empty string), or
we try to detect the repository's name by looking at remote.origin.url."""

	if not name:
		name = read_git_config('remote.origin.url')
		match = re.match(r'git@github.com:(.*)\.git$', name)
		if not match:
			die(
"""This command expects a repository name, but the name is unknown.
There are two ways to indicate a repository.
First, you can supply the --repository argument on the command line.
If no --repository argument is specified, and the current directory is
within a clone of a project hosted on github, then the name of the repository
is detected automatically.  In order for this auto-detection to work,
the remote named "origin" must point to github.
""")

		name = match.group(1)
	return name

def remove_username(repository):
	"""Return the name of the repository, without the username.
Effectively a no-op if the repo name is not of the form username/project."""
	nameparts = repository.split('/', 1)
	if len(nameparts) == 1:
		return nameparts[0]
	else:
		return nameparts[1]
