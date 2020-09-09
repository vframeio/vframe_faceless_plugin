############################################################################# 
#
# VFRAME
# MIT License
# Copyright (c) 2020 Adam Harvey and VFRAME
# https://vframe.io 
#
#############################################################################

import os
from os.path import join
from pathlib import Path
import logging

from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

LOG = logging.getLogger('vframe')


# -----------------------------------------------------------------------------
#
# Filepaths
#
# -----------------------------------------------------------------------------

# Project directory
SELF_CWD = os.path.dirname(os.path.realpath(__file__))
DIR_PROJECT_ROOT = str(Path(SELF_CWD).parent)

# source .env vars if exists
fp_env = join(DIR_PROJECT_ROOT, '.env')
if Path(fp_env).is_file():
	load_dotenv(dotenv_path=fp_env)
