import ROOT
from ROOT import TCanvas, TLine, TLegend
import pickle as pkl

ROOT.gStyle.SetOptStat(0)
#ROOT.gROOT.SetBatch(True)

nbins, dmmin, dmmax = 100, 140., 155.

with open('resolved_tree.pkl', 'rb') as f:
     tree = pkl.load(f)

canv = TCanvas('canv', 'Selection Cut Plot')
def draw(picut = -0.75, Dstrcut = 2.5, Dcut = 2., bdtcut = -999., diracut =  999., title = False):
    sel = 'pi0_CosTheta > {} && log(Dstr_FDCHI2_OWNPV) < {} && log(D_IPCHI2_OWNPV) < {} && BDT.BDT > {} && acos(D_DIRA_OWNPV) < {}'.format(picut, Dstrcut, Dcut, bdtcut, diracut) 
    basesel = 'Dstr_FIT_DM > 1850 && Dstr_FIT_DM < 1880'

    tree.Draw('deltam >> hnocut({0}, {1}, {2})'.format(nbins, dmmin, dmmax), basesel, 'pe')
    tree.Draw('deltam >> hpass({0}, {1}, {2})'.format(nbins, dmmin, dmmax), basesel+' && '+sel, 'pe same')
    tree.Draw('deltam >> hfail({0}, {1}, {2})'.format(nbins, dmmin, dmmax), basesel+' && !('+sel+')'.format(bdtcut), 'pe same')

    hnocut = ROOT.gDirectory.Get('hnocut')
    hpass = ROOT.gDirectory.Get('hpass')
    hfail = ROOT.gDirectory.Get('hfail')

    hnocut.SetTitle(sel) if title else hnocut.SetTitle('')
    hnocut.GetYaxis().SetRangeUser(0, hnocut.GetMaximum()*1.2)
    ytitle = 'Events / ({0:.2f} MeV)'.format( (dmmax-dmmin)/nbins ) 
    hnocut.GetYaxis().SetTitle(ytitle)   
    hnocut.GetYaxis().SetTitleOffset(1.2)
    hnocut.GetYaxis().SetTitleSize(0.04)
    hnocut.GetXaxis().SetTitle('#Delta m (MeV)')
    hnocut.GetXaxis().SetTitleOffset(1.1)
    hnocut.GetXaxis().SetTitleSize(0.04)
 
    hpass.SetLineColor(ROOT.kGreen+1)
    hfail.SetLineColor(ROOT.kRed+1)
    
    hnocut.SetLineWidth(3)
    hpass.SetLineWidth(3)
    hfail.SetLineWidth(3)
   
    legend = TLegend(0.6,0.6, 0.85,0.8)    
    legend.AddEntry(hnocut, 'No Cut', 'pe')
    legend.AddEntry(hpass, 'Pass', 'pe')
    legend.AddEntry(hfail, 'Fail', 'pe')
    legend.Draw()
    canv.Update()
    return hnocut, legend

stuff = draw()

