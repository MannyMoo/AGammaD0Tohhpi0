#!/usr/bin/env python

from AGammaD0Tohhpi0.data import datalib
from AnalysisUtils.tmva import TMVADataLoader, TMVAClassifier
from AnalysisUtils.addmva import add_mva_friend
import ROOT, sys
from AGammaD0Tohhpi0.pipipi0_utils import MERGED_SEL, MERGED_TRAIN_DATANAME

outfile = 'mva_output.root'

#Reading in data
selection = MERGED_SEL + " && acos(D_DIRA_OWNPV) < 3."
dataset = MERGED_TRAIN_DATANAME
realtree = datalib.get_data(dataset)


#Best list of variables yet
varlist = ["D_PT", "Dstr_PT", "log(Dstr_FDCHI2_OWNPV)", "log(D_IPCHI2_OWNPV)", "H1_PT + H2_PT", "pi0_CosTheta", 
           "D_CosTheta", "pi0_PT", "acos(D_DIRA_OWNPV)", "log(pi0_CL)"]
#msci list : varlist = ["D_PT", "Dstr_PT", "log(Dstr_FDCHI2_OWNPV)", "log(D_IPCHI2_OWNPV)", "H1_PT + H2_PT", "pi0_CosTheta", "D_P"]


weightvar = 'SidebandWeightsTree.sideband_weight'
dataloader = TMVADataLoader(realtree, realtree, varlist , signalweight = weightvar, backgroundweight = weightvar+'<0.', 
                            signalcut = selection, backgroundcut = selection)

#methoddict = {"BDT" : "!H:!V:NTrees=850:MinNodeSize=10%:MaxDepth=2:BoostType=AdaBoost:AdaBoostBeta=0.5:SeparationType=GiniIndex:nCuts=20:PruneMethod=NoPruning:NegWeightTreatment=InverseBoostNegWeights"}
methoddict = {"BDT" : "!H:!V:NTrees=250:MinNodeSize=15%:MaxDepth=2:BoostType=AdaBoost:AdaBoostBeta=0.25:SeparationType=GiniIndex:nCuts=50:PruneMethod=NoPruning:NegWeightTreatment=InverseBoostNegWeights",
"BoostedFisher" : 'H:!V:Boost_Num=20:Boost_Transform=log:Boost_Type=AdaBoost:Boost_AdaBoostBeta=0.5'}
classifier = TMVAClassifier(dataloader, methoddict, factoryoptions = TMVAClassifier.default_factory_options(Transformations = 'I'))

outputfile = ROOT.TFile.Open(outfile, 'RECREATE')
classifier.train_factory(outputfile)

#Adding BDT result to tree
for method in methoddict.keys():
    add_mva_friend(datalib, dataset, "dataset/weights/TMVAClassification_"+method+".weights.xml", method, method, 
                   perfile = False, overwrite = True)
