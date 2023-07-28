# STAC Generator

STAC Generator is a microservice that creates SpatioTemporal Asset Catalog (STAC) JSON from provided asset and metadata file paths.

With both HTTP and REDIS entrypoints, this microservice can be used in a variety of ways to generate STAC items from the incoming payload.

# Usage

1. Clone the repository
2. Copy the `.env.example` file to a file named `.env` and replace with your desired settings
3. Run `docker-compose up --build`
4. Navigate to `http://localhost:8000/docs` to view the Swagger UI

## Payload Structure

The STAC Generator accepts a JSON payload with the following structure:


```json
{
  "files": [
    "https://path-to-storage.com/readme.md",
    "https://path-to-storage.com/shapefile.shp",
    "https://deafrica-sentinel-1.s3.af-south-1.amazonaws.com/s1_rtc/N13E025/2018/01/04/0101B0/s1_rtc_0101B0_N13E025_2018_01_04_ANGLE.tif"
  ],
  "metadata": {
    "ID": "example_stac_item"
  },
  "metadata_url": "https://path-to-storage.com/SX8888.json",
  "parser": "example"
}
```

### Payload Explanation

The payload submitted as a JSON object consists of four keys: `files`, `metadata`, `metadata_url`, and `parser`. At least one of `metadata` or `metadata_url` should be provided, and both can be provided if needed. Below is a breakdown of each key:

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
- **Description**: The `metadata_url` key is an optional field that contains the URL pointing to the metadata document associated with the STAC item. If `metadata` is not provided, the service will attempt to fetch the metadata content from this URL. This key can also be used in conjunction with the `metadata` key to provide both the embedded metadata content within the STAC record and a link to the original metadata fwile. This is useful for cases where it's important to include the metadata content directly and also provide a reference to the original metadata document.
- **Restrictions**: This key is only applicable when using a parser that is designed to support it. The URL must be an HTTP or HTTPS URL pointing to a JSON metadata file.
- **Use Case**: When the metadata is available through an HTTP(S) URL and needs to be automatically fetched, or when it is important to include both metadata content and a reference to the original metadata document.
- **Example**: `"metadata_url": "https://example.com/path/to/metadata.json"`

#### `parser`

- **Type**: String
- **Description**: The `parser` key specifies the name of a custom parser script that will be used to process and integrate the data files into a STAC item. The parser script must be stored in a predefined directory in `app/stac/services/metadata_parsers/standard`, and it should be capable of handling the files and metadata provided. This allows users to implement their own logic for parsing and structuring the data, making the process more adaptable to various data formats and structures.
- **Example**: The value is the name of the parser script (without \_parser.py) that should be executed. So for `app/stac/services/metadata_parsers/standard/example_parser.py`, the value would be `example`

## Environment Variables

This application is configured using the following environment variables:

### Redis Configuration (Optional)

In addition to HTTP requests, this application can also be configured to listen for incoming tasks on a Redis channel.

In case if you want to use the Redis listener, the entrypoint is:

```bash
python3 -m app.redis_entrypoint
```

See additional [./Dockerfile-redis](./Dockerfile-redis) for more details.

In case you want to start a Redis listener instead of the HTTP server, you can use the following environment variables:

- `REDIS_HOST`: This is the hostname of your Redis instance. The default is `redis`.
- `REDIS_PORT`: This is the port number of your Redis instance. The default is `6379`.
- `REDIS_INPUT_LIST_NAME`: This is the name of the Redis list that the application will monitor for incoming tasks. The default is `stac_generator_generate`.
- `REDIS_OUTPUT_LIST_NAME`: This is the name of the Redis list where the application will post the results of its tasks. The default is `stac_generator_output`.
- `HTTP_PUBLISH_TO_STAC_API`: A boolean variable indicating whether the application should publish the generated STAC items to the STAC API via HTTP request.
- `REDIS_PUBLISH_TO_STAC_API`: A boolean variable indicating whether the application should publish the generated STAC items to the REDIS channel.

### Other Configurations

- `CHECK_COG_TYPE`: A boolean variable indicating whether to check if the TIFF files are in Cloud Optimized GeoTIFF (COG) format. The default is `true`.
- `LOG_COG_INFO`: A boolean variable indicating whether to log additional info about COGs. The default is `false`.
- `HTTP_PUBLISH_TO_STAC_API`=A boolean variable indicating whether the application should publish the generated STAC items to the STAC API. The default is true. If set to false, the application will not publish the items to the API.
- `STAC_API_URL`= This is the URL where the STAC API is hosted. The application will communicate with the STAC API through this URL.
- `USE_MOUNTED_VOLUMES` = A boolean variable indicating whether the application should utilise mounted volumes for faster access to TIFF files.

To setup these variables, copy the `.env.example` file to a file named `.env` in the same directory, and replace the right-hand side of each line with your desired settings.

## Mounted Volumes (Optional)

When working with large TIFF files, network retrieval can be slow and resource-intensive. To mitigate this, you can optionally configure the application to use mounted volumes. Mounted volumes allow for direct and rapid access to files, which significantly improves performance.

To enable the usage of mounted volumes, you need to set the `USE_MOUNTED_VOLUMES` environment variable to `true`. This instructs the application to access the TIFF files directly from a mounted directory.

### Mounted Directory Configuration Setup

To configure the application for blob mounting, follow these steps:

1. Copy the `blob_mounting_configurations_template.json` file and rename it to `blob_mounting_configurations.json`.

2. Open `blob_mounting_configurations.json` and replace the placeholder values with your actual mapped Storage details.

3. Make sure that `blob_mounting_configurations.json` is in the root directory of the project.

Note: Do not commit `blob_mounting_configurations.json` to your source control. This file contains confidential information.

## Entrypoints

This microservice can works with HTTP and Redis.

Please refer to `tests/test_stac.py` for how it currently works.

To use Redis, you can submit a request to the channel `stac_generator_stac`

To do a CURL request you can do

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/stac/generate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "files": [
    "https://path-to-storage.com/readme.md",
    "https://path-to-storage.com/shapefile.shp",
    "https://deafrica-sentinel-1.s3.af-south-1.amazonaws.com/s1_rtc/N13E025/2018/01/04/0101B0/s1_rtc_0101B0_N13E025_2018_01_04_ANGLE.tif"
  ],
  "metadata": {
    "ID": "example_stac_item"
  },
  "metadata_url": "https://path-to-storage.com/SX8888.json",
  "parser": "example"
}'
```
