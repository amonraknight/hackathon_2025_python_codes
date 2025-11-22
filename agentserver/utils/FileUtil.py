import os

def get_all_files_under_path(path: str):
    """
    Get all the file names under the given folder.
    :param path:
    :return:
    """
    if not os.path.exists(path):
        return []
    else:
        return [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]