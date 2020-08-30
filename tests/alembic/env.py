import sys
from os.path import abspath, join
from os import getcwd, environ
from turbulette.alembic.env import run_migrations


# Add project folder to python path
sys.path.append(abspath(join(getcwd())))
run_migrations("tests.settings")
