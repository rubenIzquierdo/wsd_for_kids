#!/bin/bash

#############################################################
# Author:   Ruben Izquierdo Bevia ruben.izquierdobevia@vu.nl       
# Mail:     ruben.izquierdobevia@vu.nl
# URL;      http://nl.linkedin.com/pub/rub%C3%A9n-izquierdo-bevi%C3%A1/38/24b/b08/
# Version:  1.0
# Date:     19 Sep 2013 
#############################################################


here=`pwd`
my_svm_folder='svm_ligth_multiclass'

echo 'Downloading and compiling svm_light'
mkdir $my_svm_folder
cd $my_svm_folder
wget http://download.joachims.org/svm_multiclass/current/svm_multiclass.tar.gz 2> /dev/null
echo Downloaded $svm

svm_tgz=`ls -1 | head -1`
gunzip -c $svm_tgz | tar xf -
rm $svm_tgz
echo Unzipped on $svm_folder
make
echo svm_ligth installed on $my_svm_folder


