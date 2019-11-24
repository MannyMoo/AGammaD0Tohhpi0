from AnalysisUtils.Ganga import gaudi_exec_job
import glob, os, ROOT

optsdir = os.path.expandvars('$AGAMMAD0TOHHPI0ROOT/options/')
anaoptsdir = os.path.expandvars('$ANALYSISUTILSROOT/options/')

def options_file(fname, optsdir = optsdir):
    '''Get an options file path.'''
    if not os.path.isabs(fname):
        return os.path.join(optsdir, fname)
    return fname

def ana_options_file(fname):
    '''Get an options file path from AnalysisUtils.'''
    return options_file(fname, anaoptsdir)

def make_minibias():
    '''Make jobs on minibias data.'''
    seed = 894982
    rand = ROOT.TRandom3(seed)
    frac = 0.05

    js = []
    for f in glob.glob(os.path.join(optsdir, 'data/minibias/*.py')) :
        if 'settings' in f :
            continue
        j = gaudi_exec_job(name = f.split(os.sep)[-1],
                           options = [os.path.join(optsdir, 'ntupling/minibias.py')]
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
    options = [options_file('ntupling/tuples.py'), ana_options_file('MessageSvcWideNames.py')]
    filesperjob = 50
    if ismc:
        filesperjob = 10
        options.append(ana_options_file('VeloTrackAssoc.py'))
    j = gaudi_exec_job(jobname, datafile, options, backend = Dirac(),
                       splitter = SplitByFiles(filesPerJob = filesperjob),
                       outputfiles = [DiracFile('DaVinciTuples.root')])
    return j


