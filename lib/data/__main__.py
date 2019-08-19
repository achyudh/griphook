import os

from lib.data.args import get_args
from lib.data import download

if __name__ == '__main__':
    args = get_args()

    if args.download_meta:
        # Download pull request metadata from a repository
        download.pr_metadata(args.repository, args.pages)

    if args.download_files:
        # Download files corresponding to a list of pull requests
        download.pr_files(args.repository)

    if args.download_diffs:
        # Download diffs corresponding to a list of pull requests
        download.pr_diffs(args.repository)
