from argparse import ArgumentParser


def get_args():
    parser = ArgumentParser(description="Commit data processing module for GripHook")

    parser.add_argument('--download-meta', action='store_true',
                        help='download commit metadata from a repository')
    parser.add_argument('--download-files', action='store_true',
                        help='download files corresponding to a list of commits')
    parser.add_argument('--download-diffs', action='store_true',
                        help='download diffs corresponding to a list of commits')

    parser.add_argument('--repository', type=str, required=True,
                        help='full name of the repository in owner/repo format')
    parser.add_argument('--pages', type=int, default=100,
                        help='number of pages to download')

    args = parser.parse_args()
    return args
