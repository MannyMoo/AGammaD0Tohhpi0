#!/usr/bin/env python

from AnalysisUtils.plot import plot_fit, goodcolours
from AnalysisUtils.fit import translate_and_scale_pdf
import ROOT
from ROOT import RooFit

RESOLVED_TRAIN_DATANAME = 'RealData_2015_Charm_MagDown_pipipi0_Resolved_TriggerFiltered'  
MERGED_TRAIN_DATANAME = 'RealData_2017_Charm_MagUp_pipipi0_Merged_TriggerFiltered'  

RESOLVED_SEL = 'log(D_IPCHI2_OWNPV) < 2. && log(Dstr_FDCHI2_OWNPV) < 2.5 && '\
               'Dstr_FIT_CHI2 >= 0 && Dstr_FIT_CHI2 < 30 && inrange_all'
MERGED_SEL = 'Dstr_FIT_CHI2 >= 0 && Dstr_FIT_CHI2 < 30 && inrange_all'

def reduce_dataset_name(name):
    """ Produces simple {year}_{mag}_{resolved|merged} string from dataset name
        for producing simpler output file names.
    """
    year = [y for y in ['2015', '2016', '2017', '2018'] if y in name][0]
    mag = [m for m in ['Up', 'Down'] if m in name][0]
    pi0cat = [c for c in ['Merged', 'Resolved'] if c in name][0]
    return year + '_' + mag + '_' + pi0cat

def set_plot_opts(stuff, name):
    """ Sets some plot options for deltam and pulls plot
    """
    data = stuff['hdata']
    pull = stuff['pullHist']
    canv = stuff['canv']

    data.GetXaxis().SetTitle("#Delta m (MeV)")
    data.GetXaxis().SetTitleOffset(1.)
    
    pull.GetYaxis().SetTitleSize(0.3)
    pull.GetYaxis().SetTitleOffset(0.15)
    data.GetYaxis().SetTitleSize(0.08)
    data.GetYaxis().SetTitleOffset(0.7)
            
    canv.SetName(name)
    canv.SetTitle(name[-5:])
    canv.Update()
 
class DmFitter3Pi(object):
    """
    Class for fitting deltam distribution from D0->pi+pi-pi0, in bins of D0 mass.
    """
    def __init__(self, datalib, dataname, sig_pdf, bg_pdf, workspace, mcdataname = 'MC_2016_pipipi0', 
                 selection = "Dstr_FIT_CHI2 >= 0 && Dstr_FIT_CHI2 < 30", suffix = '_pre_bdt', update = False):
        """ I really should think about whether its necessary to pass sig/bg pdfs
            or just build them then pass the workspace. Reads in specified dataset (with selection)
            builds the simultaneous total/signal pdfs in bins of D0 mass.
        """
        self.datalib = datalib
        self.dataname = dataname
        self.realmassbins = self.datalib.get_deltam_in_mass_bins_dataset(dataname, suffix = suffix, selection = selection, updatedataset = update)
        self.mcmassbins = self.datalib.get_deltam_in_mass_bins_dataset(mcdataname)

        self.workspace = workspace
        self.sig_pdf = sig_pdf
        self.bg_pdf = bg_pdf

        self.dm = workspace.roovar('deltam')
        self._build_pdfs()

    def _build_sig_pdf(self):
        # signal shape fixed by central bin
        cats = sorted(self.mcmassbins.catvals)
        corecat = cats[(len(cats)-1)/2]
        cats.remove(corecat)

        gauss = self.workspace.factory('Gaussian::gauss(deltam, mean[145.4], sigma[0.3, 0., 1.])')
        sigmacoeff = self.workspace.roovar('sigmacoeff', val = 3., xmin = 1., xmax = 4.)
        self.workspace.factory('expr', 'lambda', '"sigma * sigmacoeff"', self.workspace.roovar('sigma'), sigmacoeff)
        johnson = self.workspace.factory('Johnson::johnson(deltam, mean, lambda, gamma[-0.5,0.5], delta[1.])')

        self.set_constant(['mean'], flag=False)
        self.mcpdfs[corecat] = self.workspace.factory('RSUM::sig_pdf(frac_core[0.,1.]*gauss, johnson)')
        self.sig_pdf = self.mcpdfs[corecat]        

        # for the other bins
        for i, cat in enumerate(cats):
            name = 'dm_pdf_' + str(i)
            self.workspace.factory('Gaussian::gauss_'+name+'(deltam, mean[145.4], sigma_'+name+'[0.3, 0., 1.])')
            pdf = self.workspace.factory('RSUM::sig_pdf_'+name+'(frac_core_'+name+'[0.,1.]*gauss_'+name+', johnson)')
            self.mcpdfs[cat] = pdf
        self.mcsimul = self.mcmassbins.make_roosimultaneous(self.mcpdfs)

    def _build_sig_pdf_OLD(self):
        # signal shape fixed by central bin
        cats = sorted(self.mcmassbins.catvals)
        corecat = cats[(len(cats)-1)/2]
        cats.remove(corecat)
        self.mcpdfs[corecat] = self.sig_pdf
        
        # for the other bins
        for i, cat in enumerate(cats):
            name = 'dm_pdf_' + str(i)
            trans = self.workspace.roovar(name + '_translation', val = 0., error = 0.1, xmin = -10., xmax = 10.)
            scale = self.workspace.roovar(name + '_scale', val = 1.1, error = 0.05, xmin = 0.8, xmax = 5.)
            pdf = translate_and_scale_pdf(self.workspace, self.sig_pdf, name, self.dm, trans, scale,
                                          self.workspace.roovar('mean'))
            self.mcpdfs[cat] = pdf
        
        self.mcsimul = self.mcmassbins.make_roosimultaneous(self.mcpdfs)

    def fit_mc_data(self, constants = []):
        if constants : self.set_constant(constants, flag = True)
        self.mc_fitresult = self.mcsimul.fitTo(self.mcmassbins.datahist, RooFit.PrintLevel(-1), RooFit.Save(True))
        self.mc_fitresult.Print()
        if constants : self.set_constant(constants, flag = False)
        return self.mc_fitresult 

    def _build_real_pdf(self):
        # getting category vals for d0 mass bins
        mccats = sorted(self.mcmassbins.catvals)
        realcats = sorted(self.realmassbins.catvals)
        
        # construct total pdf in each region by adding bg and signal pdf (fitted in each region from mc data) 
        for i, cat in enumerate(mccats):
            Ntot = self.realmassbins.datasets[realcats[i]].sumEntries()
            Nbg = self.workspace.roovar("Nbg_"+str(i), xmin = 0., xmax = Ntot)
            Nsig = self.workspace.roovar("Nsig_"+str(i), xmin = 0., xmax = Ntot)
            pdf = self.workspace.factory("SUM", "total_pdf_"+str(i), *[Nbg.GetName() + "*bg_pdf", Nsig.GetName() + "*" + self.mcpdfs[cat].GetName()])
            self.realpdfs[realcats[i]] = pdf
            
        self.real_simul = self.realmassbins.make_roosimultaneous(self.realpdfs)
       
    def get_Nevents(self, sig = True):
        etype = 'sig' if sig else 'bg'
        return int(sum( [self.workspace.roovar('N'+etype+'_'+str(i)).getVal() for i in range(len(self.realpdfs))] ))

    def get_purity(self, windowsize = 2.):
        nsig, nbg = 0., 0.
        for catval in sorted(self.mcpdfs.keys()):
            sigint = self.integral(pdf = self.mcpdfs[catval], name = catval, windowsize = 2., windowpdf = self.mcpdfs[catval])
            bgint = self.integral(pdf = self.bg_pdf, name = catval, windowsize = 2., windowpdf = self.mcpdfs[catval])
            nsig += self.workspace.roovar('Nsig_'+catval[-1]).getVal() * sigint
            nbg += self.workspace.roovar('Nbg_'+catval[-1]).getVal() * bgint
        return nsig, nsig / (nsig+nbg)

    def fit_real_data(self, constants = [], printlevel = -1):
        if constants : self.set_constant(constants, flag = True)
        self.real_fitresult = self.real_simul.fitTo(self.realmassbins.datahist, RooFit.PrintLevel(printlevel), 
                                                    RooFit.Save(True), RooFit.Offset(True))
        self.real_fitresult.Print()
        if constants : self.set_constant(constants, flag = False)
        return self.real_fitresult
 
    def update_dataset(self, dataname, selection = "Dstr_FIT_CHI2 >= 0 && Dstr_FIT_CHI2 < 30", suffix = '_pre_bdt', update = False):
        self.dataname = dataname
        self.realmassbins = self.datalib.get_deltam_in_mass_bins_dataset(dataname, suffix = suffix, selection = selection, updatedataset = update)
        self._build_pdfs() 

    def _build_pdfs(self):
        self.mcpdfs, self.realpdfs = {}, {}
        self._build_sig_pdf()
        self._build_real_pdf()       
 
    def set_constant(self, varlist, flag = True):
        for v in varlist:
            self.workspace.roovar(v).setConstant(flag)

    def plot_real_fit(self, comps = {}, save = False, plotdir = '', filesuffix = ''):
        # need this since signal pdfs are currently defined by mc categories which we don't loop over 
        realcats = sorted(self.realmassbins.catvals)
        suffix = {realcats[0]: "_dm_pdf_0",
                  realcats[1]: "",
                  realcats[2]: "_dm_pdf_1"} 
        allstuff = []
        for cat, hist in self.realmassbins.datasets.items():
            components = [  [ RooFit.Name("Total") ],
                            [ RooFit.Components("bg_pdf"), RooFit.Name("BG"), RooFit.LineColor(ROOT.kGreen+2) ], 
                            [ RooFit.Components("sig_pdf"+suffix[cat]), RooFit.Name("Signal"), RooFit.LineColor(ROOT.kRed+2) ]]
            for i, (comp, name) in enumerate(comps.items()):
                components += [[ RooFit.Components(comp+suffix[cat]), RooFit.Name(name), RooFit.LineColor(goodcolours[i+4]) ]]

            stuff = plot_fit(self.realpdfs[cat], hist, components=components)
            set_plot_opts(stuff, cat)

            if save: 
                stuff['canv'].SaveAs('plots/'+plotdir+reduce_dataset_name(self.dataname)+'_'+cat[-5:]+filesuffix+'.pdf')
                self.real_fitresult.SaveAs('plots/'+plotdir+reduce_dataset_name(self.dataname)+'_'+cat[-5:]+filesuffix+'.root')

            allstuff.append(stuff)
        return allstuff # messy but stops crashes due to ROOT/Python deletion clashes

 
    def get_signal_significance(self, windowsize = 3.):
        ''' Rough implementation of signal significance. Uses only central bin for now. TODO: figure out 
            how to calculate integrals in the translated/scaled outer bins. 
        '''
 
        Nsig = self.workspace.roovar('Nsig_1').getVal()
        Nbg = self.workspace.roovar('Nbg_1').getVal()

        sigint = self.integral(pdf = self.sig_pdf, windowsize = windowsize)
        bgint = self.integral(pdf = self.bg_pdf, windowsize = windowsize)

        return Nsig*sigint / (Nsig*sigint + Nbg*bgint)**0.5
   
    def get_mean_window(self, pdf, size = 3.):
        ''' Returns limits of a window given by mean +- size * sigma
        '''
        sigma = self.sig_pdf.sigma(self.dm).getVal()
        mean = self.sig_pdf.mean(self.dm).getVal()
        return (mean-size*sigma, mean+size*sigma) 

    def integral(self, pdf = None, name = 'sig', windowsize = 2., windowpdf = None):
        ''' Calculate integral of given p.d.f. about mean, in window of width +- sigma*sigmawindow.
            Sigma and mean are taken from window p.d.f.
        '''
        if not pdf : pdf = self.sig_pdf
        if not windowpdf : windowpdf = self.sig_pdf

        meanwindow = self.get_mean_window(windowpdf, size = windowsize)

        self.dm.setRange(name, meanwindow[0], meanwindow[1])
        dmset = ROOT.RooArgSet(self.dm)
        normset = RooFit.NormSet(dmset) # need to do this to normalise p.d.f. over dm range 

        return pdf.createIntegral(dmset, normset, RooFit.Range(name)).getVal()


    def get_chi2(self):
        return self.real_simul.createChi2(self.realmassbins.datahist).getVal()

    def get_sigmas(self):
        return [(pdf.sigma(self.dm).getVal(), pdf.sigma(self.dm).getPropagatedError(self.real_fitresult)) for pdf in self.mcpdfs.values()]

