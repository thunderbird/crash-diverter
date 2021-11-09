# URL to query API.
BT_API_URL = 'https://thunderbird.sp.backtrace.io/api'

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
