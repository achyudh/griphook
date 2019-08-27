from lib.commits import download
from lib.commits.args import get_args

if __name__ == '__main__':
    args = get_args()

    if args.download_meta:
        # Download pull request metadata from a repository
        download.commit_metadata(args.repository, args.pages)

    if args.download_files:
        # Download files corresponding to a list of pull requests
        download.commit_files(args.repository)

    if args.download_diffs:
        # Download diffs corresponding to a list of pull requests
        download.commit_diffs(args.repository)
