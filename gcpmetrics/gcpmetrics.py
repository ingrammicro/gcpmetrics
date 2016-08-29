#!/usr/bin/env python

import sys
import argparse
from tabulate import tabulate
from gcloud import monitoring

def list_resource_descriptors(client):
    print 'Monitored resource descriptors:'

    index = 0
    for descriptor in client.list_resource_descriptors():
        index += 1
        print 'Resource descriptor #{}'.format(index)
        print '\tname: {}'.format(descriptor.name)
        print '\ttype: {}'.format(descriptor.type)
        print '\tdisplay_name: {}'.format(descriptor.display_name)
        print '\tdescription: {}'.format(descriptor.description)
        print '\tlabels:'
        subindex = 0
        for label in descriptor.labels:
            subindex += 1
            print '\t\tLabel descriptor #{}'.format(subindex)
            print '\t\t\tkey: {}'.format(label.key)
            print '\t\t\tvalue_type: {}'.format(label.value_type)
            print '\t\t\tdescription: {}'.format(label.description)
        print

def list_metric_descriptors(client):
    print 'Defined metric descriptors:'

    index = 0
    for descriptor in client.list_metric_descriptors():
        index += 1
        print 'Metric descriptor #{}'.format(index)
        print '\tname: {}'.format(descriptor.name)
        print '\ttype: {}'.format(descriptor.type)
        print '\tmetric_kind: {}'.format(descriptor.metric_kind)
        print '\tvalue_type: {}'.format(descriptor.value_type)
        print '\tunit: {}'.format(descriptor.unit)
        print '\tdisplay_name: {}'.format(descriptor.display_name)
        print '\tdescription: {}'.format(descriptor.description.encode('utf-8'))
        print

def _build_label_filter(category, *args, **kwargs):
    """Construct a filter string to filter on metric or resource labels."""
    terms = list(args)
    print 'PATCHED _build_label_filter (!)'
    import six
    for key, value in six.iteritems(kwargs):
        if value is None:
            continue

        suffix = None
        if key.endswith('_prefix') \
            or key.endswith('_suffix') \
            or key.endswith('_greater') \
            or key.endswith('_greaterequal') \
            or key.endswith('_less') \
            or key.endswith('_lessequal'):
                key, suffix = key.rsplit('_', 1)

        if category == 'resource' and key == 'resource_type':
            key = 'resource.type'
        else:
            key = '.'.join((category, 'label', key))

        if suffix == 'prefix':
            term = '{key} = starts_with("{value}")'
        elif suffix == 'suffix':
            term = '{key} = ends_with("{value}")'
        elif suffix == 'greater':
            term = '{key} > {value}'
        elif suffix == 'greaterequal':
            term = '{key} >= {value}'
        elif suffix == 'less':
            term = '{key} < {value}'
        elif suffix == 'lessequal':
            term = '{key} <= {value}'
        else:
            term = '{key} = "{value}"'

        terms.append(term.format(key=key, value=value))

    return ' AND '.join(sorted(terms))

def perform_query(client):

    # metric.type = "appengine.googleapis.com/http/server/response_count"
    #   AND resource.label.module_id = "service"
    #   AND metric.label.response_code >= 500
    #   AND metric.label.response_code < 600

    # yes, this is ugly, but we need to fix this method...
    monitoring.query._build_label_filter = _build_label_filter

    query = client.query(
        metric_type='appengine.googleapis.com/http/server/response_count',
        days=10
        )

    query = query.select_resources(module_id='service')
    query = query.select_metrics(response_code_greaterequal=500)
    print query.filter

def metrics(project_id, resource_descriptors, metric_descriptors, query):
    client = monitoring.Client(project=project_id)

    if resource_descriptors:
        list_resource_descriptors(client)

    elif metric_descriptors:
        list_metric_descriptors(client)

    elif query:
        perform_query(client)

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    parser.add_argument(
        '--project_id', help='GCP Project ID.', metavar='ID', required=True)
    parser.add_argument(
        '--resource_descriptors', default=False, action='store_true', help='List monitored resource descriptors.')
    parser.add_argument(
        '--metric_descriptors', default=False, action='store_true', help='List available metric descriptors.')
    parser.add_argument(
        '--query', default=False, action='store_true', help='Perform time series query.')

    args = parser.parse_args()
    metrics(args.project_id, args.resource_descriptors, args.metric_descriptors, args.query)

if __name__ == '__main__':
    sys.exit(main())

