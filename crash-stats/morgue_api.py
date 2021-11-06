import boto3
import json
import requests
import settings
from urllib.parse import unquote_plus

class APIHelper(object):
    """
    Access the Backtrace Morgue API via HTTP requests.
    """
    def __init__(self, crashid):
        token = (boto3.resource('dynamodb').Table(settings.DYNAMO_TABLE)
                      .get_item(Key={'name': 'bttoken'})['Item']['token'])
        self.query_url = settings.BT_API_URL + '/query?token={0}&universe=thunderbird&project=Thunderbird'.format(token)
        self.crashid = crashid
        self.timestamp = 1609509600

    def run_query(self):
        query = {"filter":[{
            "crashid": [["contains", self.crashid]],
            "timestamp": [["at-least", self.timestamp]]
        }],
        "virtual_columns":[],
        "select":settings.REPORT_FIELDS}
        data = requests.post(self.query_url, json=query)
        self.results = data.json()

    def parse_results(self):
        report_data = {}
        res = self.results['response']
        for i, val in enumerate(res['columns_desc']):
            name = val['name']
            if len(res['values'][i]) < 2:
                value = res['values'][i][0]
            else:
                value = res['values'][i][1][0]
            report_data[name] = value

        if 'callstack' in report_data and report_data['callstack']:
            report_data['callstack'] = json.loads(report_data['callstack'])
        if 'CrashTime' and 'InstallTime' in report_data:
            report_data['install_age'] = report_data['CrashTime'] - report_data['InstallTime']
        return report_data

    def deal_with_addons(self, report):
        """ Add-ons field is a csv string with inconsistent formatting for some reason. """
        def _get_formatted_addon(addon):
            """Return a properly formatted addon string.
            Format is: addon_identifier:addon_version
            This is used because some addons are missing a version. In order to
            simplify subsequent queries, we make sure the format is consistent.
            """
            return addon if ':' in addon else addon + ':NO_VERSION'


        report['addons_checked'] = None

        # it's okay to not have EMCheckCompatibility
        if report.get('EMCheckCompatibility', None):
            report['addons_checked'] = bool(report['EMCheckCompatibility'])

        original_addon_str = report.get('Add-ons', '')
        if not original_addon_str:
            addon = []
        else:
            addons= [
                unquote_plus(_get_formatted_addon(x))
                for x in original_addon_str.split(",")
            ]

        # Split the strings into fields.
        report['addons'] = []

        for addon_line in addons:
            split_data = addon_line.split(':')
            extension_id = ''
            version = ''

            if len(split_data) >= 1:
                extension_id = split_data[0]
            if len(split_data) >= 2:
                version = split_data[1]

            addon = {'id': extension_id, 'version': version}
            addon['name'] = ''
            addon['is_system'] = None

            report['addons'].append(addon)

        return report

    def get_results(self):
        self.run_query()
        return self.deal_with_addons(self.parse_results())
