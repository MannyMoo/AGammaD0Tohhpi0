from AnalysisUtils.Ganga import gaudi_exec_job, OptionsFile
from AnalysisUtils.Ganga import options_file as ana_options_file
import glob, os
from GangaCore.GPI import Dirac, SplitByFiles, DiracFile
# This doesn't currently work?
#import ROOT

optsdir = os.path.expandvars('$AGAMMAD0TOHHPI0ROOT/options/')

# Options file getter.
options_file = OptionsFile(optsdir)

# Real data options getter.
real_data_options = OptionsFile(options_file('data/real'))

# MC options dir
mc_data_options = OptionsFile(options_file('data/mc'))

def make_minibias():
    '''Make jobs on minibias data.'''
    import ROOT
    seed = 894982
    rand = ROOT.TRandom3(seed)
    frac = 0.05

    js = []
    for f in glob.glob(os.path.join(optsdir, 'data/minibias/*.py')) :
        if 'settings' in f :
            continue
        j = gaudi_exec_job(name = f.split(os.sep)[-1],
                           options = [os.path.join(optsdir, 'ntupling/minibias.py')],
                           backend = Dirac(),
                           splitter = SplitByFiles(filesPerJob = 10, ignoremissing = True),
                           outputfiles = [LocalFile('DVTuples.root')])
        # Select fraction of files at random.
        j.inputdata.files = filter(lambda f : rand.Rndm() < frac, j.inputdata.files)
        js.append(j)
    return js

def make_job(datafile):
    '''Make a job for the given data file.'''
    datafile = options_file(datafile)
    jobname = os.path.split(datafile)[1][:-3][:100]
    ismc = '_MC_' in datafile
    options = [options_file('ntupling/tuples.py'), ana_options_file('MessageSvcWideNames.py'),
               ana_options_file('Lumi.py')]
    filesperjob = 50
    if ismc:
        filesperjob = 10
        options.append(ana_options_file('VeloTrackAssoc.py'))
    j = gaudi_exec_job(jobname, datafile, options, backend = Dirac(),
                       splitter = SplitByFiles(filesPerJob = filesperjob),
                       outputfiles = [DiracFile('DaVinciTuples.root')])
    return j


def make_jobs(optsgetter = real_data_options):
    '''Make jobs for data files in the directory of the given options getter.'''
    js = []
    for datafile in optsgetter.data_files():
        j = make_job(datafile)
        js.append(j)
    return js

def make_mc_jobs():
    return make_jobs(mc_data_options)
