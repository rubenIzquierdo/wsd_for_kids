#!/usr/bin/env python

#############################################################
# Author:   Ruben Izquierdo Bevia ruben.izquierdobevia@vu.nl       
# Mail:     ruben.izquierdobevia@vu.nl
# URL;      http://nl.linkedin.com/pub/rub%C3%A9n-izquierdo-bevi%C3%A1/38/24b/b08/
# Version:  1.0
# Date:     19 Sep 2013 
#############################################################


import sys
from simple_wsd import my_simple_wsd

if __name__ == '__main__':
  picture_id = sys.argv[1].decode('utf-8')
  text = sys.argv[2].decode('utf-8')
   
  wsd_system = my_simple_wsd()
  wsd_system.train(picture_id,text)
  
  
  
  sys.exit(0)