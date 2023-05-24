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


def merge_rio_stac_items(generated_rio_stac_items: list):
    print(generated_rio_stac_items) # [<Item id=test-item.tif>, <Item id=test-item-2.tif>]
    for stac_item in generated_rio_stac_items:
        print(stac_item.to_dict()) 
