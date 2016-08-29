#!/usr/bin/env python

import sys
import argparse
import pandas
import datetime
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

def perform_query(client, metric_id, days, hours, minutes, resource_filter, metric_filter, align, reduce, reduce_grouping):

    # yes, ugly, but we need to fix this method...
    print 'PATCHED _build_label_filter'
    monitoring.query._build_label_filter = _build_label_filter

    query = client.query(
        metric_type=metric_id,
        days=days,
        hours=hours,
        minutes=minutes
        )

    if resource_filter:
        query = query.select_resources(**resource_filter)

    if metric_filter:
        query = query.select_metrics(**metric_filter)

    if align:
        delta = datetime.timedelta(days=days, hours=hours, minutes=minutes)
        seconds = delta.total_seconds()
        print 'ALIGNMENT: {} seconds: {}'.format(align, seconds)
        query = query.align(align, seconds=seconds)

    if reduce:
        print 'REDUCE: {} grouping: {}'.format(reduce, reduce_grouping)
        if reduce_grouping:
            query = query.reduce(reduce, *reduce_grouping)
        else:
            query = query.reduce(reduce)

    print 'QUERY: {}'.format(query.filter)

    dataframe = query.as_dataframe()
    print dataframe


def process(project_id, list_resources, list_metrics, query, metric_id, days, hours, minutes, resource_filter, metric_filter, alignment, reduce, reduce_grouping):

    client = monitoring.Client(project=project_id)

    if list_resources:
        list_resource_descriptors(client)

    elif list_metrics:
        list_metric_descriptors(client)

    elif query:
        perform_query(client, metric_id, days, hours, minutes, resource_filter, metric_filter, alignment, reduce, reduce_grouping)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
        )
    parser.add_argument('--project_id', help='Project ID.', metavar='ID', required=True)
    parser.add_argument('--list_resources', default=False, action='store_true', help='List monitored resource descriptors and exit.')
    parser.add_argument('--list_metrics', default=False, action='store_true', help='List available metric descriptors and exit.')
    parser.add_argument('--query', default=False, action='store_true', help='Run the time series query.')
    parser.add_argument('--since_dawn', default=False, action='store_true', help='Calculate delta since the dawn of time.')
    parser.add_argument('--metric_id', help='Metric ID as defined by Google Monitoring API..', metavar='ID')
    parser.add_argument('--days', default=0, help='Days from now to calculate the query start date.', metavar='INT')
    parser.add_argument('--hours', default=0, help='Hours from now to calculate the query start date.', metavar='INT')
    parser.add_argument('--minutes', default=0, help='Minutes from now to calculate the query start date.', metavar='INT')
    parser.add_argument('--resource_filter', default=None, help='Filter of resources in the var:val[,var:val] format.', metavar='S')
    parser.add_argument('--metric_filter', default=None, help='Filter of metrics in the var:val[,var:val] format.', metavar='S')
    parser.add_argument('--alignment', default=None, help='Alignment of data ALIGN_NONE, ALIGN_SUM. etc.', metavar='A')
    parser.add_argument('--reduce', default=None, help='Reduce of data REDUCE_NONE, REDUCE_SUM, etc.', metavar='R')
    parser.add_argument('--reduce_grouping', default=None, help='Reduce grouping in the var1[,var2] format.', metavar='R')

    def process_filter(_filter):
        if not _filter:
            return None
        _filter = _filter.split(',')
        _ret = {}
        for res in _filter:
            key, value = res.split(':')
            _ret[key] = value
        return _ret

    args = parser.parse_args()
    days = args.days
    hours = args.hours
    minutes = args.minutes

    if args.since_dawn:
        # October 6, 2011 = Google Cloud Platform launch date ;-)
        dawn = datetime.datetime.strptime('2011-10-06', '%Y-%m-%d')
        now =  datetime.datetime.utcnow()
        delta = now - dawn
        days = delta.days
        hours = 0
        minutes = 0

    reduce_grouping = None
    if args.reduce_grouping:
        reduce_grouping = args.reduce_grouping.aplit(',')

    resource_filter = process_filter(args.resource_filter)
    metric_filter = process_filter(args.metric_filter)
    process(
        args.project_id,
        args.list_resources,
        args.list_metrics,
        args.query,
        args.metric_id,
        int(days),
        int(hours),
        int(minutes),
        resource_filter,
        metric_filter,
        args.alignment,
        args.reduce,
        reduce_grouping
        )

if __name__ == '__main__':
    sys.exit(main())

