import falcon
import requests
from wsgiref.simple_server import make_server

target_url = "https://crash-reports.mozilla.com/submit"

class CrashDiverter:
    def on_post(self, req, resp):
        resp.context.files = {}
        form = req.get_media()
        for part in form:
            resp.context.files[part.name] = (part.filename, part.stream.read(), part.content_type)

        ans = requests.request(method='POST', url=target_url, files=resp.context.files, params=req.params)
        resp.status = ans.status_code
        resp.content_type = ans.headers['content-type']
        resp.text = ans.text


app = falcon.App()

app.add_route('/', CrashDiverter())

if __name__ == '__main__':
    with make_server('', 8000, app) as httpd:
        print('Serving on port 8000...')

        # Serve until process is killed
        httpd.serve_forever()
