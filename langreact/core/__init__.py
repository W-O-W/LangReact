import logging
import os
if 'LANGREACT_LOGGING_CONF' not in os.environ:
    _path = os.path.dirname(__file__)
    logging.basicConfig(filename=os.path.join(_path,'configure','logging.conf'),level=logging.INFO)
else:
    logging.basicConfig(filename=os.environ['LANGREACT_LOGGING_CONF'])