import sys
from os.path import abspath, join
from os import getcwd
from turbulette.management.alembic_env import run_migrations


# Add project folder to python path
sys.path.append(abspath(join(getcwd())))
run_migrations("tests.settings")
