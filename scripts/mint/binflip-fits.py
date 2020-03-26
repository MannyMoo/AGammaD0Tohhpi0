from AGammaD0Tohhpi0.data import datalib
from AGammaD0Tohhpi0.binflip import BinFlipFitter
import os

def test():
    '''Test blinding on some MINT data.'''
    timebins41 = [round(0.1*i, 10) for i in xrange(42)]
    binningname41 = 'TimeBins41'
    lifetime = 0.4101
    data3pi = 'MINT_data_worldAv_1M_noExpEff_cp'

    datainfo = datalib.get_data_info(data3pi)
    datainfo = dict(datainfo, files = datainfo['files'][:1])
    dataname = data3pi + '_' + os.path.split(datainfo['files'][0])[1]
    datalib.make_getters({dataname : datainfo})

    fpars3pi = os.path.expandvars('$AGAMMAD0TOHHPI0WORKINGDIR/hadronicParameters/pipipi0-8bins-10M/hadronicParameters.txt')

    fname = os.path.join(datalib.dataset_dir(dataname), dataname + '_' + binningname41 + '.txt')

    fitter = BinFlipFitter(datalib, dataname, 
                           #timebins41, 
                           fname,
                           lifetime = lifetime, hadronicparsfile = fpars3pi,
                           binningname = binningname41)
    chi2unblind, miniunblind = fitter.do_fit('unblind')
    chi2blind, miniblind = fitter.do_fit('blind', blindingseed = 1)
    return locals()

def real_data():
    '''Run the binflip fit on real data.'''
    timebins = '/home/ppe/n/nmchugh/SummerProject/DaVinciDev_v44r10p1/AGammaD0Tohhpi0/scripts/pipipi0_binflip/timebinning.txt'
    hadronicparsfile = os.path.expandvars('$AGAMMAD0TOHHPI0WORKINGDIR/hadronicParameters/pipipi0-8bins-10M-3body/hadronicPars_and_config.txt')
    fitter = BinFlipFitter(datalib, 
                           # The name doesn't really matter, it's just where the config file will be saved.
                           dataname = 'RealData_2015_Charm_MagDown_pipipi0_Merged_TriggerFiltered', 
                           timebins = timebins,
                           lifetime = 0.4101, binningname = 'timebinning', hadronicparsfile = hadronicparsfile)
    binflipchi2, minimiser = fitter.do_fit('fit_results')
    return locals()

if __name__ == '__main__':
    #globals().update(test())
    globals().update(real_data())
