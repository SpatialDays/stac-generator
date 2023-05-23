# STAC Generator

STAC Generator is a microservice that creates SpatioTemporal Asset Catalog (STAC) JSON from provided asset and metadata file paths.

## Payload Structure

The STAC Generator accepts a JSON payload with the following structure:

```json
{
  "gdalInfos": [
    {
      "tiffUrl": "https://path-to-cloud-storage/first-file.tif",
      "gdalInfo": {
        // GDAL info for first-file.tif here
      }
    },
    {
      "tiffUrl": "https://path-to-cloud-storage/second-file.tif",
      "gdalInfo": {
        // GDAL info for second-file.tif here
      }
    }
    // More GDAL info objects here...
  ],
  "assets": [
    "https://path-to-cloud-storage/readme.md",
    "https://path-to-cloud-storage/license.txt",
    "https://path-to-cloud-storage/shapefile.shp",
    "https://path-to-cloud-storage/metadata.json",
    "https://path-to-cloud-storage/first-file.tif",
    "https://path-to-cloud-storage/second-file.tif"
    // Other asset URLs here...
  ],
  "method": "GET | DELETE | POST"
}
```