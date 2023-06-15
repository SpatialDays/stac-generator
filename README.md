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
  "metadata_url": "https://path-to-mounted-storage/metadata.json",
  "parser": "example"
}
```

### Payload Explanation

The payload submitted as `mock_item_dict` is a JSON object that consists of four keys: `files`, `metadata`, `metadata_url`, and `parser`. At least one of `metadata` or `metadata_url` should be provided, and both can be provided if needed. Below is a breakdown of each key:

#### `files`

- **Type**: Array
- **Description**: The `files` key contains an array of URLs pointing to the data files associated with the STAC item. This includes the actual data files (e.g., GeoTIFFs), as well as any auxiliary files such as metadata documents (e.g., READMEs, licenses) or shapefiles that are related to the item.
- **Example**: URLs can be absolute URLs pointing to an external source or relative paths pointing to local storage.

#### `metadata` (Optional)

- **Type**: Object
- **Description**: The `metadata` key contains an object with additional information relevant to the STAC item. This information is primarily intended for identification and contextualization purposes. It may include an ID, title, description, or any other metadata that can help in the organization and comprehension of the item.
- **Example**: The metadata or manifest associated with a TIFF order which can contain data such as cloud cover, acquisition date, etc.

#### `metadata_url` (Optional)

- **Type**: String
- **Description**: The `metadata_url` key is an optional field that contains the URL pointing to the metadata document associated with the STAC item. If `metadata` is not provided, the service will attempt to fetch the metadata content from this URL. This key can also be used in conjunction with the `metadata` key to provide both the embedded metadata content within the STAC record and a link to the original metadata file. This is useful for cases where it's important to include the metadata content directly and also provide a reference to the original metadata document.
- **Restrictions**: This key is only applicable when using a parser that is designed to support it. The URL must be an HTTP or HTTPS URL pointing to a JSON metadata file.
- **Use Case**: When the metadata is available through an HTTP(S) URL and needs to be automatically fetched, or when it is important to include both metadata content and a reference to the original metadata document.
- **Example**: `"metadata_url": "https://example.com/path/to/metadata.json"`

#### `parser`

- **Type**: String
- **Description**: The `parser` key specifies the name of a custom parser script that will be used to process and integrate the data files into a STAC item. The parser script must be stored in a predefined directory in `app/stac/services/metadata_parsers/standard`, and it should be capable of handling the files and metadata provided. This allows users to implement their own logic for parsing and structuring the data, making the process more adaptable to various data formats and structures.
- **Example**: The value is the name of the parser script (without \_parser.py) that should be executed. So for `app/stac/services/metadata_parsers/standard/example_parser.py`, the value would be `example`

## Environment Variables

This application is configured using the following environment variables:

### Redis Configuration

- `REDIS_HOST`: This is the hostname of your Redis instance. The default is `redis`.
- `REDIS_PORT`: This is the port number of your Redis instance. The default is `6379`.
- `REDIS_INCOMING_LIST_NAME`: This is the name of the Redis list that the application will monitor for incoming tasks. The default is `stac_generator_generate`.
- `REDIS_OUTGOING_LIST_NAME`: This is the name of the Redis list where the application will post the results of its tasks. The default is `stac_generator_output`.
- `REDIS_DB`: This is the number of the Redis database to use. The default is `0`.

### Other Configurations

- `CHECK_COG_TYPE`: A boolean variable indicating whether to check if the TIFF files are in Cloud Optimized GeoTIFF (COG) format. The default is `true`.
- `LOG_COG_INFO`: A boolean variable indicating whether to log additional info about COGs. The default is `false`.
- `PUBLISH_TO_STAC_API`=A boolean variable indicating whether the application should publish the generated STAC items to the STAC API. The default is true. If set to false, the application will not publish the items to the API.
- `STAC_API_URL`= This is the URL where the STAC API is hosted. The application will communicate with the STAC API through this URL.
- `USE_MOUNTED_VOLUMES` = A boolean variable indicating whether the application should utilise mounted volumes for faster access to TIFF files.

To setup these variables, copy the `.env.example` file to a file named `.env` in the same directory, and replace the right-hand side of each line with your desired settings.

## Usage with Mounted Directory

STAC Generator is designed to work with a mounted directory. When providing file paths in the payload, ensure that they correspond to the mounted directory paths rather than direct URLs. To facilitate this, the `get_mounted_file()` function is provided in the `utils` module. It converts a given file path into its corresponding path within the mounted file system.

### Mounted Directory Configuration Setup

To configure the application for blob mounting, follow these steps:

1. Copy the `blob_mounting_configurations_template.json` file and rename it to `blob_mounting_configurations.json`.

2. Open `blob_mounting_configurations.json` and replace the placeholder values with your actual mapped Storage details.

3. Make sure that `blob_mounting_configurations.json` is in the root directory of the project.

Note: Do not commit `blob_mounting_configurations.json` to your source control. This file contains confidential information.

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
