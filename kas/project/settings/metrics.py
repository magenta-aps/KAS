import os
from distutils.util import strtobool

# Skip health_check for cache layer since we are not using it
WATCHMAN_CHECKS = ("watchman.checks.databases", "watchman.checks.storage")
# skip checking of oracle database
WATCHMAN_DATABASES = ["default"]

METRICS = {
    # used to disable metrics in the pipeline
    "disable": bool(strtobool(os.environ.get("DISABLE_METRICS", "False"))),
}
