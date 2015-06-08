# encoding: utf-8

import sys
import base64
import argparse
from workflow import Workflow, ICON_WEB, ICON_WARNING, web, PasswordNotFound
from pprint import pprint

log = None
WORK_SPACE_ID = YOUR_WID_HERE

def get_recent_projects(api_key):
    """Retrieve recent projects from toggl

    Returns a list of projects dictionaries.

    """
    url = 'https://www.toggl.com/api/v8/workspaces/{}/projects'.format(WORK_SPACE_ID)
    base64string = base64.encodestring('%s:%s' % (api_key, 'api_token')).replace('\n', '')

    headers = {'Authorization' : 'Basic '+ base64string}
    r = web.get(url, headers = headers)

    # throw an error if request failed
    # Workflow will catch this and show it to the user
    r.raise_for_status()

    # Parse the JSON returned by toggl and return the projects
    result = r.json()
    return result

def search_key_for_project(project):
    """Generate a string search key for a post"""
    elements = []
    elements.append(project['name'])  # title of post
    return u' '.join(elements)

def main(wf):
    log.debug('Started')
    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()
    # add an optional (nargs='?') --setkey argument and save its
    # value to 'apikey' (dest). This will be called from a separate "Run Script"
    # action with the API key
    parser.add_argument('--setkey', dest='apikey', nargs='?', default=None)
    # add an optional query and save it to 'query'
    parser.add_argument('query', nargs='?', default=None)
    # parse the script's arguments
    args = parser.parse_args(wf.args)

    ####################################################################
    # Save the provided API key
    ####################################################################

    # decide what to do based on arguments
    if args.apikey:
        # Script was passed an API key
        # save the key
        log.debug('Saving the API_KEY')
        wf.save_password('toggl_api_key', args.apikey)
        return 0  # 0 means script exited cleanly

    ####################################################################
    # Check that we have an API key saved
    ####################################################################

    try:
        api_key = wf.get_password('toggl_api_key')
    except PasswordNotFound:  # API key has not yet been set
        wf.add_item('No API key set.',
                    'Please use pbsetkey to set your Pinboard API key.',
                    valid=False,
                    icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    ####################################################################
    # View/filter Toggl projects
    ####################################################################


    #query = args.query

    # Retrieve posts from cache if available and no more than 600
    # seconds old

    def wrapper():
        """`cached_data` can only take a bare callable (no args),
        so we need to wrap callables needing arguments in a function
        that needs none.
        """
        return get_recent_projects(api_key)

    projects = wf.cached_data('projects', wrapper, max_age=300)

    # If script was passed a query, use it to filter posts
    # min_score helps eliminating ambiguous searches
    time = None
    if args.query:
        splited_query = args.query.split(":")
        projects = wf.filter(splited_query[0], projects, key=search_key_for_project, min_score=20)
        if len(splited_query) > 1:
            time = splited_query[1]
            time = time.strip()


    if not projects:
        # we have no data to show, so show a warning and stop
        wf.add_item('No project found with this name', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    # Loop through the returned posts and add an item for each to
    # the list of results for Alfred
    for project in projects:
        if time:
            wf.add_item(title=project['name'],
                        subtitle='Press enter to record time',
                        arg='{0}:{1}:{2}'.format(project['name'], project['id'], time),
                        valid=True)
        else:
            wf.add_item(title=project['name'],
                        subtitle='Press tab to select this project AND add time in minutes (syntax :time)',
                        autocomplete=project['name'])

    # Send the results to Alfred as XML
    wf.send_feedback()

if __name__ == u"__main__":
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
