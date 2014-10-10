#!/usr/bin/env python

############################################################
# Author:   Ruben Izquierdo Bevia ruben.izquierdobevia@vu.nl       
# Mail:     ruben.izquierdobevia@vu.nl
# URL;	    http://nl.linkedin.com/pub/rub%C3%A9n-izquierdo-bevi%C3%A1/38/24b/b08/
# Version:  1.0
# Date:     19 Sep 2013
#############################################################

import sys
from simple_wsd import *


if __name__ == '__main__':
  text = sys.argv[1].decode('utf-8')
  wsd_system = my_simple_wsd()
  sense = wsd_system.classify(text)

  print sense
  
  sys.exit(0)