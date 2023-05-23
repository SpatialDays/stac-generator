import mimetypes


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
