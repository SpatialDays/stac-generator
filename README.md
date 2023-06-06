# STAC Generator

STAC Generator is a microservice that creates SpatioTemporal Asset Catalog (STAC) JSON from provided asset and metadata file paths.

`This is a work in progress, expect improvements over the coming weeks`

## Payload Structure

The STAC Generator accepts a JSON payload with the following structure:

```json
{
  "files": [
    "https://path-to-cloud-storage/readme.md",
    "https://path-to-cloud-storage/license.txt",
    "https://path-to-cloud-storage/shapefile.shp",
    "https://path-to-cloud-storage/first-file.tif",
    "https://path-to-cloud-storage/second-file.tif"
  ],
  "metadata": ["https://path-to-cloud-storage/metadata.json"],
  "method": "POST | PUT | DELETE"
}
```
## Optional Payload

`metadata` and `method` do nothing for now. This will change.

## Usage with Mounted Directory

STAC Generator is designed to work with a mounted directory. When providing file paths in the payload, ensure that they correspond to the mounted directory paths rather than direct URLs. To facilitate this, the `get_mounted_file()` function is provided in the `utils` module. It converts a given file path into its corresponding path within the mounted file system.

## Usage of `rio_stac`

STAC Generator utilizes the `rio_stac` package to generate STAC metadata for each TIFF file provided in the payload. The generated metadata is then added to the STAC item. The `rio_stac.create_stac_item()` function is used to create STAC metadata for a given TIFF file.


## Entrypoints

This microservice can works with HTTP and Redis.

Please refer to `tests/test_stac.py` for how it currently works.

To use Redis, you can submit a request to the channel `stac_generator_stac`
