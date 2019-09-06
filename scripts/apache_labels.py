import json
import os
import string
from collections import defaultdict

import requests

# List of repositories that will make up the dataset
repositories = ['apache/beam']

# Filename extension for code files
code_ext = '.java'


def has_whitespace(s):
    return True in [c in s for c in string.whitespace]


def get_commit_tag(commit_message):
    if commit_message[0] == '[':
        commit_tag = commit_message[1:].split(']')[0]

    else:
        commit_tag = commit_message.split()[0]

        if commit_tag[-1] in {'.', ':', ',', ';'}:
            commit_tag = commit_tag[:-1]

    if '-' not in commit_tag or has_whitespace(commit_tag):
        return None

    return commit_tag


def get_commit_label(commit_tag):
    issue_type = None
    request_url = 'https://issues.apache.org/jira/rest/api/2/issue/'

    try:
        response = requests.get(request_url + commit_tag).json()
        issue_type = response['fields']['issuetype']['name']

    except Exception as e:
        print('Exception processing %s:' % commit_tag, e)

    return issue_type


for repo_name in repositories:
    # List containing labelled pull requests
    labels = dict()
    label_counts = defaultdict(int)

    # Load commit metadata dict
    metadata_path = os.path.join(os.pardir, 'data', 'commits', repo_name, 'commit_metadata.json')
    with open(metadata_path, 'r') as metadata_file:
        metadata_dict = json.load(metadata_file)

    num_processed = 0
    for commit in metadata_dict:
        commit_tag = get_commit_tag(commit['commit']['message'])

        if commit_tag:
            commit_label = get_commit_label(commit_tag)
            if commit_label:
                labels[commit['sha']] = commit_label
                label_counts[commit_label] += 1

        num_processed += 1
        if num_processed % 100 == 0:
            print('Processed %d of %d commits in %s' %
                  (num_processed, len(metadata_dict), repo_name))

    label_path = os.path.join(os.pardir, 'data', 'commits', repo_name, 'commit_labels.json')
    with open(label_path, 'w') as json_file:
        json.dump(labels, json_file)

    print("Number of labelled commits:", len(labels))
    print("Dataset distribution:", label_counts)