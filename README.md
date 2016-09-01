# Google Cloud Monitoring API Command Line
[![Build Status](https://travis-ci.org/odin-public/gcpmetrics.svg?branch=master)](https://travis-ci.org/odin-public/gcpmetrics)

Homepage: https://github.com/odin-public/gcpmetrics

## 1. Overview

The Google Monitoring API v3 gives you access to over 900 Stackdriver Monitoring
metrics from Google Cloud Platform and Amazon Web Services. You can create your
own custom metrics and can organize your cloud resources using groups.

More information: https://cloud.google.com/monitoring/api/v3/

This tool provides a simple command-line interface to query Google Monitoring API v3.
This is handy when integrating with warious monitoring tools, like Zabbix (http://www.zabbix.com/)
or Nagios (https://www.nagios.org/).

## 2. Installation

You can install this tool simply by running

```
$ pip install --upgrade gcpmetrics
```

## 3. Authentication

You need to be authenticated with Google Cloud API to run this tool. Two ways of authentication 
are supported: (a) interactive login and (b) service account token. 
  
### a. Interactive

If you're developing locally, the easiest way to authenticate is using the Google Cloud SDK:

```
$ gcloud auth login
```

### b. Service acount

If you're running your application elsewhere, you should download a service account
JSON keyfile and point to it using --keyfile parameter.

```
$ gcpmetrics --keyfile ./keyfile.json [...]
```

More details on authentication with gcloud: http://googlecloudplatform.github.io/gcloud-python/stable/gcloud-auth.html

## 4. Project ID

The project ID is a unique identifier for a Google Cloud Platform project and is used only
within the console. A project ID cannot be changed after the project is created. You need to
identify your project ID with the --project parameter

```
$ gcpmetrics --project my-unique-project-id [...]
```

More details on how to locate your project ID: https://support.google.com/cloud/answer/6158840

## 5. Monitored Resources

A monitored resource represents a cloud entity that originates some monitoring data or is the subject of it.
You can list all monitored resources visible to you at the moment by running the following command:

```
$ gcpmetrics --keyfile ./keyfile.json --project my-unique-project-id --list-resources

Monitored resource descriptors:
Resource descriptor #1
	name: projects/my-unique-project-id/monitoredResourceDescriptors/api
	type: api
[...]
```

More details on monitored resources: https://cloud.google.com/monitoring/api/v3/metrics#intro-resources

## 6. Available Metrics

A MetricDescriptor defines a metric type and its dimensions and could be listed
as shown in the following example:

```
$ gcpmetrics --keyfile ./keyfile.json --project my-unique-project-id --list-metrics

Defined metric descriptors:
Metric descriptor #1
	name: projects/my-unique-project-id/metricDescriptors/agent.googleapis.com/agent/api_request_count
	type: agent.googleapis.com/agent/api_request_count
	metric_kind: CUMULATIVE
	value_type: INT64
	unit: 1
	display_name: API Request Count
	description: API request count
[...]
```

More details on metrics: https://cloud.google.com/monitoring/api/v3/metrics#metric-descriptor

## 7. Simple Query

An example of simple query to retrieve on of standard metrics (see https://cloud.google.com/monitoring/api/metrics)
identified as "appengine.googleapis.com/system/cpu/usage" would look like the following:

```
$ gcpmetrics --keyfile ./keyfile.json \
    --project my-unique-project-id \
    --query --days 2 \
    --metric appengine.googleapis.com/system/cpu/usage

QUERY: metric.type = "appengine.googleapis.com/system/cpu/usage"
resource_type                            gae_app
project_id                  my-unique-project-id           
module_id                                default           
version_id                                     1           
source                                       api runtime   
2016-08-30 13:35:52.268                      0.0     0.0   
...
2016-09-01 13:32:52.268                      0.0    18.0  

[2825 rows x 4 columns]
```

Note that time period is required and in the above example it was specified as 2 days (from 'now').

## 8. Aggregations

Let's say we want to calculate the total value of the same counter used in the above example. The
query would look like the following:

```
$ gcpmetrics --keyfile ./keyfile.json \
    --project my-unique-project-id \
    --query --days 2 \
    --metric appengine.googleapis.com/system/cpu/usage \
    --reduce REDUCE_SUM \
    --align ALIGN_SUM

ALIGN: ALIGN_SUM seconds: 172800.0
REDUCE: REDUCE_SUM grouping: None
QUERY: metric.type = "appengine.googleapis.com/system/cpu/usage"
resource_type                        gae_app
project_id              my-unique-project-id
2016-09-01 13:40:00                    45809
```

Supported --align parameters:

  - ALIGN_NONE
  - ALIGN_DELTA
  - ALIGN_RATE
  - ALIGN_INTERPOLATE
  - ALIGN_NEXT_OLDER
  - ALIGN_MIN
  - ALIGN_MAX
  - ALIGN_MEAN
  - ALIGN_COUNT
  - ALIGN_SUM
  - ALIGN_STDDEV
  - ALIGN_COUNT_TRUE
  - ALIGN_FRACTION_TRUE

Supported --reduce parameters:

  - REDUCE_NONE
  - REDUCE_MEAN
  - REDUCE_MIN
  - REDUCE_MAX
  - REDUCE_SUM
  - REDUCE_STDDEV
  - REDUCE_COUNT
  - REDUCE_COUNT_TRUE
  - REDUCE_FRACTION_TRUE
  - REDUCE_PERCENTILE_99
  - REDUCE_PERCENTILE_95
  - REDUCE_PERCENTILE_50
  - REDUCE_PERCENTILE_05

## 9. Silent Mode

In certain cases (like integration into systems like Zabbix) you only need the resulting value
to be printed to the standard output. To do that, just append --iloc00 as shown below:

```
$ gcpmetrics --keyfile ./keyfile.json \
    --project my-unique-project-id \
    --query --days 2 \
    --metric appengine.googleapis.com/system/cpu/usage \
    --reduce REDUCE_SUM \
    --align ALIGN_SUM \
    --iloc00

45809
```

Note that 'iloc' stands for "integer location" of the pandas library (http://pandas.pydata.org/)
and refers to the index [0:0] of the returned table. Thus will only work with aggregated values.

## 10. Metric Filtering

Let's say you want to calculate total number of 5xx responses in a given period of time.
The coutner responsible for that is called "appengine.googleapis.com/http/server/response_count",
but you need to apply filter (500 <= code) && (code < 600). You can do that with the following 
command: 

```
$ gcpmetrics --keyfile ./keyfile.json \
    --project my-unique-project-id \
    --query --days 2 \
    --metric appengine.googleapis.com/http/server/response_count \
    --metric-filter \
    response_code_greaterequal:500,response_code_less:600

QUERY: metric.type = "appengine.googleapis.com/http/server/response_count" \
        AND metric.label.response_code < 600 \
        AND metric.label.response_code >= 500

resource_type                            gae_app
project_id                  my-unique-project-id                              
module_id                                default                   service2   
version_id                                     1                 0-1-dev159   
loading                                    false true                 false   
response_code                                500  500                   501   
2016-08-30 15:13:34.577                      NaN  1.0                   NaN   
2016-08-30 15:14:34.577                      2.0  0.0                   NaN   
2016-08-30 15:15:34.577                      0.0  0.0                   NaN   
[...]
```

The following operations are supported
      
  - ```'{key}_prefix:{value}'``` becomes ```'{key} = starts_with("{value}")'```
  - ```'{key}_suffix:{value}'``` becomes ```'{key} = ends_with("{value}")'```
  - ```'{key}_greater:{value}'``` becomes ```'{key} > {value}'```
  - ```'{key}_greaterequal:{value}'``` becomes ```'{key} >= {value}'```
  - ```'{key}_less:{value}'``` becomes ```'{key} < {value}'```
  - ```'{key}_lessequal:{value}'``` becomes ```'{key} <= {value}'```

More on filters: https://cloud.google.com/monitoring/api/v3/filters

## 11. Resource Filtering

In case you need to filter based on resource attributes, you might want to use --resource-filter directly,
or refer to the particularly often used filter of resource.label.module_id = "{value}" with --service as 
shown in the below example: 

```
$ gcpmetrics --keyfile ./keyfile.json \
    --project my-unique-project-id \
    --query --days 2 \
    --metric appengine.googleapis.com/http/server/response_count \
    --metric-filter \
    response_code_greaterequal:500,response_code_less:600 \

QUERY: metric.type = "appengine.googleapis.com/http/server/response_count" \
        AND resource.label.module_id = "default" \
        AND metric.label.response_code < 600 \
        AND metric.label.response_code >= 500

resource_type                            gae_app     
project_id                  my-unique-project-id     
module_id                                default     
version_id                                     1     
loading                                    false true
response_code                                500  500
2016-08-30 15:13:34.577                      NaN  1.0
2016-08-30 15:14:34.577                      2.0  0.0
2016-08-30 15:15:34.577                      0.0  0.0
[...]
```

Note that only service 'default' data was returned this time. 
More on filters: https://cloud.google.com/monitoring/api/v3/filters

## 12. Configurations

When monitoring multiple metrics across multuple projects it is handy to have command line 
parameters predefined (instead of writing the whole set of parameters every time). This could
be achieved with configuration files.

You can init your own configuration by running the following command: 
```
$ gcpmetrics --init-config ./folder

Creating folder: ./folder
Creating configuration file: ./folder/config.yaml
Creating (empty) key file: ./folder/keyfile.json
Configuration created, use '--config ./folder' to reference it.
```

The configuration file looks like the below:

```
$ cat ./folder/config.yaml

keyfile: ./keyfile.json
project: my-unique-project-id
service: default

http_response_5xx_sum:
    query: true
    infinite: true
    metric: 'appengine.googleapis.com/http/server/response_count'
    metric_filter: 'response_code_greaterequal:500,response_code_less:600'
    align: 'ALIGN_SUM'
    reduce: 'REDUCE_SUM'
    iloc00: True
```

which is a yaml file containing the same command line parameters as the tool itself.
By referencing this file, tool will pickup parameters defined in it, i.e.

```
$ gcpmetrics --config ./folder/config.yaml
```

will be interpreted as

```
$ gcpmetrics --keyfile ./keyfile.json \
             --project my-unique-project-id \
             --service default
```

based on the configuration file defined above.

## 13. Presets

It is also possible to refer to the configuration presets defined in the configuraiton file.
Based on the example configuration file below, where "http_response_5xx_sum" is defined,
it is possible to run the following command:
 
```
$ gcpmetrics --init-config ./folder --preset http_response_5xx_sum
```

which will be interpreted as

```
$ gcpmetrics --keyfile ./keyfile.json \
             --project my-unique-project-id \
             --service default \
             --query: true \
             --infinite: true \
             --metric: appengine.googleapis.com/http/server/response_count \
             --metric_filter response_code_greaterequal:500,response_code_less:600 \
             --align ALIGN_SUM \
             --reduce REDUCE_SUM \
             --iloc00 True
```

## 14. All Parameters

```
$ gcpmetrics --help

usage: gcpmetrics [-h] [--version] [--init-config DIR] [--config FILE]
                  [--keyfile FILE] [--preset ID] [--project ID]
                  [--list-resources] [--list-metrics] [--query] [--service ID]
                  [--metric ID] [--infinite] [--days INT] [--hours INT]
                  [--minutes INT] [--resource-filter S] [--metric-filter S]
                  [--align A] [--reduce R] [--reduce-grouping R] [--iloc00]

Google Cloud Monitoring API Command Line
Website: https://github.com/odin-public/gcpmetrics

optional arguments:
  -h, --help           show this help message and exit
  --version            Print gcpmetics version and exit.
  --init-config DIR    Location of configuration files.
  --config FILE        Local configuration *.yaml file to be used.
  --keyfile FILE       Goolge Cloud Platform service account key file.
  --preset ID          Preset ID, like http_response_5xx_sum, etc.
  --project ID         Project ID.
  --list-resources     List monitored resource descriptors and exit.
  --list-metrics       List available metric descriptors and exit.
  --query              Run the time series query.
  --service ID         Service ID.
  --metric ID          Metric ID as defined by Google Monitoring API.
  --infinite           Calculate time delta since the dawn of time.
  --days INT           Days from now to calculate the query start date.
  --hours INT          Hours from now to calculate the query start date.
  --minutes INT        Minutes from now to calculate the query start date.
  --resource-filter S  Filter of resources in the var:val[,var:val] format.
  --metric-filter S    Filter of metrics in the var:val[,var:val] format.
  --align A            Alignment of data ALIGN_NONE, ALIGN_SUM. etc.
  --reduce R           Reduce of data REDUCE_NONE, REDUCE_SUM, etc.
  --reduce-grouping R  Reduce grouping in the var1[,var2] format.
  --iloc00             Print value from the table index [0:0] only.
```
