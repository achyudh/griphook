import json
import time

import requests
from requests.auth import HTTPBasicAuth
from tqdm import tqdm

with open('config.json', 'r') as config_file:
    client_config = json.load(config_file)

http_auth_username = client_config['HTTP_AUTH_USERNAME']
http_auth_secret = client_config['HTTP_AUTH_SECRET']
http_auth = HTTPBasicAuth(http_auth_username, http_auth_secret)

# Header to get diff along with pull request
sort_header = {'direction': 'desc', 'sort': 'created'}
diff_header = {'Accept': 'application/vnd.github.VERSION.diff'}


def rate_reset_wait(headers):
    """

    :param headers:
    :return:
    """
    if 'X-RateLimit-Remaining' in headers:
        ratelimit_remaining = int(headers['X-RateLimit-Remaining'])
    else:
        ratelimit_remaining = 1
    if ratelimit_remaining <= 0:
        tqdm.write("Waiting for %d minutes..." % ((int(headers['X-RateLimit-Reset']) - time.time())//60))
        time.sleep(int(headers['X-RateLimit-Reset']) - time.time() + 1)
        return "RateLimit Reset"
    else:
        if ratelimit_remaining % 100 == 0:
            tqdm.write('X-RateLimit-Remaining: %d' % ratelimit_remaining)
        return "Positive RateLimit"


def generic(request_url, headers=None, plaintext=False):
    """

    :param request_url:
    :param headers:
    :param plaintext:
    :return:
    """
    if headers is not None:
        response = requests.get(request_url, auth=http_auth, headers=headers)
    else:
        response = requests.get(request_url, auth=http_auth)

    wait_status = rate_reset_wait(response.headers)
    if wait_status != "Positive RateLimit":
        if headers is not None:
            response = requests.get(request_url, auth=http_auth, headers=headers)
        else:
            response = requests.get(request_url, auth=http_auth)

    if response.status_code == 404:
        raise Exception(response.json()['message'])

    if plaintext:
        return response.content.decode("utf-8", "ignore")
    else:
        return response.json()


def paged_generic(request_url, headers=None, num_pages=1):
    """

    :param request_url:
    :param headers:
    :param num_pages:
    :return:
    """
    merged_response = list()

    for _ in tqdm(range(num_pages)):
        if headers is not None:
            response = requests.get(request_url, auth=http_auth, headers=headers)
        else:
            response = requests.get(request_url, auth=http_auth)

        wait_status = rate_reset_wait(response.headers)
        if wait_status == "Positive RateLimit":
            merged_response.extend(response.json())
        else:
            if headers is not None:
                response = requests.get(request_url, auth=http_auth, headers=headers)
            else:
                response = requests.get(request_url, auth=http_auth)
                merged_response.extend(response.json())

        if 'Link' not in response.headers:
            break

        # Change request_url to next url in the link
        raw_links = response.headers['Link'].split(',')
        next_url = None

        for link in raw_links:
            split_link = link.split(';')
            if split_link[1][-6:] == '"next"':
                next_url = split_link[0].strip()[1:-1]
                break

        request_url = next_url
        if not next_url:
            break

    return merged_response


def pull_request(repo_name, pr_number):
    """

    :param repo_name: string in owner/repo_name format
    :param pr_number: integer identifier for the pull request
    :return: dict containing the pull request meta data along with the diff if get_diff was true
    """
    request_url = 'https://api.github.com/repos/%s/pulls/%s' % (repo_name, pr_number)
    try:
        response = generic(request_url)
    except Exception as e:
        raise e
    return response


def pull_request_diff(repo_name, request_url):
    """

    :param repo_name: string in owner/repo_name format
    :param request_url: diff url for the pull request
    :return: dict containing the pull request meta data along with the diff if get_diff was true
    """
    try:
        response = generic(request_url, plaintext=True)
    except Exception as e:
        raise e
    return response


def pull_request_files(repo_name, pr_number):
    """

    :param repo_name:
    :param pr_number:
    :return:
    """
    request_url = 'https://api.github.com/repos/%s/pulls/%s/files' % (repo_name, pr_number)
    try:
        response = generic(request_url)
    except Exception as e:
        raise e
    return response


def pull_requests(repo_name, num_pages=1):
    """

    :param repo_name:
    :param num_pages:
    :return:
    """
    request_url = 'https://api.github.com/repos/%s/pulls?state=all' % repo_name
    return paged_generic(request_url, headers=sort_header, num_pages=num_pages)
