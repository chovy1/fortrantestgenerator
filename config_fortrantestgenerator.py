import os
import sys


### EDIT HERE ###

FTG_FOLDER = os.path.dirname(os.path.realpath(__file__))
FCG_FOLDER = FTG_FOLDER + '/../github-fortrancallgraph'
sys.path.append(FCG_FOLDER)

TEMPLATE_FOLDER = FCG_FOLDER + '/templates/standalone'
TEST_SOURCE_FOLDER = ''

#################

BACKUP_SUFFIX = 'ftg-backup'
FTG_PREFIX = 'ftg_'

#################

### Instead of importing config_fortrancallgraph, you can also configure those variables here, 
### just copy the structure from config_fortrancallgraph.py,

from config_fortrancallgraph import SPECIAL_MODULE_FILES, GRAPH_BUILDER, IGNORE_GLOBALS_FROM_MODULES, IGNORE_DERIVED_TYPES, EXCLUDE_MODULES  # @UnusedImport
from config_fortrancallgraph import SOURCE_FOLDER, SOURCE_FILES  # @UnusedImport
