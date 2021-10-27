from flask import Flask, render_template, request
from flask_assets import Environment, Bundle
import settings


application = Flask(__name__)
assets = Environment(application)

@application.route("/report/<uuid>")
def view_report(uuid):
    for attr in settings.report_fields:
        report[attr] = ''
    report['product'] = 'Thunderbird'
    report['uuid'] = uuid
    bh_url = ''

    return render_template('crashstats/report_index.html', report=report, buildhub_url=bh_url)


assets.register('crashstats_base',
    Bundle('crashstats/css/base.less',
    filters='less', output='css/crashstats-base.min.css')
)

if __name__ == '__main__':
      application.run(host='0.0.0.0', port=5000)
