#!/usr/bin/python

import csv, json
import pip._vendor.requests as requests

queries = {}


def parse_comment(rowstr):
    """
    Gets the test tag and query description from the comment line
    """
    tag, desc = '', ''
    if rowstr.startswith('#'):
        for entry in rowstr.split('#'):
            entry = entry.strip()
            if entry and 'TAG' in entry:
                tag = entry.split(':')[1]
                queries[tag] = {}
            elif entry != '':
                desc = entry
    return tag, desc


def populate_queries(csvfile):
    """
    Generates a dictionary of test tags, query description and query list for each test
    """
    last = ''
    for row in reader:
        rowstr = ', '.join(row)
        tag, desc = parse_comment(rowstr)
        if (tag != '' and desc != ''):
            last = tag
            queries[tag] = {'desc': desc, 'entries': []}
            continue
        queries[last]['entries'].append(rowstr)


if __name__ == "__main__":
    with open('local-corp-test-sample-corps.csv') as csvfile:
        reader = csv.reader(csvfile)
        populate_queries(csvfile)

    for query in queries['entity_type']['entries']:
        params = query.split(',')
        source_id = params[0].strip()
        type = params[1].strip()

        r = requests.get(f'http://localhost:8080/api/topic/ident/{type}/{source_id}/formatted')
        print(r.json())
