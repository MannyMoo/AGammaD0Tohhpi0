#!/usr/bin/env python

from AGammaD0Tohhpi0.mint import pattern_D0Topipipi0, set_default_config
from Mint2.utils import three_body_event

set_default_config()

# Get the ranges
s13min = pattern_D0Topipipi0.sijMin(1, 3)
s13max = pattern_D0Topipipi0.sijMax(1, 3)
s23min = pattern_D0Topipipi0.sijMin(2, 3)
s23max = pattern_D0Topipipi0.sijMax(2, 3)

# Try making a DalitzEvent.
s13 = (s13max + s13min)/2.
s23 = (s23max + s23min)/2.

evt = three_body_event(pattern_D0Topipipi0, s13, s23)

# Check that the DalitzEvent has the expected s13 and s23.
evt_s13 = evt.s(1, 3)
evt_s23 = evt.s(2, 3)
print 's13:', s13, 'evt s13:', evt_s13, 'diff:', s13 - evt_s13
print 's23:', s23, 'evt s23:', evt_s23, 'diff:', s23 - evt_s23
if abs(s13 - evt_s13) < 1e-6 and abs(s23 - evt_s23) < 1e-6 :
    print 'Success!'
else :
    print 'Something went wrong!'
