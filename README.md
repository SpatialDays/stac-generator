# STAC Generator

STAC Generator is a microservice that creates SpatioTemporal Asset Catalog (STAC) JSON from provided asset and metadata file paths.

## Payload Structure

The STAC Generator accepts a JSON payload with the following structure:

```json
{
  "source": "manual", // or "automatic"
  "provider": "<provider-name>",
  "collection": "<URL-to-collection.json>",
  "itemId": "<optional-item-ID>",
  "assetPaths": [
    "<Blob-Storage-URL-1>",
    "<Blob-Storage-URL-2>",
    "<Blob-Storage-URL-3>",
    // ...as many URLs as there are assets
  ],
  "metadataPaths": [
    "<Blob-Storage-URL-Metadata-1>",
    "<Blob-Storage-URL-Metadata-2>"
    // ...as many URLs as there are metadata files
  ],
  "extensions": [
    "<extension-1>",
    "<extension-2>"
    // ...as many extensions as needed
  ]
}
```

If itemId is not supplied, a unique item ID will be generated. 
If extensions are not supplied or the array is empty, all available STAC extensions will be used.