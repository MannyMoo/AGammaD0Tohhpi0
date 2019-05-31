#!/usr/bin/env python
import ROOT

unweighted = {'16_magup' : (5.920, 3.516),
              '16_down' : (-4.295, 2.6752),
              '15_up' : (-5.223, 6.622),
              '15_down' : (-5.574, 5.661)}

weighted = {'16_up' : (-6.43, 3.52),
            '16_down' : (-0.695, 2.681),
            '15_up' : (-6.252, 6.626),
            '15_down' : (-2.862, 5.676)}

def compatibility(vals) :
    n = 0
    chi2 = 0.
    for val, err in vals.values() :
        n += 1
        chi2 += (val/err)**2
    print 'Chi2/ndf: {0:.2f}/{1:d}, P = {2:.3f}'.format(chi2, n, ROOT.TMath.Prob(chi2, n))

for vals, name in (unweighted, 'unweighted'), (weighted, 'weighted') :
    print name
    compatibility(vals)
    for year in '15', '16' :
        print name, year
        compatibility({k : v for k, v in vals.items() if k.startswith(year)})
