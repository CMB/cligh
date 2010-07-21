#!/usr/bin/python
# Repository-related commands.

from cligh.utils import read_user_input

def cmd_repo_create(client, args):
	"""Create a new repository."""

	def validate_description(text):
		if len(text) == 0:
			print 'Description may not be empty.  Try again.'
			return False
		return True

	def validate_name(text):
		if len(text) == 0:
			print 'Name may not be empty.  Try again.'
			return False
		if any(char for char in text if char.isspace()):
			print 'Name may not contain spaces.  Try again.'
			return False
		# What other characters don't belong in the name?
		return True

	def validate_homepage(text):
		# This is a lame excuse for validation.
		if len(text) == 0:
			print 'Home page may not be empty.  Try again.'
			return False
		return True

	name = read_user_input('Repository name', validate_name)
	homepage = read_user_input('Homepage', validate_homepage)
	description = read_user_input('Description', validate_description)
	print client.repos.create(name, description, homepage)

def cmd_repo_fork(client, args):
	"""Fork a repository."""
	print client.repos.fork(args.repository)

def cmd_repo_list(client, args):
	"""Command to list the repos for a given user."""
	repos = client.repos.list(args.user)
	print '%s has the following repositories:' % args.user
	print 'Name - Description'
	for repo in repos:
		print '%s - %s' % (repo.name, repo.description)
