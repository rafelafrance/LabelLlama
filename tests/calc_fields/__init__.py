import logging

# Expected error-path logging (e.g. logging.error in job_runner)
# would otherwise print to stderr via the "last resort" handler.
# assertLogs captures on its own handler and is unaffected.
if not logging.getLogger().handlers:
    logging.getLogger().addHandler(logging.NullHandler())
