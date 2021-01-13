#!/usr/bin/env python

from AGammaD0Tohhpi0.data import datalib
from AnalysisUtils.tmva import TMVADataLoader, TMVAClassifier
from AnalysisUtils.addmva import add_mva_friend
from AGammaD0Tohhpi0.pipipi0_utils import RESOLVED_TRAIN_DATANAME, RESOLVED_SEL
import ROOT
from ROOT import RooFit

outputname = 'mva_output.root'

#Reading in data
dataset = RESOLVED_TRAIN_DATANAME
selection = RESOLVED_SEL + ' && acos(D_DIRA_OWNPV) < 3.'
realtree = datalib.get_data(dataset)

varlist = ["acos(D_DIRA_OWNPV)", "D_CosTheta", "pi0_PT", "log(pi0_CL)", "pi0_CosTheta", "Dstr_PT", "D_PT", "H1_PT + H2_PT"]

weightvar = 'SidebandWeightsTree.sideband_weight'
dataloader = TMVADataLoader(realtree, realtree, varlist , signalweight = weightvar, backgroundweight = weightvar +'<0.', 
                            signalcut = selection, backgroundcut = selection)
method = "BDT"
methoddict = {"BDT" : "!H:!V:NTrees=350:MinNodeSize=10%:MaxDepth=2:BoostType=AdaBoost:AdaBoostBeta=0.5:SeparationType=GiniIndex:nCuts=50:PruneMethod=NoPruning:NegWeightTreatment=InverseBoostNegWeights",
"BoostedFisher" : 'H:!V:Boost_Num=20:Boost_Transform=log:Boost_Type=AdaBoost:Boost_AdaBoostBeta=0.2'}
classifier = TMVAClassifier(dataloader, methoddict, factoryoptions = TMVAClassifier.default_factory_options(Transformations = 'I'))
outputfile = ROOT.TFile.Open(outputname, 'RECREATE')
classifier.train_factory(outputfile)

#Adding BDT result to tree
for method in methoddict.keys():
    add_mva_friend(datalib, dataset, "dataset/weights/TMVAClassification_"+method+".weights.xml", method, method, 
                   perfile = False, overwrite = True)

