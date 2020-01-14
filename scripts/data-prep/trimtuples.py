#!/usr/bin/env python

import os, ROOT, shutil, glob, subprocess
from AnalysisUtils.treeutils import copy_tree, is_tfile_ok
from AGammaD0Tohhpi0.data import datadir, datalib, filtereddatadir
from AnalysisUtils.addmva import make_mva_tree
from AGammaD0Tohhpi0.selection import bdtcut, bdtsel, add_bdt_kinematic, selections, MC_sels, AND, trigger_filter
from time import sleep
import multiprocessing

def trim_file(infile) :
    removebranches = ('lab[0-9]_MC12TuneV[0-9]_ProbNN',
                      'lab[0-9]_ProbNN',
                      'lab[0-9]_PID',
                      'lab0_DTF_vtx_DstMass',
                      'lab0_DTF_vtx_BothMass',
                      'lab0_DTF_DstMass',
                      'lab0_DTF_D0Mass',
                      'lab0_DTF_BothMass',
                      'lab[0-9]_hasMuon',
                      'lab[0-9]_isMuon',
                      'lab[0-9]_hasRich',
                      'lab[0-9]_UsedRich',
                      'lab[0-9]_RichAbove',
                      'lab[0-9]_hasCalo')

    outfile = ROOT.TFile.Open(infile + '.trim', 'recreate')
    infile = ROOT.TFile.Open(infile)
    for k in infile.GetListOfKeys() :
        if 'KK' in k.GetName() or 'WIDEMASS' in k.GetName() :
            continue
        outfile.mkdir(k.GetName())
        outfile.cd(k.GetName())
        for tname in infile.Get(k.GetName()).GetListOfKeys() :
            print 'Copy tree', k.GetName() + '/' + tname.GetName()
            tcopy = copy_tree(infile.Get(k.GetName() + '/' + tname.GetName()), removebranches = removebranches)
            tcopy.Write()
        outfile.cd()

    outfile.Close()
    infile.Close()
    shutil.move(outfile.GetName(), infile.GetName())

def trim_2015_tuples() :
    files = glob.glob(os.path.join(datadir, 'data', '2015', '*', 'DaVinciTuples_*_Data.root'))
    nfiles = '/' + str(len(files))
    for i, f in enumerate(files) :
        print str(i+1) + nfiles, f
        trim_file(f)

def filter_tuple_mva(inputtree, weightsfile, weightsvar, outputfile, cut) :
    print 'Calculate MVA variable for tree', inputtree.GetName()
    make_mva_tree(inputtree, weightsfile, weightsvar, weightsvar + 'Tree', outputfile + '.weights')
    mvafile = ROOT.TFile.Open(outputfile + '.weights')
    mvatree = mvafile.Get(weightsvar + 'Tree')
    evtlist = ROOT.TEventList('evtlist')
    sel = weightsvar + ' >= ' + str(cut)
    mvatree.Draw('>>' + evtlist.GetName(), sel)
    inputtree.SetEventList(evtlist)
    mvatree.SetEventList(evtlist)
    fout = ROOT.TFile.Open(outputfile, 'recreate')
    print 'Filter tree', inputtree, 'with selection', sel
    treeout = inputtree.CopyTree('')
    mvatreeout = mvatree.CopyTree('')
    fout.Write()
    fout.Close()
    print 'Wrote file', outputfile

def filter_2016_tuples(overwrite = False) :
    weightsfile = os.path.expandvars('$AGAMMAD0TOHHPI0ROOT/tmva/20180702-Lewis/TMVAClassification_BDT_Kpipi0.weights.xml')
    for mag in 'Up', 'Down' :
        print 'Filter Mag' + mag, 'files'
        datainfo = datalib.get_data_info('Data_2016_Kpipi0_Mag' + mag + '_full')
        outputdir = os.path.join(datadir, 'data', '2016', 'mag' + mag.lower())
        if not os.path.exists(outputdir) :
            os.makedirs(outputdir)
        mod2016 = __import__('AGammaD0Tohhpi0.Reco16_Charm_Mag{0}_TupleURLs'.format(mag), fromlist = ['urls'])
        nok = 0
        for lfn, urls in mod2016.urls.items() :
            print 'Process LFN', lfn
            outputfile = os.path.join(outputdir, lfn[1:].replace('/', '_').replace('.root', '_Kpipi0.root'))
            if not overwrite and os.path.exists(outputfile) and is_tfile_ok(outputfile) :
                print 'Output already exists, skipping'
                nok += 1
                continue
            if not urls :
                continue
            ok = False
            # Find a URL that works.
            for url in urls :
                if is_tfile_ok(url) :
                    ok = True
                    break
            if not ok :
                print 'No working URL'
                continue
            inputfile = ROOT.TFile.Open(url)
            tree = inputfile.Get(datainfo['tree'])
            if not tree :
                print 'No tree named {0!r} in file {1}'.format(datainfo['tree'], url)
                continue
            nok += 1
            filter_tuple_mva(tree, weightsfile, 'BDT', outputfile, bdtcut)
        print 'Successfully filtered', str(nok) + '/' + str(len(mod2016.urls)), 'files'

def add_mvas_2015() :
    for finalstate in 'pipi', : # 'Kpi' :
        # Merged doesn't work currently cause the BDT expects lab6&7 to be the photons.
        for pi0 in 'Resolved', : # 'Merged' :
            for mag in 'Up', 'Down' :
                dataset = 'Data_2015_{finalstate}pi0_{pi0}_Mag{mag}_full'.format(**locals())
                print dataset
                add_bdt_kinematic(datalib, dataset)

def filter_2015_pipi() :
    sels = {'Resolved' : {'' : selection_R,
                          '_LowMass' : selection_R_low,
                          '_HighMass' : selection_R_high},
            'Merged' : {}}
    for finalstate in 'pipi', : # 'Kpi' :
        # Merged doesn't work currently cause the BDT expects lab6&7 to be the photons.
        for pi0 in 'Resolved', : # 'Merged' :
            for mag in 'Up', 'Down' :
                dataset = 'Data_2015_{finalstate}pi0_{pi0}_Mag{mag}_full'.format(**locals())
                print dataset
                info = datalib.get_data_info(dataset)
                tree = datalib.get_data(dataset)
                for suff, sel in sels[pi0].items():
                    outputname = dataset.replace('_full', suff)
                    print outputname
                    outputdir = os.path.join(filtereddatadir, outputname)
                    if not os.path.exists(outputdir) :
                        os.makedirs(outputdir)
                    outputfile = os.path.join(outputdir, outputname + '.root')
                    fout = ROOT.TFile.Open(outputfile, 'recreate')
                    treeout = copy_tree(tree, sel, write = True)
                    fout.Close()

def offline_filter(sel = bdtsel, match = '.*Resolved_TriggerFiltered', 
                   rename = (lambda name : name.replace('TriggerFiltered', 'OfflineFiltered')),
                   nthreads = multiprocessing.cpu_count()):
    pool = Pool(processes = nthreads)
    procs = []
    datasets = datalib.get_matching_datasets(match)
    for dataset in datasets:
        newname = rename(dataset)
        print dataset, '->', newname
        outputdir = os.path.join(filtereddatadir, newname)
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        fout = os.path.join(outputdir, newname + '.root')
        tree = datalib.get_data(dataset)
        #copy_tree(tree = tree, selection = sel, fname = fout, write = True)
        proc = pool.apply_async(copy_tree, kwds = dict(tree = tree, selection = sel, fname = fout, write = True))
        procs.append(proc)
    for proc, dataset in zip(procs, datasets):
        proc.wait()
        print dataset, proc.successful()

def add_kinematic_mva(match = '.*Resolved_TriggerFiltered'):
    threads = []
    for dataset in datalib.get_matching_datasets(match):
        print dataset
        args = (datalib, dataset)
        thread = Process(target = add_bdt_kinematic, args = (datalib, dataset))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

def filter_all_trigger(overwrite = True):
    # trigger_filter(datalib, 'pipipi0_DecProdCut_PHSP_2016_MC_MagUp_pipipi0_Resolved')
    datasets = filter(lambda x : x.endswith('Merged') or x.endswith('Resolved'), datalib.get_matching_datasets('RealData_201.*pipipi0_(Merged|Resolved)'))
    print 'Datasets:', datasets
    for dataset in datasets:
        # Still don't know why it's necessary to do this via subprocess, but otherwise it hangs.
        subprocess.call(['python', '-c', '''from AGammaD0Tohhpi0.data import filtereddatadir, datalib
from AGammaD0Tohhpi0.selection import trigger_filter
trigger_filter(filtereddatadir, datalib, {0!r}, overwrite = {1!r})'''.format(dataset, overwrite)])

if __name__ == '__main__' :
    filter_all_trigger(False)
    #offline_filter()
    #add_kinematic_mva()
