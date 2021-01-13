from AGammaD0Tohhpi0.data import datalib
import pickle as pkl
import pandas as pd
from root_numpy import array2tree
from itertools import izip

tree = datalib.get_data('RealData_2015_Charm_MagDown_pipipi0_Resolved_TriggerFiltered')
#tree = datalib.get_data('RealData_2017_Charm_MagUp_pipipi0_Merged_TriggerFiltered')
friendvars = ['BDT', 'BoostedFisher']

cutvars = ['Dstr_PT', 'D_PT', 'D_IPCHI2_OWNPV', 'Dstr_FDCHI2_OWNPV', 'pi0_CosTheta', 'D_DIRA_OWNPV', 'Dstr_FIT_DLT']
dmvars = ['Dstr_FIT_M', 'Dstr_FIT_DM', 'D_MMERR']
data, columns = tree.AsMatrix(columns = dmvars+['Dstr_FIT_CHI2']+cutvars, return_labels = True)
df = pd.DataFrame(data=data, columns=columns)
df['deltam'] = df[dmvars[0]] - df[dmvars[1]]

# add mva output - have to do here because for some reason friend trees only load after a call to AsMatrix
frienddata, friendcols = tree.AsMatrix(columns=friendvars, return_labels = True)
for i in range(len(friendcols)):
    df[friendcols[i]] = frienddata[:,i]

df = df.query('Dstr_FIT_CHI2 >= 0 and Dstr_FIT_CHI2 < 30')
#df = df.drop(columns = ['Dstr_FIT_CHI2']+[dmvars[0]])

tree = array2tree(df.to_records(index=False))
with open('resolved_tree.pkl', 'wb') as f:
    pkl.dump(tree, f)


