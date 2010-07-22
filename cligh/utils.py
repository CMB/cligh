#!/usr/bin/python
import os
import os.path
import re
import subprocess
import sys
import tempfile

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

def find_executable(executable):
	path = os.environ['PATH'].split(os.pathsep)
	for subdirectory in path:
		tryname = os.path.join(subdirectory, executable)
		if os.access(tryname, os.X_OK):
			return tryname
	return None

def choose_editor():
	if os.environ.has_key('EDITOR'):
		editor =  os.environ['EDITOR']
	else:
		print_error('$EDITOR not set, assuming default of vi.')
		editor = find_executable('vi')
	if not editor:
		die(
"""Error: cannot continue with the current command, because the text
editor could not be found.  Please set your EDITOR environment variable
to the pathname of your preferred editor.
""")
	return editor

def text_from_editor(original_text=''):
	"""Allow a user to compose a text using his editor of choice."""
	text = ''
	editor_cmd = choose_editor()
	my_tempfile = None
	try:
		my_tempfile = tempfile.NamedTemporaryFile(delete=False)
		if original_text:
			my_tempfile.write(original_text)
			my_tempfile.flush()
			my_tempfile.seek(0) # And go back to the beginning.
		editor_status = subprocess.call([editor_cmd, my_tempfile.name])
		if editor_status != 0:
			die(
"""Error: the text editor did not complete successfully.  Unable to continue.
""")
		text = my_tempfile.read()
	finally:
		if my_tempfile:
			my_tempfile.close()
			os.unlink(my_tempfile.name)
	return text

