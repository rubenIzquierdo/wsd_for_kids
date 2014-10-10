Installation
===========

+ 1) Clone the repository (git clone https://github.com/rubenIzquierdo/wsd_for_kids.git)
+ 2) run the install.sh to download and compile svmligt


Scripts
=====

+ 1) train.py -> for training the system with a new instance
* Usage: python train.py "sense_id" "text"
* Example: python train.py 'caballo.1' "resultado de su salto, el caballo..."
* Output: void

* classify.py --> for classifying a new instance 
* Usage: python classify.py "text"
* Example: python classify.py "este caballo es un animal muy noble"
* Output: the guessed sense (or unknown in case there is no classifier)

* clean.py --> to clean all the classifiers and "forget" everything
* python clean.py

*** Important ***
-----------------

* The sense identifiers should follow the format: target_word.sensenumber:
* caballo.1  paard.2  muis.200 ...

* The scripts produce some debug output. To remove it edit the file simple_wsd.py and comment the next line (line number 15)
* logging.basicConfig(stream=sys.stderr,format='%(asctime)s - %(levelname)s - %(message)s',level=logging.DEBUG)

   
* The train.py will obtain the target word directly from the sense
  identifier, but the classify.py will try to "guess" which is the target word by selecting
  the target word most likely from a predefined list of words by using the
  levenshtein distance (comparing each possible target word with each token in
  the text). This predefined list of possible target words is encoded in the
  file "target_words", so for adding/removing a target word just modify that
  file (one target word per file in lowercase)


* There are shell scripts which simulate the training/classification of
some instances for the spanish word "caballo" (horse) which is also
polysemous in spanish. You can run them to see how the system works:
* run_train.sh (will train a classifier for "caballo" with 4 examples, 2
for sense 1 and 2 for sense2)
* run_classify.sh (will classify 3 examples with the caballo classifier"


Contact
======

+ Author:   Ruben Izquierdo Bevia      
+ Mail:     ruben.izquierdobevia@vu.nl  rubensanvi@gmail.com
+ URL:      http://rubenizquierdobevia.com/


