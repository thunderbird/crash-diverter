import falcon
import helpers
import json
import requests
import settings
from wsgiref.simple_server import make_server

# URL for main crash submission
target_url = settings.backtrace_url
# URLs for other crash services
other_urls = []

class CrashDiverter:
    def copy_post_remote(req, resp, resource):
        for url in other_urls:
            ans = requests.request(method='POST', url=url, data=self.data, files=resp.context.files, params=req.params)

    @falcon.after(copy_post_remote)
    def on_post(self, req, resp):
        def extract_values():
            # Extract some things to pass as attributes for Backtrace.
            data = json.loads(resp.context.files['extra'][1])
            if data.get('TelemetryEnvironment', None):
                env = json.loads(data['TelemetryEnvironment'])
                # Get useful bits out of TelemetryEnvironment
                data['os_name'] = env['system']['os']['name']
                data['os_version'] = env['system']['os']['version']

            # Delete unwanted attributes.
            for key in settings.skip_attributes:
                data.pop(key, None)
            return data

        # Prepare data.
        resp.context.files = {}
        form = req.get_media()
        import pdb; pdb.set_trace()
        for part in form:
            resp.context.files[part.name] = (part.filename, part.stream.read(), part.content_type)
        self.data = extract_values()
        data['crashid'] = helpers.create_crash_id()

        ans = requests.request(method='POST', url=target_url, data=self.data, files=resp.context.files, params=req.params)
        resp.status = ans.status_code
        resp.content_type = 'text/plain'
        resp.text = ''
        if resp.status == falcon.HTTP_200:
            resp.text = 'CrashID=bp-{crashid}\n'.format(crashid=data['crashid'])


application = falcon.App()

application.add_route('/submit', CrashDiverter())

if __name__ == '__main__':
    with make_server('', 8000, application) as httpd:
        print('Serving on port 8000...')
        httpd.serve_forever()
