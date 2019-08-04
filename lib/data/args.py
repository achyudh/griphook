from argparse import ArgumentParser


def get_args():
    parser = ArgumentParser(description="Data processing module for GripHook")
    parser.add_argument('--download-meta', action='store_true',
                        help='download pull request metadata from a repository')
    parser.add_argument('--download-files', action='store_true',
                        help='download files corresponding to a list of pull requests')
    args = parser.parse_args()
    return args
