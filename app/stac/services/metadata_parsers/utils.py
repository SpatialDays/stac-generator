from loguru import logger


def deep_merge_dicts(dict1, dict2):
    """
    Merge two dictionaries recursively, with dict2 taking precedence over dict1.

    :param dict1: The primary dictionary.
    :param dict2: The secondary dictionary which takes precedence over dict1.
    :return: A new dictionary which is the result of merging dict1 and dict2.
    """
    merged = dict1.copy()

    for key, value in dict2.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = deep_merge_dicts(merged[key], value)
        else:
            merged[key] = value

    return merged


def merge_stac_items(primary_item, metadata_item):
    """
    Merge two STAC items, with metadata_item taking precedence over primary_item.

    :param primary_item: The primary STAC item.
    :param metadata_item: The secondary STAC item which takes precedence over primary_item.
    :return: A new STAC item which is the result of merging primary_item and metadata_item.
    """
    return deep_merge_dicts(primary_item, metadata_item)
