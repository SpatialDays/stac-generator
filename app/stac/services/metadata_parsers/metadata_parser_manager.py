import importlib.util
from loguru import logger
import os


class MetadataParserManager:
    @staticmethod
    def get_parser(metadata_type):
        logger.info(f"Getting parser for metadata type: {metadata_type}")
        # Check for standard parsers
        standard_parser = MetadataParserManager.load_parser("standard", metadata_type)
        if standard_parser:
            return standard_parser

        # Check for proprietary parsers
        proprietary_parser = MetadataParserManager.load_parser(
            "proprietary", metadata_type
        )
        if proprietary_parser:
            return proprietary_parser

        raise ValueError(f"Unsupported metadata type: {metadata_type}")

    @staticmethod
    def load_parser(directory, metadata_type):
        # Construct the path to the parser
        parser_path = os.path.join(
            os.path.dirname(__file__), directory, f"{metadata_type}_parser.py"
        )

        # Check if the parser file exists and load it dynamically
        if os.path.exists(parser_path):
            spec = importlib.util.spec_from_file_location(
                f"{directory}.{metadata_type}_parser", parser_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # This assumes that the parser class is named 'Parser' in each file
            return module.Parser()

        return None

    @staticmethod
    def list_available_parsers():
        parser_directories = ["standard", "proprietary"]
        available_parsers = {"standard": [], "proprietary": []}

        for directory in parser_directories:
            directory_path = os.path.join(os.path.dirname(__file__), directory)
            if os.path.exists(directory_path):
                for filename in os.listdir(directory_path):
                    if filename.endswith("_parser.py"):
                        parser_name = filename.replace("_parser.py", "")
                        available_parsers[directory].append(parser_name)

        logger.info(f"Available metadata parsers: {available_parsers}")

        return available_parsers
