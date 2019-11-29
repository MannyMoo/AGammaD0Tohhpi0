from AnalysisUtils.Ganga import gaudi_exec_job, OptionsFile, get_output_lfns
from AnalysisUtils.Ganga import options_file as ana_options_file
import glob, os
from GangaCore.GPI import Dirac, SplitByFiles, DiracFile
# This doesn't currently work?
#import ROOT

# Options file getter.
optsdir = os.path.expandvars('$AGAMMAD0TOHHPI0ROOT/options/')
options_file = OptionsFile(optsdir)

# Real data options getter.
real_data_options = OptionsFile(options_file('data/real'))

# MC options dir
mc_data_options = OptionsFile(options_file('data/mc'))

# Python file getter.
pythondir = os.path.expandvars('$AGAMMAD0TOHHPI0ROOT/python/AGammaD0Tohhpi0/')
python_file = OptionsFile(pythondir)

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


def make_jobs(optsgetter = real_data_options, matchpatterns = ()):
    '''Make jobs for data files in the directory of the given options getter.'''
    js = []
    for datafile in optsgetter.data_files(matchpatterns = matchpatterns):
        j = make_job(datafile)
        js.append(j)
    return js

def make_mc_jobs(matchpatterns = ()):
    '''Make jobs for MC data.'''
    return make_jobs(mc_data_options, matchpatterns = matchpatterns)

def save_output_files(job):
    '''Save output LFNs and access URLs for the output files of the given job.'''
    name = job.name
    if 'MC' in name:
        mag = 'Up' if 'MagUp' in name else 'Down'
        name = 'MC_' + name[:name.index('MC')] + 'Mag' + mag
    outputdir = python_file('Datasets')
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    foutLFNs = os.path.join(outputdir, name + '_LFNs.py')
    foutURLs = os.path.join(outputdir, name + '_URLs.py')
    get_output_lfns(job, foutLFNs, foutURLs)
    
