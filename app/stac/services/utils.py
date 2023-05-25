import mimetypes
from urllib.parse import urlparse


def get_file_type(filepath: str):
    """
    Determines the MIME type of a file based on its content.

    Args:
        filepath (str): The path to the file.

    Returns:
        str: The MIME type of the file.
    """
    # TODO: Greatly extend. Also consider using https://gist.github.com/james-hinton/88876c7e8709e788546a4e0ca03e4eb7
    mime_type, _ = mimetypes.guess_type(filepath)
    return mime_type


def is_tiff(filepath: str):
    """
    Determines if a file is a TIFF based on its MIME type.

    Args:
        filepath (str): The path to the file.

    Returns:
        bool: True if the file is a TIFF, False otherwise.
    """
    mime_type = get_file_type(filepath)
    return mime_type == "image/tiff"


def get_mounted_file(filepath: str):
    """
    Converts a given file path into its corresponding path within a mounted file system.

    This function parses the given file path and prepends it with '/mnt/' to simulate a path
    in a file system that's been mounted at '/mnt/'.

    Args:
        filepath (str): The original file path.

    Returns:
        str: The corresponding path in the mounted file system.
    """
    parsed_url = urlparse(filepath)
    mounted_path = '/mnt/' + parsed_url.path.lstrip('/')
    return mounted_path
