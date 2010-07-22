#!/usr/bin/python
# Repository-related commands.

from cligh.utils import read_user_input

def create(client, args):
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

def fork(client, args):
	"""Fork a repository."""
	print client.repos.fork(args.repository)

def do_list(client, args):
	"""Command to list the repos for a given user."""
	repos = client.repos.list(args.user)
	print '%s has the following repositories:' % args.user
	print 'Name - Description'
	for repo in repos:
		print '%s - %s' % (repo.name, repo.description)

def make_repo_parser(subparsers):
	repo = subparsers.add_parser('repo', help='Manage and query repositories.')
	subparsers = repo.add_subparsers(title='Repository-related Subcommands')
	repo_list = subparsers.add_parser('list', help='List repositories belonging to a given user.')
	repo_list.set_defaults(func=do_list)
	repo_list.add_argument('user')
	repo_create = subparsers.add_parser('create', help='Create a new repository.')
	repo_create.set_defaults(func=create)
	repo_fork = subparsers.add_parser('fork', help='Fork an existing repository.')
	repo_fork.set_defaults(func=fork)
	repo_fork.add_argument('repository', help='Name of the repository, in the form USERNAME/REPONAME')
