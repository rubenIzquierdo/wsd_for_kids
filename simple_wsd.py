#############################################################
# Author:   Ruben Izquierdo Bevia ruben.izquierdobevia@vu.nl       
# Mail:     ruben.izquierdobevia@vu.nl
# URL;      http://nl.linkedin.com/pub/rub%C3%A9n-izquierdo-bevi%C3%A1/38/24b/b08/
# Version:  1.0
# Date:     19 Sep 2013 
#############################################################


import os
import pickle
import sys
from operator import itemgetter
from tempfile import NamedTemporaryFile
from subprocess import Popen,PIPE
import logging

this_folder = os.path.dirname(__file__)
svm_learn = os.path.join(this_folder,'svm_ligth_multiclass','svm_multiclass_learn')
svm_learn_opts = '-c 1'
svm_classify = os.path.join(this_folder,'svm_ligth_multiclass','svm_multiclass_classify')

#Comment next line to remove debug log
logging.basicConfig(stream=sys.stderr,format='%(asctime)s - %(levelname)s - %(message)s',level=logging.DEBUG)


def load_target_words():
    filename = os.path.join(this_folder,'target_words')
    target_words = []
    file_obj = open(filename,'r')
    for line in file_obj:
        target_words.append(line.strip())
    file_obj.close()
    return target_words

## From wikipedia
## http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
def levenshtein(seq1, seq2):
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
    return thisrow[len(seq2) - 1]

def guess_target_word(text):
    target_words = load_target_words()
    tokens = text.strip().lower().split(' ')
    vector_tw_mindist = []
    for tw in target_words:
        min_dist = 1000
        for token in tokens:
            dist = levenshtein(tw,token)
            if dist<min_dist: min_dist = dist
        vector_tw_mindist.append((tw,min_dist))
    vector_tw_mindist.sort(key=itemgetter(1))
    return vector_tw_mindist[0][0]

class my_simple_wsd:
    def __init__(self):
        self.target=''
        
    def my_init(self):
        self.wsd_folder= os.path.join(this_folder,self.target)
        self.instances_filename = os.path.join(self.wsd_folder,'training_instances.bin')
        self.index_for_sense = {}
        self.index_for_sense_filename = os.path.join(self.wsd_folder,'index_for_sense.bin')
        self.index_features_filename = os.path.join(self.wsd_folder,'index_features.bin')
        self.model_filename = os.path.join(self.wsd_folder,'model.svm')
        self.unknown_sense = 'unknown'

        self.examples = []      # Vector or pairs (sense_id,BOW)

        
    def get_features(self,text):
        return text.lower().split(' ')
    
   
    def train(self,sense_id,text):
        self.target = sense_id.split('.')[0]
        logging.debug('Training system for target word '+self.target+' sense: '+sense_id)
        self.my_init()
        ######################################################
        ## Initialize trainer and load training instances
        if not os.path.exists(self.wsd_folder): #not yet trained for this target word
            os.mkdir(self.wsd_folder)
            self.examples = []                  # there are no examples
        else:
            instances_file = open(self.instances_filename,'rb')
            self.examples = pickle.load(instances_file)
            instances_file.close()
            os.remove(self.instances_filename)  # The current file is removed
            
            idx_sense_file = open(self.index_for_sense_filename,'rb')
            self.index_for_sense = pickle.load(idx_sense_file)
            idx_sense_file.close()
            os.remove(self.index_for_sense_filename)
        logging.debug('Loaded '+str(len(self.examples))+' examples')
        logging.debug('Loaded '+str(len(self.index_for_sense))+' classes')
        ######################################################
        
        ######################################################
        ## Add the new example to the list of examples
        new_features = self.get_features(text)
        self.examples.append((sense_id,new_features))
        del new_features
        
        if not sense_id in self.index_for_sense:
            self.index_for_sense[sense_id] = len(self.index_for_sense)+1
        ######################################################


        ################################################
        # Save the current list of examples to the training_instances
        instances_file = open(self.instances_filename,'wb')
        pickle.dump(self.examples,instances_file)
        instances_file.close()
        
        
        idx_sense_file = open(self.index_for_sense_filename,'wb')
        pickle.dump(self.index_for_sense,idx_sense_file)
        idx_sense_file.close()
        logging.debug('Saved '+str(len(self.examples))+' examples on ' + self.instances_filename)
        logging.debug('Saved '+str(len(self.index_for_sense))+' classes on '+ self.instances_filename)
        ################################################
        
        ######################################################
        # Create index of features for encoding in smv_light format
        # map {feat} --> (index, frequency)
        ######################################################
        self.feature_index = {}
        for sense_id, features in self.examples:
            for feat in features:
                if feat in self.feature_index:
                    idx,freq = self.feature_index[feat]
                    self.feature_index[feat] = (idx,freq+1)
                else:
                    idx = len(self.feature_index) + 1   #First feautre is number 1    
                    freq = 1
                    self.feature_index[feat] = (idx,freq)
        #Save it to use it later on classification
        idx_feats_file = open(self.index_features_filename,'wb')
        pickle.dump(self.feature_index,idx_feats_file)
        idx_feats_file.close()
        logging.debug('Created index of features for '+str(len(self.feature_index))+' unique features')
        ######################################################

        ######################################################
        # Encoding each feature for the training and creating training file
        ######################################################
        training_file = NamedTemporaryFile('w',delete=False)
        for sense_id, features in self.examples:
            logging.debug('Encoding new instance for the sense '+sense_id+' with '+str(len(features))+' features')
            index_for_sense = self.index_for_sense[sense_id]
            feats_for_example = {}  #For this example, a feature -> frequency map
            for feat in features:
                if feat in feats_for_example: 
                    feats_for_example[feat] += 1
                else:
                    feats_for_example[feat] = 1
            
            vector_feats = []   # is a vector of pairs (num_feature, weight)
            for feat, freq_feat in feats_for_example.items():
                index, total_freq_feat = self.feature_index[feat]
                weight = 1  #Use weight 1
                weight = 1.0*freq_feat / total_freq_feat
                vector_feats.append((index,weight))
            # Sort the vector according to the first element
            vector_feats.sort(key=itemgetter(0))
            my_str = str(index_for_sense)
            for idx, weight in vector_feats:
                my_str = my_str+' '+str(idx)+':'+str(weight)
            training_file.write('%s\n' % my_str)
        training_file.close()
        ######################################################

        ######################################################
        # Performing the training
        cmd = svm_learn+' '+svm_learn_opts+' '+training_file.name+' '+self.model_filename
        svm_process = Popen(cmd, stdout=PIPE, stderr=PIPE,  shell=True)
        return_code = svm_process.wait()
        logging.debug('Model trained on '+self.model_filename)
        err = svm_process.stderr.read()
        if len(err)!=0:
            print>>sys.stderr,'ERROR during training: ',err
        os.remove(training_file.name)
        ######################################################
       
    def classify(self,text):
        self.target = guess_target_word(text)
        logging.debug('Classification for target word (guessed by levenshtein distance) '+self.target)
        self.my_init()
        if not os.path.exists(self.wsd_folder):
            return self.unknown_sense
        
        ### Load classes and create inverted index
        idx_sense_file = open(self.index_for_sense_filename,'rb')
        self.index_for_sense = pickle.load(idx_sense_file)
        idx_sense_file.close()
        logging.debug('Loaded possible classes for '+self.target+' ==> '+str(self.index_for_sense))
        
        if len(self.index_for_sense) == 1:  #For this classifier, the word is monosemous
            return self.index_for_sense.keys()[0]
            
        
        self.sense_for_index = {}
        for sense,index in self.index_for_sense.items():
            self.sense_for_index[str(index)] = sense
        ######################################################


        ######################################################
        # Load feature index
        idx_index_features = open(self.index_features_filename,'rb')
        feature_index = pickle.load(idx_index_features)
        idx_index_features.close()
        logging.debug('Loaded index features for '+str(len(feature_index))+' unique features')
        
        ######################################################
        
        
        ##Creating map of feat --> freq for the example
        features = self.get_features(text)
        logging.debug('Extracted '+str(len(features))+' features for the example')
        feats_for_example = {}  #For this example, a feature -> frequency map
        for feat in features:
            if feat in feats_for_example: 
                feats_for_example[feat] += 1
            else:
                feats_for_example[feat] = 1
            
        ## Encoding the example using the feature index loaded before    
        vector_feats = []   # is a vector of pairs (num_feature, weight)
        for feat, freq_feat in feats_for_example.items():
            if feat in feature_index:
                index, total_freq_feat = feature_index[feat]
                weight = 1  #Use weight 1
                weight = 1.0*freq_feat / total_freq_feat
                vector_feats.append((index,weight))
            
        logging.debug('Using '+str(len(vector_feats))+' features for classification (intersection with training features)')
        # Sort the vector according to the first element
        vector_feats.sort(key=itemgetter(0))           
        if len(vector_feats) == 0:
            logging.debug('Zero matches with features, returning unknown')
            return self.unknown_sense
        
        #Creating example file
        example_file = NamedTemporaryFile('w',delete=False)
        my_str = '1 '   ## unknown class, all set to 1
        for idx, weight in vector_feats:
            my_str = my_str+' '+str(idx)+':'+str(weight)
        example_file.write('%s\n' % my_str)
        example_file.close()
        
        ## Calling to the classifier
        output_file = NamedTemporaryFile('w',delete=False)
        output_file.close()
        
        cmd = svm_classify+' '+example_file.name+' '+self.model_filename+' '+output_file.name
        svm_process = Popen(cmd,stdout=PIPE,stderr=PIPE,shell=True)
        ret_code = svm_process.wait()
        err = svm_process.stderr.read()
        if len(err) != 0:
            logging.debug('ERROR on svm classification: '+err)
            sys.exit(-1)
        
        ##Read the result
        result_file = open(output_file.name,'r')
        all_result = result_file.readlines()[0]     #predicted prob1 prob2 prob3...
        predicted_index_class = all_result.split(' ')[0]
        predicted_class = self.sense_for_index[predicted_index_class]
        logging.debug('Complete svm output result: '+all_result)
        logging.debug('Predicted sense index: '+predicted_class)
        result_file.close()
        
        os.remove(example_file.name)
        os.remove(output_file.name)
        return predicted_class
        
        
            
            
            
        
        
        
            

        
        
            
            
        
            

    
    