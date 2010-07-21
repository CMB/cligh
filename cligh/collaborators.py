#!/usr/bin/python
# Commands for managing collaborators.

from cligh.utils import get_repository_name, remove_username

def cmd_collab_add(client, args):
	"""Add a collaborator to a repo."""
	repository = get_repository_name(args.repository)
	repository = remove_username(repository)
	print client.repos.add_collaborator(repository, args.user)

def cmd_collab_remove(client, args):
	"""Remove a collaborator from a repo."""
	repository = get_repository_name(args.repository)
	repository = remove_username(repository)
	print client.repos.remove_collaborator(repository, args.user)

def cmd_collab_list(client, args):
	"""List a repository's collaborators."""
	repository = get_repository_name(args.repository)
	collaborators = client.repos.list_collaborators(repository)
	if not collaborators:
		print 'There are no collaborators for %s.' % repository
	else:
		print 'The following people are collaborating on %s:' % \
			repository
		for collaborator in collaborators:
			print collaborator
