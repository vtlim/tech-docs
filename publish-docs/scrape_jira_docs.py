#!/usr/bin/env python3

import os
import re
import subprocess
import sys

from jira import JIRA
import jira
import yaml
from pathlib import Path

from jira.resources import Version

JIRA_URL = "https://implydata.atlassian.net"


config = {}
j: JIRA = {}
# dictionary to hold release notes by product
rn = {}


def read_config():
    global config

    if not config:
        config_fname = f'{Path.home()}/.gitjira/config.yaml'
        if os.path.isfile(config_fname):
            with open(config_fname, 'r') as config:
                config = yaml.load(config, Loader=yaml.SafeLoader)
        else:
            print(f"Could not find config file {config_fname}")
            exit(1)


def init_jira():
    global j
    read_config()
    j = JIRA(JIRA_URL, basic_auth=(config['jira']['username'], config['jira']['token']))

issue_types  = " and issuetype not in (Documentation,Test,'Test Execution','Test Plan','Test Set','Xray Test','Precondition')"
ticket_types = " and type not in (Subtask,Sub-task)"
label_types  = " and (labels not in (no_release_note) OR labels = NULL)"
eng_teams  = " and 'Eng Teams' not in (Talaria, Docs)"
status_types = " and ((status != 'To Do') OR (summary ~ 'Release Ticket - OS:*'))"

def get_tickets(fix_version):
    issues = j.search_issues("project=IMPLY and fixVersion=" + fix_version + issue_types + ticket_types + label_types + eng_teams + status_types, maxResults=False)
    #issues = j.search_issues("project=IMPLY and fixVersion=" + fix_version + issue_types)

    if not issues:
      return
    print(issues)
    for i in issues:

        # Custom field 10033 is Product. Each issue may have
        # multiple products. This adds the rn to each product
        # in the format used in the docs site.
        for option in i.fields.customfield_10033:

            # Add a new list and new product category
            if option.value not in rn.keys():
                rn[option.value]=[]

            # If resolution isn't done, mark for follow up
            # This means that ticket status is not done or that
            # the resolution could be something like 'won't do' or 'duplicate'
            suffix = ""
            ticket_resolution = i.fields.resolution
            if not i.fields.summary.startswith('Release Ticket - OS:') and (ticket_resolution is None or ticket_resolution.name != "Done"):
                suffix = " DOCS-TEAM-FOLLOWUP"

            key = i.key.split('-')[1]
            rn[option.value].append(f'- {i.fields.summary} (id: {key}){suffix}')

def main():
    init_jira()
    version = sys.argv[1]
    print (f'### Other changes in {version}\n')
    get_tickets(version)
    for key in rn.keys():
        print (f'#### {key} changes\n')
        for note in rn[key]:
            print(note)
        print('\n')
    # print ("\n")
    # get_tickets(version, "Druid")
    print ("\n")

if __name__ == '__main__':
    main()
