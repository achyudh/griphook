import os


def create_directory_structure(path):
    """
    Creates a nested directory structure if it doesn't exist
    :param path: directory structure to create
    """
    if not os.path.exists(path):
        try:
            os.makedirs(path)

        except FileExistsError:
            # Check if the directory is created between the
            # os.path.exists and the os.makedirs function calls
            pass
