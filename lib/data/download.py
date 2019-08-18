import json
import os

from lib.data import github
from lib.util.io import create_directory_structure


def pr_metadata(repo_name, num_pages):
    """

    :param repo_name:
    :param num_pages:
    :return:
    """
    metadata_dict = github.pull_requests(repo_name, num_pages=num_pages)

    create_directory_structure(os.path.join('data', repo_name))
    with open(os.path.join('data', repo_name, 'pr_metadata.json'), 'w') as metadata_file:
        json.dump(metadata_dict, metadata_file)


def pr_files(repo_name):
    """

    :param repo_name:
    :return:
    """
    with open(os.path.join('data', repo_name, 'pr_metadata.json'), 'r') as metadata_file:
        metadata_dict = json.loads(metadata_file)

    files_dict = dict()
    for pull_request in metadata_dict:
        files_dict['sha'] = github.pull_request_files(repo_name, pull_request['number'])

    with open(os.path.join('data', repo_name, 'pr_files.json'), 'w') as metadata_file:
        json.dump(metadata_dict, metadata_file)
