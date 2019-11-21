'''Instantiates the RooWorkspace for the current analysis.'''

#from AGammaD0Tohhpi0.data import datadir
from AnalysisUtils.workspace import *
import os
from AGammaD0Tohhpi0.variables import variables

# If you want a persistent workspace between sessions you can give it a file name.
#workspacefilename = os.path.join(datadir, 'workspace.root')
workspace = Workspace('workspace', 
                      #fname = workspacefilename,
                      variables = variables
                      )
