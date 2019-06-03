from Mint2.utils import run_job
from Mint2.ConfigFile import ConfigFile
import os

config = ConfigFile('$AGAMMAD0TOHHPI0ROOT/scripts/mint/pipipi0.txt')
outputdir = os.path.expandvars(config.parameters['integratorsDirectory'])
config.parameters['integratorsDirectory'] = os.path.join(outputdir, 'integrators')
if not os.path.exists(outputdir) :
    os.makedirs(outputdir)
run_job('genTimeDependent.exe', outputdir, config)
