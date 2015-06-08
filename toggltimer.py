# encoding: utf-8

import sys
import argparse
import json
import base64
import time
from workflow import Workflow, ICON_WEB, ICON_WARNING, web, PasswordNotFound
from pprint import pprint

log = None

def create_time_entry(api_key, project, timeInMinutes):
    """Creates the given amount on the given project
    """
    url = 'https://www.toggl.com/api/v8/time_entries'
    base64string = base64.encodestring('%s:%s' % (api_key, 'api_token')).replace('\n', '')

    headers = {'Authorization' : 'Basic ' + base64string,
                'Content-Type': 'application/json' }
    timeInSec = int(timeInMinutes)*60
    todayString = time.strftime("%Y-%m-%dT%H:%M:%S+02:00")
    log.debug('Logging ' + timeInMinutes + 'min for ' + todayString)

    payload = {'time_entry':
                {'description':'I was working dude!',
                'created_with':'Alfred Toggl Workflow',
                'start':todayString,
                'duration': '{0}'.format(timeInSec), 'pid': '{0}'.format(project)
                }}
    #log.debug(payload)
    #log.debug(headers)

    r = web.post(url, data = json.dumps(payload), headers = headers)
    #log.debug(r.status_code)
    #log.debug(r.headers)
    #log.debug(r)


    # throw an error if request failed
    # Workflow will catch this and show it to the user
    r.raise_for_status()

    # Parse the JSON returned by toggl and return the projects
    result = r.json()
    return result



def main(wf):
    log.debug('Started')
    api_key = None

    # Get query from Previous script
    if len(wf.args):
        query = wf.args[0]
    else:
        query = None

    try:
        api_key = wf.get_password('toggl_api_key')
    except PasswordNotFound:  # API key has not yet been set
        wf.add_item('No API key set.',
                    'Please use pbsetkey to set your Pinboard API key.',
                    valid=False,
                    icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    if query and api_key:
        splited_query = query.split(":")
        output_string = '{0} minutes in '.format(splited_query[2]) + splited_query[0]
        result = create_time_entry(api_key, splited_query[1], splited_query[2])

if __name__ == u"__main__":
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
