import falcon
import helpers
import json
import requests
import settings
from wsgiref.simple_server import make_server


class CrashDiverter:
    def copy_post_remote(req, resp, resource):
        for url in settings.other_urls:
            ans = requests.request(method='POST', url=url, data=resp.context.data, files=resp.context.files, params=req.params)


    @falcon.after(copy_post_remote)
    def on_post(self, req, resp):
        # Prepare data.
        resp.context.files = {}
        form = req.get_media()

        for part in form:
            resp.context.files[part.name] = (part.filename, part.stream.read(), part.content_type)

        # Parameters for the request to Socorro/Backtrace.
        reqparams = {
            'method':'POST',
            'url':'',
            'files': resp.context.files,
            'params': req.params
        }
        # Thunderbird expects a plaintext response with the Crash ID.
        crashid = ''
        resp.content_type = 'text/plain'

        # We are sending to Socorro.
        if settings.usemoz:
            reqparams['url'] = settings.mozcrash
            ans = requests.request(**reqparams)
            if ans.status_code == 200:
                crashid = ans.text.split('=')[1]
            resp.text = ans.text

        # Extract JSON data for Backtrace.
        resp.context.data = helpers.extract_values(resp.context.files['extra'][1])
        resp.context.data['crashid'] = crashid

        # We're not sending to Socorro, only Backtrace.
        if not settings.usemoz:
            # Without Socorro, we generate a crash ID ourselves.
            resp.context.data['crashid'] = helpers.create_crash_id()
            reqparams['url'] = settings.other_urls[0]
            reqparams['data'] = resp.context.data
            ans = requests.request(**reqparams)
            if ans.status_code == 200:
                    respdata = json.loads(ans.text)
                    if respdata.get('response') == 'ok' and respdata.get('_rxid'):
                        resp.text = 'CrashID={crashid}\n'.format(crashid=resp.context.data['crashid'])
        # Send the response.
        resp.status = ans.status_code


application = falcon.App()

application.add_route('/submit', CrashDiverter())

if __name__ == '__main__':
    with make_server('', 8000, application) as httpd:
        print('Serving on port 8000...')
        httpd.serve_forever()
