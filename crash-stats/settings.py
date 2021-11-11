from flask_assets import Bundle

# Base URL to the Backtrace API.
BT_API_URL = 'https://thunderbird.sp.backtrace.io/api'

# URL for API login.
BT_LOGIN_URL = BT_API_URL + '/login'

# URL for doing queries.
BT_QUERY_URL = BT_API_URL + '/query?token={token}&universe=thunderbird&project=Thunderbird'

# URL to link directly to a crash in Backtrace.
BT_CRASH_URL = 'https://thunderbird.sp.backtrace.io/p/Thunderbird/triage?filters=((crashid,contains,{uuid}))'

# URL to Mozilla BuildHub.
BUILDHUB_URL = 'https://buildhub.moz.tools/'

# Name of DynamoDB Table.
DYNAMO_TABLE = 'crash_stats'

# List of data fields to pull from Backtrace.
REPORT_FIELDS = [
    "Accessibility", "AdapterDeviceID", "AdapterDriverVendor", "AdapterDriverVersion",
    "Add-ons", "AsyncShutdownTimeout", "AvailablePageFile", "AvailablePhysicalMemory",
    "AvailableVirtualMemory", "buildid", "callstack", "callstack.functions",
    "cpu.count", "CrashTime", "EMCheckCompatibility", "fault.address", "InstallTime",
    "MozCrashReason", "OOMAllocationSize", "os_name", "os_version", "ReleaseChannel",
    "SecondsSinceLastCrash", "StartupCrash", "SystemMemoryUsePercentage", "timestamp.received",
    "TotalVirtualMemory", "UptimeTS", "version", "WindowsErrorReporting"
]

FILTERS = ['timestamp_to_date', 'human_readable_iso_date']


SITE_CSS = Bundle(
    'crashstats/css/base.less',
    # Below is only for the report index page.
    'crashstats/css/pages/report_index.less',
    'crashstats/css/components/tree.less',
    'jsonview/jsonview.custom.less',
    filters='less', output='css/crashstats-base.min.css'
)

SITE_JS = Bundle(
    'crashstats/js/jquery/jquery.js',
    'crashstats/js/socorro/timeutils.js',
    'crashstats/js/socorro/nav.js',
    # Below is only for the report index page.
    'crashstats/js/socorro/report.js',
    filters='jsmin', output='js/crashstats-base.min.js'
)
