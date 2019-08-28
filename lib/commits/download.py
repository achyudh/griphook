import json
import os

from tqdm import tqdm

from lib.common import github
from lib.util.io import create_directory_structure


def commit_metadata(repo_name, num_pages):
    """
    Download commit metadata from a repository
    :param repo_name: string in owner/repo_name format
    :param num_pages:
    """
    metadata_dict = github.commits(repo_name, num_pages=num_pages)

    create_directory_structure(os.path.join('data', 'commits', repo_name))
    with open(os.path.join('data', 'commits', repo_name, 'commit_metadata.json'), 'w') as metadata_file:
        json.dump(metadata_dict, metadata_file)


def commit_files(repo_name):
    """
    Download files corresponding to a list of commits
    :param repo_name: string in owner/repo_name format
    """
    with open(os.path.join('data', 'commits', repo_name, 'commit_metadata.json'), 'r') as metadata_file:
        metadata_dict = json.load(metadata_file)

    files_dict = dict()
    for commit in tqdm(metadata_dict):
        files_dict[commit['sha']] = github.commit_files(repo_name, commit['sha'])

    with open(os.path.join('data', 'commits', repo_name, 'commit_files.json'), 'w') as metadata_file:
        json.dump(metadata_dict, metadata_file)


def commit_diffs(repo_name):
    """
    Download files corresponding to a list of commits
    :param repo_name: string in owner/repo_name format
    """
    with open(os.path.join('data', 'commits',  repo_name, 'commit_metadata.json'), 'r') as metadata_file:
        metadata_dict = json.load(metadata_file)

    diffs_dict = dict()
    for commit in tqdm(metadata_dict):
        diffs_dict[commit['sha']] = github.diff(commit['diff_url'])

    with open(os.path.join('data', 'commits', repo_name, 'commit_diffs.json'), 'w') as metadata_file:
        json.dump(diffs_dict, metadata_file)
