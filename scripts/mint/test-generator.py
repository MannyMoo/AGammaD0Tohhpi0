#!/usr/bin/env python

import Mint2
from ROOT import DalitzEvent
from AGammaD0Tohhpi0.mint import pattern_D0Topipipi0

evt = DalitzEvent(pattern_D0Topipipi0,
                  (pattern_D0Topipipi0.sijMax(1, 3) + pattern_D0Topipipi0.sijMin(1, 3))*2/3.,
                  (pattern_D0Topipipi0.sijMax(2, 3) + pattern_D0Topipipi0.sijMin(2, 3))*1/3.)) ;
