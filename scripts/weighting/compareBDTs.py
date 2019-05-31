import ROOT
ROOT.TH1.SetDefaultSumw2()

weighted = '/home/ppe/l/ldickson/MSci/detector_assymmetry_code/code_2_0_1_6/ProjectCode/D0Bar_weightapplied_mag{mag}{year}.root'
unweighted = {'15' : '/nfs/lhcb/d2hh01/hhpi0/data/2015/mag{mag}/unweighted_mag{mag}15_{flavour}.root',
              '16_nobdt' : '/home/ppe/l/ldickson/MSci/2016_datasets/D0_M_1825_1905_mag{mag}_Kpipi_2016.root',
              '16' : '/home/ppe/l/ldickson/MSci/detector_assymmetry_code/code_2_0_1_6/ProjectCode/BDT_ONLY_datasets/mag{mag}_2016/D0_Kpipi_mag{mag}_2016_BDT_ONLY.root'
              }

def plot_BDT(name, data, weight = False) :
    h = ROOT.TH1F(name, '', 100, data.get(0)['BDT'].getMin(), data.get(0)['BDT'].getMax())
    if weight :
        for i in xrange(data.numEntries()) :
            args = data.get(i)
            h.Fill(args['BDT'].getVal(), data.weight())
    else :
        for i in xrange(data.numEntries()) :
            args = data.get(i)
            h.Fill(args['BDT'].getVal())
    h.SetDirectory(None)
    h.Scale(1./h.Integral())
    return h

plots = []
for year in '15', '16', : # '16_nobdt' :
    for mag in 'down', 'up' : 
        f_d0 = ROOT.TFile.Open(unweighted[year].format(flavour = 'D0', mag = mag, year = year[:2]))
        f_d0bar = ROOT.TFile.Open(weighted.format(mag = mag, year = year[:2]))
        d0 = f_d0.Get('data')
        d0bar = f_d0bar.Get('data')
        print year, mag, 'N. D0:', d0.numEntries(), 'N D0bar:', d0bar.numEntries()
        h_d0 = plot_BDT('_'.join(['D0', mag, year]), d0)
        h_d0bar = plot_BDT('_'.join(['D0bar', mag, year]), d0bar)
        h_d0barweighted = plot_BDT('_'.join(['D0bar_weighted', mag, year]), d0bar, True)
        hratio = ROOT.TH1F(h_d0)
        hratio.SetName(hratio.GetName().replace('D0', 'ratio'))
        hratio.Divide(h_d0bar)
        hratio.SetLineWidth(3)
        hratio.SetDirectory(None)
        for h, c in (h_d0, ROOT.kBlack), (h_d0bar, ROOT.kBlue), (h_d0barweighted, ROOT.kRed) :
            h.SetLineWidth(3)
            h.SetLineColor(c)
        for h1, h2 in (h_d0, h_d0bar), (h_d0, h_d0barweighted) :
            canv = ROOT.TCanvas()
            leg = ROOT.TLegend(0.7, 0.7, 1., 1.)
            for h in h1, h2 :
                print h.GetName()
                leg.AddEntry(h, h.GetName())
            print h1.Chi2Test(h2, 'wwp')
            h1.Draw()
            h2.Draw('same')
            leg.Draw()
            plots.append([canv, leg, h1, h2])
        h2d = ROOT.TH2F('_'.join(['D0bar', mag, year, 'weight-vs-BDT']), '_'.join(['D0bar', mag, year, 'weight-vs-BDT']),
                        50, -0.1, 0.1, 50, 0.8, 1.2)
        h2d.SetDirectory(None)
        for i in xrange(d0bar.numEntries()) :
            args = d0bar.get(i)
            h2d.Fill(args['BDT'].getVal(), d0bar.weight())
        canv2 = ROOT.TCanvas()
        h2d.Draw('colz')
        hratio.Draw('same')
        plots.append([canv2, h2d, hratio])
