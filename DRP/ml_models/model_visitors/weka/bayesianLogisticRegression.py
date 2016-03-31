from django.conf import settings
import uuid
from DRP.ml_models.model_visitors.weka.AbstractWekaModelVisitor import AbstractWekaModelVisitor
import os

    
class BayesianLogisticRegression(AbstractWekaModelVisitor):
    def wekaTrainCommand(self, arff_file, filePath, response_index):
        command = "java weka.classifiers.bayes.BayesianLogisticRegression -t {} -d {} -p 0 -c {}".format(arff_file, filePath, response_index)
        return command
        
    def wekaPredictCommand(self, arff_file, model_file, response_index, results_path):
        command = "java weka.classifiers.bayes.BayesianLogisticRegression -T {} -l {} -p 0 -c {} 1> {}".format(arff_file, model_file, response_index, results_path)
        return command
