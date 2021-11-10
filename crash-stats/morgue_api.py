import boto3
import json
import requests
import settings
from urllib.parse import unquote_plus

class NotFoundError(Exception):
    """Query works but no data is returned by the API."""
    pass

class UnknownAPIError(Exception):
    """Backtrace API query failed for no known reason."""
    pass

class KnownAPIError(Exception):
    """Backtrace API query failed and there's an error message in the response."""
    pass

class LoginError(Exception):
    """Unable to complete login to Backtrace API."""
    pass


class APIHelper(object):
    """
    Access the Backtrace Morgue API via HTTP requests.
    """
    def __init__(self, crashid):
        self.crashid = crashid
        self.timestamp = 1609509600
        self.retries = 0

    def set_token(self):
        token = (boto3.resource('dynamodb').Table(settings.DYNAMO_TABLE)
                      .get_item(Key={'name': 'bttoken'})['Item']['token'])
        self.query_url = settings.BT_QUERY_URL.format(token=token)

    def do_login(self):
        """ Login to Backtrace and store the token."""
        table = boto3.resource('dynamodb').Table(settings.DYNAMO_TABLE)
        key = {'name': 'btcreds'}

        username = table.get_item(Key=key)['Item']['username']
        password = table.get_item(Key=key)['Item']['password']

        resp = requests.post(settings.BT_LOGIN_URL, data={'username': username, 'password': password})

        if 'token' in resp.json():
            token = resp.json()['token']
        else:
            raise LoginError("Can't find token in login response.")

        table.put_item(Item={'name': 'bttoken', 'token': token})

    def run_query(self):
        """ Run the API query and perform error checking on the response."""
        self.set_token()
        query = {"filter":[{
            "crashid": [["contains", self.crashid]],
            "timestamp": [["at-least", self.timestamp]]
        }],
        "virtual_columns":[],
        "select":settings.REPORT_FIELDS}
        data = requests.post(self.query_url, json=query)
        self.results = data.json()

        # Check if any results were returned.
        if 'error' in self.results:
            if self.results['error']['code'] == 5:
                if self.retries < 2:
                    self.do_login()
                    self.retries += 1
                    self.run_query()
                    return
                else:
                    raise LoginError('Unable to login after 2 attempts.')
            else:
                raise KnownAPIError('Code {code}: {msg}'.format(
                    code=str(self.results['error']['code']),
                    msg=str(self.results['error']['message'])
                ))

        if data.status_code != 200 or '_' not in self.results:
            raise UnknownAPIError('Backtrace returned a broken response.')

        if self.results['_']['runtime']['filter']['rows'] < 1:
            raise NotFoundError('Backtrace returned no results.')

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
