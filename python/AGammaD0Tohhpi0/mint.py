from Mint2.utils import run_job, gen_time_dependent, gen_time_dependent_main
from Mint2.ConfigFile import ConfigFile
import os
from AGammaD0Tohhpi0.data import workingdir, datadir, mintdatadir
from ROOT import DalitzEventPattern
from ROOT.MINT import NamedParameterBase

integratorsdir = os.path.join(workingdir, 'integrators')
config = os.path.expandvars('$AGAMMAD0TOHHPI0ROOT/scripts/mint/pipipi0.txt')

pattern_D0Topipipi0 = DalitzEventPattern(421, 211, -211, 111)
pattern_D0barTopipipi0 = DalitzEventPattern(-421, 211, -211, 111)

def gen_pipipi0(name, configs = config, integratorsdir = integratorsdir, 
                mintdatadir = mintdatadir, **parameters) :
    '''Generate D0->pipipi0 MINT MC.'''

    parameters.update(locals())
    del parameters['parameters']
    gen_time_dependent(**parameters)

def gen_pipipi0_main() :
    '''Main function to generate D0->pipipi0 MINT MC, parsing arguments from the commandline.'''
    gen_time_dependent_main([config], integratorsdir, mintdatadir)

def set_default_config(config = config) :
    '''Set the default MINT config file.'''
    NamedParameterBase.setDefaultInputFile(config)
