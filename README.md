# STAC Generator

STAC Generator is a microservice that creates SpatioTemporal Asset Catalog (STAC) JSON from provided asset and metadata file paths.

`This is a work in progress, expect improvements over the coming weeks`

## Payload Structure

The STAC Generator accepts a JSON payload with the following structure:

```json
{
  "files": [
    "https://path-to-mounted-storage/readme.md",
    "https://path-to-mounted-storage/license.txt",
    "https://path-to-mounted-storage/shapefile.shp",
    "https://path-to-mounted-storage/first-file.tif",
    "https://path-to-mounted-storage/second-file.tif"
  ],
  "metadata": { "ID": "This is an example metadata object" },
  "parser": "example"
}
```

### Payload Explanation

The payload submitted as `mock_item_dict` is a JSON object that consists of three keys: `files`, `metadata`, and `parser`. Below is a breakdown of each key:

#### `files`

- **Type**: Array
- **Description**: The `files` key contains an array of URLs pointing to the data files associated with the STAC item. This includes the actual data files (e.g., GeoTIFFs), as well as any auxiliary files such as metadata documents (e.g., READMEs, licenses) or shapefiles that are related to the item.
- **Example**: URLs can be absolute URLs pointing to an external source or relative paths pointing to local storage.

#### `metadata`

- **Type**: Object
- **Description**: The `metadata` key contains an object with additional information relevant to the STAC item. This information is primarily intended for identification and contextualization purposes. It may include an ID, title, description, or any other metadata that can help in the organization and comprehension of the item.
- **Example**: The metadata or manifest associated with a TIFF order which can contain data such as cloud cover, acquisition date, etc.

#### `parser`

- **Type**: String
- **Description**: The `parser` key specifies the name of a custom parser script that will be used to process and integrate the data files into a STAC item. The parser script must be stored in a predefined directory in `app/stac/services/metadata_parsers/standard`, and it should be capable of handling the files and metadata provided. This allows users to implement their own logic for parsing and structuring the data, making the process more adaptable to various data formats and structures.
- **Example**: The value is the name of the parser script (without _parser.py) that should be executed. So for `app/stac/services/metadata_parsers/standard/example_parser.py`, the value would be `example`

## Environment Variables

This application is configured using the following environment variables:

### Redis Configuration

- `REDIS_HOST`: This is the hostname of your Redis instance. The default is `redis`.
- `REDIS_PORT`: This is the port number of your Redis instance. The default is `6379`.
- `REDIS_INCOMING_LIST_NAME`: This is the name of the Redis list that the application will monitor for incoming tasks. The default is `stac_generator_generate`.
- `REDIS_OUTGOING_LIST_NAME`: This is the name of the Redis list where the application will post the results of its tasks. The default is `stac_generator_output`.
- `REDIS_DB`: This is the number of the Redis database to use. The default is `0`.

### Other Configurations

- `MERGE_TIFFS`: A boolean variable indicating whether to merge TIFF files. The default is `false`.
- `CHECK_COG_TYPE`: A boolean variable indicating whether to check if the TIFF files are in Cloud Optimized GeoTIFF (COG) format. The default is `true`.
- `LOG_COG_INFO`: A boolean variable indicating whether to log additional info about COGs. The default is `false`.

To setup these variables, copy the `.env.example` file to a file named `.env` in the same directory, and replace the right-hand side of each line with your desired settings.

## Usage with Mounted Directory

STAC Generator is designed to work with a mounted directory. When providing file paths in the payload, ensure that they correspond to the mounted directory paths rather than direct URLs. To facilitate this, the `get_mounted_file()` function is provided in the `utils` module. It converts a given file path into its corresponding path within the mounted file system.

## Usage of `rio_stac`

STAC Generator utilizes the `rio_stac` package to generate STAC metadata for each TIFF file provided in the payload. The generated metadata is then added to the STAC item. The `rio_stac.create_stac_item()` function is used to create STAC metadata for a given TIFF file.

## Entrypoints

This microservice can works with HTTP and Redis.

Please refer to `tests/test_stac.py` for how it currently works.

To use Redis, you can submit a request to the channel `stac_generator_stac`

To do a CURL request you can do

```bash
curl -X POST "http://localhost:8000/stac/generate" -H "Content-Type: application/json" -d '{"files": ["https://path-to-mounted-storage.com/readme.md", "https://path-to-mounted-storage.com/license.txt", "https://path-to-mounted-storage.com/shapefile.shp", "manual-upload-storage-blob/017078204010_01_20AUG12110524-S3DS-017078204010_01_P001.TIF"], "metadata": {"ID": "017078204010_01_20AUG12110524-S3DS-017078204010_01_P001"}, "parser": "example"}'
```