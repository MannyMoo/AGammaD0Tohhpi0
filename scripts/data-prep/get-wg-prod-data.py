#!/usr/bin/env python

import os, glob, pprint
from AnalysisUtils.diracutils import get_access_urls

fdata = os.path.join(os.environ['AGAMMAD0TOHHPI0ROOT'], 'scripts', 'data-prep', 'wgprods.txt')
with open(fdata) as f:
    lines = f.readlines()[2:]
paths = {}
for line in lines:
    line = line.split()
    splitname = line[2].split('_')
    mag = splitname[-1]
    year = splitname[1].split('-')[-1]
    name = 'RealData_{0}_Charm_{1}'.format(year, mag)
    paths[name] = line[-1]
datadir = os.path.join(os.environ['AGAMMAD0TOHHPI0ROOT'], 'python', 'AGammaD0Tohhpi0', 'Datasets')
for name, path in paths.items():
    files = glob.glob(path)
    lfns = ['/' + '/'.join(f.split('/')[5:]) for f in files]
    lfnsfile = os.path.join(datadir, name + '_LFNs.py')
    with open(lfnsfile, 'w') as f:
        f.write('lfns = ' + pprint.pformat(lfns).replace('\n', len('lfns = ') * ' ' + '\n') + '\n')
    urlsfile = os.path.join(datadir, name + '_URLs.py')
    get_access_urls(lfns, urlsfile)
