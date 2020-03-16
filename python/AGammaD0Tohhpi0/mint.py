from Mint2.utils import run_job, gen_time_dependent, gen_time_dependent_main
from Mint2.ConfigFile import ConfigFile
import os, ROOT
from AGammaD0Tohhpi0.data import workingdir, datadir, mintdatadir
from ROOT import DalitzEventPattern, TVector3, DalitzEvent
from ROOT.MINT import NamedParameterBase
from AnalysisUtils.treeutils import TreePVector, TreeFormula

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

def get_config_file_name(name, number = 0, zfill = 3) :
    '''Get the config file name for a generator job.'''
    return os.path.join(integratorsdir, name, str(number).zfill(zfill), 'config.txt')

def get_config(name, number = None, zfill = 3) :
    '''Get the config file for a generator job.'''
    if None == number :
        for number in xrange(100) :
            fname = get_config_file_name(name, number, zfill)
            if os.path.exists(fname) :
                return ConfigFile(fname)
        raise OSError("Couldn't find any configs for {0} {1}-{3}!".format(name, '0'.zfill(zfill), 
                                                                          str(number).zfill(zfill)))
    fname = get_config_file_name(name, number, zfill)
    return ConfigFile(fname)

def momentum(tree, partname, form = 'Dstr_FIT_{partname}P{comp}'):
    '''Get a TreeFormula for the 3-vector momentum for the given particle.'''
    return TreePVector(tree, partname, pform = form, comps = 'XYZ', vectclass = TVector3)

class TreeMomenta(object):
    def __init__(self, tree, parts = ['D', 'H1', 'H2', 'Pi0']):
        self._momenta = [momentum(tree, part) for part in parts]
        self.h1id = TreeFormula('H1_ID', 'H1_ID', tree)
        self.did = TreeFormula('D_ID', 'D_ID', tree)

    def __call__(self):
        momenta = [mom.vector() for mom in self._momenta]
        # Make sure pi+ momentum comes first.
        if self.h1id() < 0:
            momenta[1:3] = momenta[2:0:-1]
        return momenta

    def dalitz_event(self):
        vect = ROOT.vector('TVector3')()
        for mom in self():
            vect.push_back(mom)
        if self.did() < 0:
            return DalitzEvent(pattern_D0barTopipipi0, vect)
        return DalitzEvent(pattern_D0Topipipi0, vect)
        
