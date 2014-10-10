#!/usr/bin/env python

#############################################################
# Author:   Ruben Izquierdo Bevia ruben.izquierdobevia@vu.nl       
# Mail:     ruben.izquierdobevia@vu.nl
# URL;      http://nl.linkedin.com/pub/rub%C3%A9n-izquierdo-bevi%C3%A1/38/24b/b08/
# Version:  1.0
# Date:     19 Sep 2013 
#############################################################

import shutil
import os

from simple_wsd import *

this_folder = os.path.dirname(__file__)

if __name__ == '__main__':

  target_words = load_target_words()
  
  for tw in target_words:
      folder = os.path.join(this_folder,tw)
      if os.path.exists(folder):
          shutil.rmtree(folder)
          print>>sys.stderr,'Removed ',folder

  sys.exit(0)