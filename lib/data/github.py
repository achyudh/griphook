from requests.auth import HTTPBasicAuth
import requests, json, time
from flask import Flask

with open('config.json', 'r') as config_file:
    client_config = json.load(config_file)

app = Flask(__name__)
http_auth_username = client_config['HTTP_AUTH_USERNAME']
http_auth_secret = client_config['HTTP_AUTH_SECRET']
http_auth = HTTPBasicAuth(http_auth_username, http_auth_secret)

# Header to get reactions along with comments
reactions_header = {'Accept': 'application/vnd.github.squirrel-girl-preview',
                    'direction': 'desc', 'sort': 'created'}
# Header to get diff along with pull request
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
        print("Waiting for %d minutes..." % ((int(headers['X-RateLimit-Reset']) - time.time())//60))
        time.sleep(int(headers['X-RateLimit-Reset']) - time.time() + 1)
        return "RateLimit Reset"
    else:
        if ratelimit_remaining % 100 == 0:
            print('X-RateLimit-Remaining:', ratelimit_remaining)
        return "Positive RateLimit"


def generic(request_url, headers=None, plaintext=False):
    """

    :param request_url:
    :param headers:
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
    merged_response = list()
    for i0 in range(num_pages):
        # print("Request:", request_url)
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

        # Change request_url to next url in the link
        if 'Link' in response.headers:
            raw_links = response.headers['Link'].split(',')
            next_url = None
            for link in raw_links:
                split_link = link.split(';')
                if split_link[1][-6:] == '"next"':
                    next_url = split_link[0].strip()[1:-1]
                    break
            if next_url is not None:
                request_url = next_url
            else:
                break
        else:
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

def pull_request_files():
    return


def pull_requests(repo_name, num_pages=1):
    request_url = 'https://api.github.com/repos/%s/pulls' % repo_name
    return generic(request_url, headers=reactions_header, num_pages=num_pages)
