import falcon
import json
import requests
import settings
from wsgiref.simple_server import make_server

# URL for main crash submission
target_url = settings.mozcrash
# URLs for other crash services
other_urls = [settings.backtrace_url]

class CrashDiverter:
    def copy_post_remote(req, resp, resource):
        def extract_values():
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

        data = extract_values()
        if resp.text:
            data['crashid'] = resp.text.split('=')[1]
        for url in other_urls:
            ans = requests.request(method='POST', url=url, data=data, files=resp.context.files, params=req.params)

    @falcon.after(copy_post_remote)
    def on_post(self, req, resp):
        resp.context.files = {}
        form = req.get_media()
        for part in form:
            resp.context.files[part.name] = (part.filename, part.stream.read(), part.content_type)

        ans = requests.request(method='POST', url=target_url, files=resp.context.files, params=req.params)
        resp.status = ans.status_code
        resp.content_type = ans.headers['content-type']
        resp.text = ans.text


application = falcon.App()

application.add_route('/submit', CrashDiverter())

if __name__ == '__main__':
    with make_server('', 8000, application) as httpd:
        print('Serving on port 8000...')
        httpd.serve_forever()
