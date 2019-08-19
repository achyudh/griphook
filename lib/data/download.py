import json
import os

from tqdm import tqdm

from lib.data import github
from lib.util.io import create_directory_structure


def pr_metadata(repo_name, num_pages):
    """
    Download pull request metadata from a repository
    :param repo_name: string in owner/repo_name format
    :param num_pages:
    """
    metadata_dict = github.pull_requests(repo_name, num_pages=num_pages)

    create_directory_structure(os.path.join('data', repo_name))
    with open(os.path.join('data', repo_name, 'pr_metadata.json'), 'w') as metadata_file:
        json.dump(metadata_dict, metadata_file)


def pr_files(repo_name):
    """
    Download files corresponding to a list of pull requests
    :param repo_name: string in owner/repo_name format
    """
    with open(os.path.join('data', repo_name, 'pr_metadata.json'), 'r') as metadata_file:
        metadata_dict = json.load(metadata_file)

    files_dict = dict()
    for pull_request in tqdm(metadata_dict):
        files_dict[pull_request['number']] = github.pull_request_files(repo_name, pull_request['number'])

    with open(os.path.join('data', repo_name, 'pr_files.json'), 'w') as metadata_file:
        json.dump(metadata_dict, metadata_file)


def pr_diffs(repo_name):
    """
    Download files corresponding to a list of pull requests
    :param repo_name: string in owner/repo_name format
    """
    with open(os.path.join('data', repo_name, 'pr_metadata.json'), 'r') as metadata_file:
        metadata_dict = json.load(metadata_file)

    diffs_dict = dict()
    for pull_request in tqdm(metadata_dict):
        diffs_dict[pull_request['number']] = github.pull_request_diff(repo_name, pull_request['diff_url'])

    with open(os.path.join('data', repo_name, 'pr_diffs.json'), 'w') as metadata_file:
        json.dump(diffs_dict, metadata_file)
