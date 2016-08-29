# Google Cloud Metrics Command-Line Tool

## Overview

You need to be authenticated to run this tool as described in 
http://googlecloudplatform.github.io/gcloud-python/stable/gcloud-auth.html

Today it only supports interactive authentication, i.e.:

```
$ gcloud auth login
```

We will soon add support of service account tokents.

## Usage

```
usage: gcpmetrics.py [-h] --project_id ID [--resource_descriptors]
                     [--metric_descriptors] [--query] [--service_id ID]
                     [--metric_id ID] [--days num] [--hours num]
                     [--minutes num]
```

## Examples

```
$ gcpmetrics --project_id odin-ap --resource_descriptors

$ gcpmetrics --project_id odin-ap --metric_descriptors

$ gcpmetrics --project_id odin-ap --query --service_id service --days 1 --metric_id appengine.googleapis.com/http/server/response_count
```
