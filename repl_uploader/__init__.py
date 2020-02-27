# -*- coding: utf-8 -*-
"""Interface to generate "Replicon" expense sheets and to generate report requests."""

import logging
from .replicon import Replicon

VERSION = "2.0.11"
__AUTHOR__ = "Thiago Weidman (tw@weidman.com.br)"
__COPYRIGHT__ = "(C) 2014-2019 Thiago Weidman. GNU GPL 3 or later."

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())
