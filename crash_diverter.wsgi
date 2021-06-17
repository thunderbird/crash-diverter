import falcon
import requests
import settings
from wsgiref.simple_server import make_server

# URL for main crash submission
target_url = settings.mozcrash
# URLs for other crash services
other_urls = [settings.backtrace_url]

class CrashDiverter:
    def copy_post_remote(req, resp, resource):
        for url in other_urls:
            ans = requests.request(method='POST', url=url, files=resp.context.files, params=req.params)

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


app = falcon.App()

app.add_route('/submit', CrashDiverter())

if __name__ == '__main__':
    with make_server('', 8000, app) as httpd:
        print('Serving on port 8000...')
        httpd.serve_forever()
