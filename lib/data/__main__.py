import os

from lib.data.args import get_args
from lib.data import download

if __name__ == '__main__':
    args = get_args()

    if args.download_meta:
        # Download pull request metadata from a repository
        download.pr_metadata()
    if args.pr_files:
        # Download files corresponding to a list of pull requests
        download.pr_files()
