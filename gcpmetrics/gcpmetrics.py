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

def metrics(project_id, resource_descriptors, metric_descriptors):
    client = monitoring.Client(project=project_id)

    if resource_descriptors:
        list_resource_descriptors(client)

    elif metric_descriptors:
        list_metric_descriptors(client)

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

    args = parser.parse_args()
    metrics(args.project_id, args.resource_descriptors, args.metric_descriptors)

if __name__ == '__main__':
    sys.exit(main())

