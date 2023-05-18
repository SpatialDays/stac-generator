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
  ]
}
```

If itemId is not supplied, a unique item ID will be generated. 
If extensions are not supplied or the array is empty, all available STAC extensions will be used.

## Metadata Structure

The metadata provided should be in JSON format, designed to align closely with the STAC Item structure. This helps in ensuring the metadata can be correctly merged with the STAC Item generated by the STAC Generator. 

Below is a simplified example of a `metadata.json` that includes information for the `view` STAC extension:

```json
{
  "stac_extensions": [
    "view"
  ],
  "properties": {
    "view:incidence_angle": "<incidence_angle_value>",
    "view:sun_azimuth": "<sun_azimuth_value>"
  }
}
```

## Asynchronous Processing & Job Queueing

STAC Generator is designed to handle multiple requests efficiently, using Redis Queue (RQ) for job queueing and providing asynchronous processing of STAC Item generation.

When a request is received, it is converted into a job and added to a Redis-backed queue for processing. This allows the service to immediately start handling the next request.

Each job is assigned a unique ID, which is returned in the response to the client's request. This job ID can be used by the client to check the status of their job.

Here's a simplified example of how the queueing system works:

```python
from rq import Queue
from redis import Redis

# Set up a connection to Redis and a queue
redis_conn = Redis()
q = Queue(connection=redis_conn)

# When a request is received, create a job and add it to the queue
payload = {
    # ...payload data...
}
job = q.enqueue(generate_stac_item, payload)

# Return the job ID in the response
return {'job_id': job.get_id()}, 202
```

To check the status of a job, we can use the provided job ID with a status endpoint:

```python
from flask import Flask, request
from rq.job import Job

app = Flask(__name__)

@app.route("/status/<job_id>", methods=['GET'])
def get_status(job_id):
    job = Job.fetch(job_id, connection=redis_conn)
    return {'status': job.get_status()}
```