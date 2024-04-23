import logging
import logging.config
import os
if 'LANGREACT_LOGGING_CONF' not in os.environ:
    _path = os.path.dirname(__file__)
    logging.config.fileConfig(fname=os.path.join(_path,'configure','logging.conf'))
else:
    logging.config.fileConfig(fname=os.environ['LANGREACT_LOGGING_CONF'])