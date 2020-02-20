from PyQt4 import QtGui, QtCore
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from scipy import sparse
from enum import Enum

class BusyProgressBar(QtGui.QProgressBar):
    def __init__(self):
        super(BusyProgressBar,self).__init__()
        
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet("background-color:green;color:black;")
        
        self.__Text = None
        
    def setText(self,statusName_Prm):
        self.__Text = statusName_Prm
    
    def text(self):
        return self.__Text

class SFMethod(Enum):
    Information_Gain_Feature_Selection = 1
    Maximal_Marginal_Relevance_Feature_Selection = 2
    Information_Gain_Maximal_Marginal_Relevance_Feature_Selection = 3
    
class EvValue(Enum):
    Accuracy = 1
    Presision = 2
    Recall = 3
    Fmeasure = 4
    @staticmethod
    def getValue(name_Prm):
        for i in EvValue:
            if(i.name == name_Prm):
                return i.value
    
class BagOfWords_Obj(object):
    def __init__(self,documentLstPrm, maxFeaturePrm):
        self.documentLst = documentLstPrm
        self.maxFeature = maxFeaturePrm
        vectorizer = CountVectorizer(max_features=self.maxFeature)
        self.wordCountLst = vectorizer.fit_transform(self.documentLst)
        self.uniqueFeatureLst = vectorizer.get_feature_names()
        
    def featureExtraction(self): #Get Unique Feature
        return self.uniqueFeatureLst
    
    def get2dArrayform(self):
        return self.wordCountLst.toarray()
    
    def sum(self):
        return self.wordCountLst.sum()
    
    def getWordCountinTextLstWithSelectedFeature(self,selectedFeatureLstPrm):
        Result = []
        idxSelectedFeaturesIG = [self.uniqueFeatureLst.index(selectedFeatureLstPrm[i]) for i in range(len(selectedFeatureLstPrm))]
        tmp = self.get2dArrayform()[:,idxSelectedFeaturesIG]
        
        for i in range(tmp.shape[0]):
                bowPerRow = ""
                # features taken are contained in top features
                for j in range(tmp.shape[1]):
                    if (j == 0):
                        bowPerRow = bowPerRow + "[" + str(tmp[i,j]) + ", "
                    elif (j == tmp.shape[1]-1):
                        bowPerRow = bowPerRow + str(tmp[i,j]) + "]"
                    else:
                        bowPerRow = bowPerRow + str(tmp[i,j]) + ", "
                Result.append(bowPerRow)
                
        return Result
    
    def filterWordcount(self, selectedFeatureLst_Prm):
        Result = []
        termIdxArr = [i for i in range(len(self.uniqueFeatureLst))]
        selectedFeatureIdx = [self.uniqueFeatureLst.index(i) for i in selectedFeatureLst_Prm]
        
        deletedIndexArr = np.delete(np.array(termIdxArr),selectedFeatureIdx)
        newBagOfWords = np.delete(self.wordCountLst.toarray(), deletedIndexArr, axis=1)
        Result = sparse.csr_matrix(newBagOfWords)
        
        return Result
        
    
class selectedFeatureMethod_Obj(object):
    def __init__(self, methodNameStr_Prm="", IGThresholdInt_Prm=0, MMRThresholdInt_Prm=0, MMRLambdaFlt_Prm=0, isDFW_Prm=0):
        self.Name = methodNameStr_Prm
        self.IGThreshold = IGThresholdInt_Prm
        self.MMRThreshold = MMRThresholdInt_Prm
        self.MMRLambda = MMRLambdaFlt_Prm
        self.IsDFW = isDFW_Prm

class CVResult_Obj(object):
    def __init__(self,fold, textIdxLst_Prm, predictedCategoryLst_Prm):
        self.Fold = fold
        self.TextIdx = textIdxLst_Prm
        self.PredictedCategory = predictedCategoryLst_Prm 