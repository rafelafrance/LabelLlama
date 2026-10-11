import logging

# Keep expected error-path logging (e.g. logging.error in job_runner)
# from printing to stderr via the "last resort" handler.
# Tests that assert on logs use assertLogs, which captures on its own
# handler and is unaffected by this.
logging.getLogger().addHandler(logging.NullHandler())
