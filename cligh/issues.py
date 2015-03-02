"""Commands for managing and querying issues."""

from github import GithubException
from cligh.utils import text_from_editor, get_working_repo, die

# Helper functions:
def get_working_issue(client, args):
	"""Get an object corresponding to the issue
that the user wishes to manipulate.  Issues are identified by
a repository name and issue number."""
	issue = None
	repository = get_working_repo(client, args.repository)
	try:
		issue_number = int(args.number)
	except ValueError:
		die("""%s is not a valid issue number.""")
	try:
		issue = repository.get_issue(issue_number)
	except GithubException as e:
		die('Unable to fetch issue number %d for this repository: %s' % (issue_number, e.data['message']))
	return issue

def print_enclosed_text(text):
	"""Print some text, enclosed by horizontal lines."""
	print('-' * 80)
	print(text)
	print('-' * 80)
	print()

def print_comment(comment):
	print('Comment by %s on %s at %s' % (comment.user.login,
		comment.created_at.date(),
		comment.created_at.strftime('%H:%M:%S')))
	print_enclosed_text(comment.body)

def do_open(client, args):
	"""Create a new issue."""
	repository = get_working_repo(client, args.repository)
	print('Please enter the long description for this issue.')
	print('Starting your text editor:')
	desc_text = text_from_editor()
	repository.create_issue(args.title, body=desc_text)

def close(client, args):
	"""Close an existing open issue."""
	issue = get_working_issue(client, args)
	issue.edit(state='closed')

def do_list(client, args):
	"""Command to list the issues for a given repository."""
	repository = get_working_repo(client, args.repository)
	status = args.status or 'open'
	issues = list(repository.get_issues(state=status))
	if not issues:
		print('%s has no %s issues' % (repository.full_name, status))
	else:
		print('%s has the following %s issues' % (repository.full_name, status))
		print('Issue# - Title')
	for issue in issues:
		print('%s - %s' % (issue.number, issue.title))

def get(client, args):
	issue = get_working_issue(client, args)
	comments = issue.get_comments()
	print('Issue #%d: %s' % (issue.number, issue.title))
	print('Opened by %s on %s at %s' % (issue.user.login,
		issue.created_at.date(), issue.created_at.strftime('%H:%M:%S')))
	print('Last updated on %s at %s' % (issue.updated_at.date(),
		issue.updated_at.strftime('%H:%M:%S')))
	if issue.closed_by and issue.closed_at:
		print("Closed by %s on %s at %s" % (issue.closed_by.login,
		issue.closed_at.date(), issue.closed_at.strftime('%H:%M:%S')))
	if issue.labels:
		print('Labels:')
		for label in issue.labels:
			print('* %s' % label.name)
	print('Long description:')
	print_enclosed_text(issue.body)
	print('Comments:')
	print()
	for comment in comments:
		print_comment(comment)

def comment(client, args):
	issue = get_working_issue(client, args)
	print('Starting your text editor, so that you can compose your comment:')
	comment_text = text_from_editor()
	issue.create_comment(comment_text)

def addlabel(client, args):
	issue = get_working_issue(client, args)
	repository = get_working_repo(client, args.repository)
	try:
		label = repository.get_label(args.label)
	except GithubException as e:
		if e.status == 404:
			die('''The label %s has not yet been added to this repository.
First, add it using:
cligh repo addlabel %s
''' % (args.label, args.label))
		else:
			die('''Unable to find the label %s in this repository.
Error message: %s
''' % (args.label, e.data['message']))

	issue.add_to_labels(label)

def remlabel(client, args):
	issue = get_working_issue(client, args)
	repository = get_working_repo(client, args.repository)
	try:
		label = repository.get_label(args.label)
	except GithubException as e:
		die('''Unable to find the label %s in this repository.
It cannot be removed from the issue at this time.
Error message: %s
''' % (args.label, e.data['message']))

	issue.remove_from_labels(label)

def make_issue_parser(subparsers):
	issue = subparsers.add_parser('issue', help='Manage and query issues.')
	subparsers = issue.add_subparsers(title='Issue-related subcommands.')
	subparsers.required = True
	subparsers.dest = 'issue_command'

	issue_list = subparsers.add_parser('list', help='List issues for a given repository.')
	issue_list.set_defaults(func=do_list)
	issue_list.add_argument('--status',
		help='List issues having this status; default is "open"')
	issue_list.add_argument('--repository', help='Name of the repository.')

	issue_get = subparsers.add_parser('get', help='View an issue.')
	issue_get.set_defaults(func=get)
	issue_get.add_argument('number', help='Number of the issue to retrieve.')
	issue_get.add_argument('--repository', help='Name of the repository.')

	issue_close = subparsers.add_parser('close', help='Close an issue.')
	issue_close.set_defaults(func=close)
	issue_close.add_argument('number',
		help='Number of the issue to close.')
	issue_close.add_argument('--repository', help='Name of the repository.')

	issue_open = subparsers.add_parser('open', help='Open a new issue.')
	issue_open.set_defaults(func=do_open)
	issue_open.add_argument('title', help='Title of the issue.')
	issue_open.add_argument('--repository', help='Name of the repository.')

	issue_comment = subparsers.add_parser('comment',
		help='Comment on an existing issue.')
	issue_comment.set_defaults(func=comment)
	issue_comment.add_argument('number',
		help='Number of the issue on which you wish to comment.')
	issue_comment.add_argument('--repository', help='Name of the repository.')

	issue_addlabel = subparsers.add_parser('add_label',
		help='Add a label to an issue.')
	issue_addlabel.set_defaults(func=addlabel)
	issue_addlabel.add_argument('number',
		help='Number of the issue on which you wish to add a label.')
	issue_addlabel.add_argument('label', help='Label to add.')
	issue_addlabel.add_argument('--repository', help='Name of the repository.')

	issue_remlabel = subparsers.add_parser('remove_label',
		help='Remove a label from an issue.')
	issue_remlabel.set_defaults(func=remlabel)
	issue_remlabel.add_argument('number',
		help='Number of the issue from which you wish to remove a label.')
	issue_remlabel.add_argument('label', help='Label to remove.')
	issue_remlabel.add_argument('--repository', help='Name of the repository.')

