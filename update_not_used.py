# encoding: utf-8

from workflow import Workflow, ICON_WEB, ICON_WARNING, web, PasswordNotFound

WORK_SPACE_ID = YOUR_WID_HERE

def get_recent_projects(api_key):
    """Retrieve recent projects from toggl

    Returns a list of projects dictionaries.

    """
    url = 'https://www.toggl.com/api/v8/workspaces/{}/projects'.format(WORK_SPACE_ID)
    headers = {'Authorization' : 'Basic {}'.format(api_key)}
    r = web.get(url, headers = headers)

    # throw an error if request failed
    # Workflow will catch this and show it to the user
    r.raise_for_status()

    # Parse the JSON returned by toggl and return the projects
    result = r.json()
    return result

def main(wf):
    try:
        # Get API key from Keychain
        api_key = wf.get_password('toggl_api_key')

        # Retrieve projects from cache if available and no more than 300
        # seconds old
        def wrapper():
            """`cached_data` can only take a bare callable (no args),
                so we need to wrap callables needing arguments in a function
                that needs none.
                """
            return get_recent_projects(api_key)

        projects = wf.cached_data('projects', wrapper, max_age=300)
        # Record our progress in the log file
        wf.logger.debug('{} Toggl projects cached'.format(len(projects)))

    except PasswordNotFound:
        # API key has not yet been set
        # Nothing we can do about this, so just log it
        wf.logger.error('No API key saved')


if __name__ == '__main__':
    wf = Workflow()
    wf.run(main)
