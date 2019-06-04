from Mint2.utils import run_job
from Mint2.ConfigFile import ConfigFile
import os
from AGammaD0Tohhpi0.data import workingdir, datadir, mintdatadir

integratorsdir = os.path.join(workingdir, 'integrators')
config = '$AGAMMAD0TOHHPI0ROOT/scripts/mint/pipipi0.txt'

def gen_pipipi0(name, configs = config, integratorsdir = integratorsdir, 
                mintdatadir = mintdatadir, **parameters) :
    '''Generate D0->pipipi0 MINT MC.'''

    if isinstance(configs, str) :
        configs = [configs]
    config = ConfigFile(*configs, **parameters)
    outputdir = os.path.join(integratorsdir, name)
    if not os.path.exists(outputdir) :
        os.makedirs(outputdir)
    integsdir = os.path.join(outputdir, 'integrators')
    config['integratorsDirectory'] = [integsdir]

    datadir = os.path.join(mintdatadir, name)
    if not os.path.exists(datadir) :
        os.makedirs(datadir)
    config['outputFileName'] = [os.path.join(datadir, 'pipipi0.root')]

    run_job(exe = 'genTimeDependent.exe', workingdir = outputdir, configs = config,
            stdout = 'stdout', stderr = 'stdout')

def gen_pipipi0_main() :
    '''Main function to generate D0->pipipi0 MINT MC, parsing arguments from the commandline.'''
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('name', help = 'Name of the dataset to generate')
    parser.add_argument('--configs', nargs = '*', help = 'Config files to use', default = [config])
    parser.add_argument('--integratorsdir', help = 'Integrators directory', default = integratorsdir)
    parser.add_argument('--mintdatadir', help = 'Directory to save generated data', default = mintdatadir)
    
    args, remainder = parser.parse_known_args()
    variableslists = {}
    for arg in remainder :
        if arg.startswith('--') :
            varargs = []
            variableslists[arg[2:]] = varargs
            continue
        varargs.append(arg)

    gen_pipipi0(name = args.name, configs = args.configs, integratorsdir = args.integratorsdir,
                mintdatadir = args.mintdatadir, **variableslists)
