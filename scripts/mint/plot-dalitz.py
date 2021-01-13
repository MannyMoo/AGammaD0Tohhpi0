import Mint2
from AGammaD0Tohhpi0.data import datalib
from ROOT import DalitzEvent
from AGammaD0Tohhpi0.mint import set_default_config

set_default_config()

tree = datalib.get_data('MINT_test-kkpi0')

tree.GetEntry(0)
evt = DalitzEvent()
evt.fromTree(tree)
pattern = evt.eventPattern()

s12min, s12max = pattern.sijMin(1,2), pattern.sijMax(1,2)
s13min, s13max = pattern.sijMin(1,3), pattern.sijMax(1,3)

for i in xrange(tree.GetEntries()):
    tree.GetEntry(i)
    evt = DalitzEvent()
    evt.fromTree(tree)
    
    tag = tree.tag
    s12 = evt.s(1,2)
    s13 = evt.s(1,3)
    s23 = evt.s(2,3)
