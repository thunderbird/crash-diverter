from flask import Flask, render_template, request
from flask_assets import Environment, Bundle
import helpers
import morgue_api
import settings

application = Flask(__name__)
application.jinja_env.globals.update(settings=settings,
    **helpers.jinjafunctions, hex=hex, bool=bool)
for f in settings.FILTERS:
    application.jinja_env.filters[f] = helpers.jinjafunctions[f]

assets = Environment(application)
assets.url = application.static_url_path

@application.route("/report/<uuid>")
def view_report(uuid):
    api = morgue_api.APIHelper(uuid)
    report = api.get_results()

    # TODO: Put field descriptions in here.
    fields_desc = {}
    report['product'] = 'Thunderbird'
    report['uuid'] = uuid
    for attr in settings.REPORT_FIELDS:
        if attr not in report:
            report[attr] = None
        fields_desc[attr] = ''
    # Rename some of these from their Backtrace names.
    report['signature'] = report['callstack']['frame'][0]
    report['address'] = report['fault.address']

    return render_template(
        'report_index.html',
        fields_desc=fields_desc, raw = {}, report=report,
        parsed_dump = {}, public_raw_keys = []
    )


css = Bundle(
    'crashstats/css/base.less',
    # Below is only for the report index page.
    'crashstats/css/pages/report_index.less',
    'crashstats/css/components/tree.less',
    'jsonview/jsonview.custom.less',
    filters='less', output='css/crashstats-base.min.css'
)
assets.register('crashstats_base', css)

assets.register('base_js', Bundle(
    'crashstats/js/jquery/jquery.js',
    'crashstats/js/socorro/timeutils.js',
    'crashstats/js/socorro/nav.js',
    # Below is only for the report index page.
    'crashstats/js/socorro/report.js',
    filters='jsmin', output='js/crashstats-base.min.js'
))

if __name__ == '__main__':
      application.run(host='0.0.0.0', port=5000)
