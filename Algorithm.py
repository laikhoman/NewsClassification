import numpy as np
import string
import nltk
ps = nltk.stem.porter.PorterStemmer()
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.feature_extraction.text import CountVectorizer
from scipy import sparse
import itertools
import math

from SystemMaterial import BagOfWords_Obj, CVResult_Obj

class Textpreprocessing(object):
    def __init__(self,textPrm):
        self.Text = textPrm
        
    def casefolding(self):
        return self.Text.lower()
    
    def tokenization(self):
        return self.__splitText(self.__removeDigit(self.__removePunctuation(self.Text)))

    def removeStopwords(self):
        stopwordArr = self.__getStopWords()
        return " ".join([i for i in self.Text.split() if not i in stopwordArr])
        
    def __removePunctuation(self,textPrm):
        return "".join(i for i in textPrm if i not in string.punctuation)
    
    def __removeDigit(self,textPrm):
        return "".join(i for i in textPrm if not i.isdigit() )
    
    def Stemming(self):
        return ' '.join([self.__stem(i) for i in self.Text.split()])
    
    def __splitText(self,textPrm):
        return " ".join([i for i in textPrm.split()])
    
    def __getStopWords(self):
        fp = open('resrc/stopwordEnglishRankNL.txt') # open file on read mode
        lines = fp.read().split("\n") # create a list containing all lines
        fp.close() # close file
        return lines

    def __stem(self,term):
        return ps.stem(term)
    
class infoGainDoc(object):   
    def __init__(self,thresholdPrm,datacorpusPrm):
        self.result = np.array([])
        self.maxFeature = 1000
        self.threshold = thresholdPrm #Number of Feature
        self.datacorpus = datacorpusPrm #List Text
        self.BOW = BagOfWords_Obj(self.datacorpus,self.maxFeature)
         
    def findFeatures(self):        
        totalWordCount = self.BOW.sum()
        totalWordCountPerFeatureLst = np.sum(self.BOW.wordCountLst, axis = 0)
        totalWordCountPerDocLst = np.sum(self.BOW.wordCountLst, axis = 1)
        
        probaDocContainsFeatureLst = totalWordCountPerFeatureLst / totalWordCount
        probaDocNotContainsFeatureLst = 1-probaDocContainsFeatureLst
        
        tmp1 = self.BOW.wordCountLst/totalWordCountPerFeatureLst
        logtmp1 = np.where(tmp1==0.0,0.0,np.log10(tmp1))
        multTmp1 = np.where(np.isnan(np.multiply(tmp1,logtmp1)),0.0,np.multiply(tmp1,logtmp1))
        sumOfFeatureProba = np.sum(multTmp1, axis = 0)
        
        tmp2 = (totalWordCountPerDocLst - self.BOW.wordCountLst)/(totalWordCount - totalWordCountPerFeatureLst)
        logtmp2 = np.where(tmp2==0.0,0.0,np.log10(tmp2))
        multTmp2 = np.where(np.isnan(np.multiply(tmp2,logtmp2)),0.0,np.multiply(tmp2,logtmp2))
        sumOfNotFeatureProba = np.sum(multTmp2, axis = 0)
        
        res1 = np.multiply(probaDocContainsFeatureLst,sumOfFeatureProba)
        res2 = np.multiply(probaDocNotContainsFeatureLst,sumOfNotFeatureProba)
        res = np.add(res1,res2)

        result = np.asarray(res) #res
        
        indexFeatureList = []
        for i in range(len(result[0])):
            indexFeatureList.append(i)
        indexIGDoc = np.array([result[0], indexFeatureList])
        
        sortedIndexIGDoc = indexIGDoc[:,np.argsort(-indexIGDoc[0])]
        
        self.result = sortedIndexIGDoc.T
        
        return self.result
    
    def getSelectedResult(self, IndexLst_Prm = []):
        if(IndexLst_Prm != []): S = IndexLst_Prm
        else: S = self.result[:self.threshold][:,1].astype(int)
        
        IndexLstInt = [int(float(i)) for i in S]
        Result = [self.BOW.uniqueFeatureLst[i] for i in sorted(IndexLstInt)]        
        
        return Result

class mmrFS(object):
    def __init__(self,thresholdPrm,lambdaPrm,datacorpusPrm,categoryPrm,IGSelectedfeaturePrm = []):
        self.maxFeature = 1000
        self.threshold = thresholdPrm
        self.lmbda = lambdaPrm
        self.datacorpus = datacorpusPrm
        self.category = categoryPrm
        self.selectedFeature = IGSelectedfeaturePrm
        
        self.BOW = BagOfWords_Obj(self.datacorpus, self.maxFeature) 
        if(IGSelectedfeaturePrm != []):
            self.BOW.wordCountLst = self.filterDataWithIG()
            self.BOW.uniqueFeatureLst = self.selectedFeature
            
    def filterDataWithIG(self):
        vectorizer = CountVectorizer(max_features=self.maxFeature)
        tmp = vectorizer.fit_transform(self.datacorpus)
        uniqueFeatures = vectorizer.get_feature_names()
        
        termIndexArr = []
        for i in range(len(uniqueFeatures)):
            termIndexArr.append(i)
        indexOfSelectedFeatureArr = [uniqueFeatures.index(i) for i in self.selectedFeature]
        
        deletedIndexArr = np.delete(np.array(termIndexArr),indexOfSelectedFeatureArr)
        
        newBagOfWords = np.delete(tmp.toarray(), deletedIndexArr, axis=1)
        
        return sparse.csr_matrix(newBagOfWords)
    
    def getIndexigMMR(self):
        
        totalCount = self.BOW.wordCountLst.sum()
        
        totalWordCountPerFeatureLst = np.sum(self.BOW.wordCountLst, axis = 0)

        probaDocContainsFeature = totalWordCountPerFeatureLst / totalCount
        probaDocNotContainsFeature = 1-probaDocContainsFeature
        classArr = np.array(self.category)
        
        uniqueClass = np.unique(self.category)

        numOfUniqueClass = uniqueClass.shape[0]
        
        sumOfFeatureProba = 0.0
        sumOfNotFeatureProba = 0.0
        
        for i in range(numOfUniqueClass):
            
            print(classArr)
            mask = (classArr[:] == uniqueClass[i])
            
            dataByClass = self.BOW.wordCountLst[mask]

            totalCountInClass = dataByClass.sum()

            totalInEveryFeatureInClass = np.sum(dataByClass, axis = 0)
            
            tmp1 = totalInEveryFeatureInClass/totalWordCountPerFeatureLst
            logtmp1 = np.where(tmp1==0.0,0.0,np.log10(tmp1))
            multTmp1 = np.where(np.isnan(np.multiply(tmp1,logtmp1)),0.0,np.multiply(tmp1,logtmp1))
            sumOfFeatureProba = sumOfFeatureProba + multTmp1
            
            tmp2 = (totalCountInClass - totalInEveryFeatureInClass)/(totalCount - totalWordCountPerFeatureLst)
            logtmp2 = np.where(tmp2==0.0,0.0,np.log10(tmp2))
            multTmp2 = np.where(np.isnan(np.multiply(tmp2,logtmp2)),0.0,np.multiply(tmp2,logtmp2))
            sumOfNotFeatureProba = sumOfNotFeatureProba + multTmp2
    
        Result = np.multiply(probaDocContainsFeature,sumOfFeatureProba) + np.multiply(probaDocNotContainsFeature,sumOfNotFeatureProba)
        
        return np.array([np.squeeze(np.asarray(Result))])
    
    def getIndexIGPairMMR(self):
        classArr = np.array(self.category)
        numOfFeatures = self.BOW.wordCountLst.shape[1]
        uniqueClass = np.unique(self.category)
        
        numOfUniqueClass = uniqueClass.shape[0]
        s = (numOfFeatures,numOfFeatures)
        res = np.zeros(s)
        
        totalCount = self.BOW.wordCountLst.sum()
        
        for i in range(numOfFeatures):
            for j in range(i+1,numOfFeatures):
                
                dataBy2Features = self.BOW.wordCountLst[:,[i,j]]
                
                TMP = np.where(dataBy2Features.toarray()<1,0,1)
                
                LOGICALANDARR = np.logical_and(TMP[:,0],TMP[:,1])
                
                ANDMASK = (LOGICALANDARR == 1)
                NOTANDMASK = (LOGICALANDARR == 0)
                
                
                totalInTwoFeatureAnd = (np.sum(dataBy2Features[ANDMASK], axis = 0)).sum()
                
                totalInTwoFeatureNotAnd = (np.sum(dataBy2Features[NOTANDMASK], axis = 0)).sum()
                
                probaDocContainsFeature = totalInTwoFeatureAnd / totalCount
                
                probaDocNotContainsFeature = 1-probaDocContainsFeature
                
                sumOfFeatureProba = 0.0
                sumOfNotFeatureProba = 0.0
                for k in range(numOfUniqueClass):
                    mask = (classArr[:] == uniqueClass[k])                    
                    
                    dataBy2FeaturesInClass = dataBy2Features[mask]
                    
                    toBiner = np.where(dataBy2FeaturesInClass.toarray()!=0,1,0)
                    
                    logicalAndArr = np.logical_and(toBiner[:,0],toBiner[:,1])
                    
                    oneMask = (logicalAndArr[:] == True)
                    
                    zeroMask = (logicalAndArr[:] == False)
                    
                    totalInTwoFeatureAndInClass = (np.sum(dataBy2FeaturesInClass[oneMask].toarray(), axis = 0)).sum()
                    
                    totalInTwoFeatureNotAndInClass = (np.sum(dataBy2FeaturesInClass[zeroMask].toarray(), axis = 0)).sum()
                    
                    tmp1 = totalInTwoFeatureAndInClass/totalInTwoFeatureAnd
                    
                    logtmp1 = np.where(tmp1==0.0,0.0,np.log10(tmp1))
                    
                    multTmp1 = np.where(np.isnan(np.multiply(tmp1,logtmp1)),0.0,np.multiply(tmp1,logtmp1))
                    
                    sumOfFeatureProba = sumOfFeatureProba + multTmp1
                    
                    tmp2 = totalInTwoFeatureNotAndInClass/totalInTwoFeatureNotAnd
                    
                    logtmp2 = np.where(tmp2==0.0,0.0,np.log10(tmp2))
                    
                    multTmp2 = np.where(np.isnan(np.multiply(tmp2,logtmp2)),0.0,np.multiply(tmp2,logtmp2))
                    
                    sumOfNotFeatureProba = sumOfNotFeatureProba + multTmp2
                    
                res[i,j] = probaDocContainsFeature*sumOfFeatureProba + probaDocNotContainsFeature*sumOfNotFeatureProba
                res[j,i] = res[i,j]
                
        return res
    
    def doMMRFS(self,igMMRdfPrm,igPairMMRdfPrm):
        self.igMMRdf = igMMRdfPrm
        self.igPairMMRdf = igPairMMRdfPrm
        
        if(self.selectedFeature != []):
        
            R_S = [] # list of not yet selected index of feature R-S
            S = [] #list of selected index of feature/term
            for i in range(len(self.selectedFeature)):
                R_S.append(i)
            for i in range(self.threshold):
               
                R_S,S = self.getIndexMMR(R_S,S)
                
            return [self.selectedFeature[i] for i in sorted(S)]
        else:
            R_S = [] # list of not yet selected index of feature R-S
            S = [] #list of selected index of feature/term
            for i in range(len(self.BOW.uniqueFeatureLst)):
                R_S.append(i)
            for i in range(self.threshold):
                
                R_S,S = self.getIndexMMR(R_S,S)
                
            return [self.BOW.uniqueFeatureLst[i] for i in sorted(S)]
        
    def getIndexMMR(self,listIndexNotYetSelected,listIndexSelected):
        listOfMMR = []
        for i in listIndexNotYetSelected:
            
            secondEquation = []
            for j in listIndexSelected:

                secondEquation.append(self.igPairMMRdf.iloc[i,j])
            if(len(secondEquation)==0):
                
                tmp = self.igMMRdf.iloc[0,i] #infoGainMMR(X,Y,listIndexNotYetSelected[i])
            else:
                tmp = self.lmbda*self.igMMRdf.iloc[0,i] - (1-self.lmbda)*max(secondEquation)
            
            listOfMMR.append(tmp)
        
        indexOfMax = listOfMMR.index(max(listOfMMR))
        
        listIndexSelected.append(listIndexNotYetSelected[indexOfMax])
        listIndexNotYetSelected.remove(listIndexNotYetSelected[indexOfMax])
        
        return listIndexNotYetSelected,listIndexSelected

class FCMatrix(object):
    def __init__(self, X,Y):
        self.X = X
        self.Y = Y
    
    def __entropy(self, vec, base=10):
        " Returns the empirical entropy H(X) in the input vector."
        _, vec = np.unique(vec, return_counts=True)
        prob_vec = np.array(vec/float(sum(vec)))
        if base == 2:
            logfn = np.log2
        elif base == 10:
            logfn = np.log10
        else:
            logfn = np.log
        return prob_vec.dot(-logfn(prob_vec))
    
    def __conditional_entropy(self, x, y):
        "Returns H(X|Y)."
        uy, uyc = np.unique(y, return_counts=True)
        prob_uyc = uyc/float(sum(uyc))
        cond_entropy_x = np.array([self.__entropy(x[y == v]) for v in uy])
        return prob_uyc.dot(cond_entropy_x)
    
    def __mutual_information(self, x, y):
        " Returns the information gain/mutual information [H(X)-H(X|Y)] between two random vars x & y."
        
        return self.__entropy(x) - self.__conditional_entropy(x, y)
    
    def __symmetrical_uncertainty(self, x, y):
        " Returns 'symmetrical uncertainty' (SU) - a symmetric mutual information measure."
        return 2.0*self.__mutual_information(x, y)/(self.__entropy(x) + self.__entropy(y))
    
    def makeFCMatrix(self):
        numOfFeatures = self.X.shape[1]
        s = (numOfFeatures,numOfFeatures+1)
        res = np.zeros(s)
        for i in range(numOfFeatures):
            for j in range(numOfFeatures+1):
                if(j==i):
                    res[i,j] =  1.0
                elif(j==numOfFeatures):
                    res[i,j] =  self.__symmetrical_uncertainty(self.X[:,i].toarray(),self.Y)
                else:
                    res[i,j] =  self.__symmetrical_uncertainty(self.X[:,i].toarray(),self.X[:,j].toarray())
        return res

class cfs(object):
    
    def __init__(self,data_corpus,Y,selectedFeatureIGMMR,maxFeature):
        self.data_corpus = data_corpus
        self.Y = Y
        self.selectedFeatureIGMMR = selectedFeatureIGMMR
        self.maxFeature = maxFeature
        self.selectedIndex = []
        self.FCMatrix = np.array([])
    
        vectorizer = CountVectorizer(max_features = self.maxFeature)
        X = vectorizer.fit_transform(self.data_corpus)
        uniqueFeatures = vectorizer.get_feature_names()

        termIndexArr = []
        for i in range(len(uniqueFeatures)):
            termIndexArr.append(i)
        indexOfSelectedFeatureArr = [uniqueFeatures.index(i) for i in self.selectedFeatureIGMMR]
        deletedIndexArr = np.delete(np.array(termIndexArr),indexOfSelectedFeatureArr)
        newBagOfWords = np.delete(X.toarray(), deletedIndexArr, axis=1)
        self.sNewBagOfWords = sparse.csr_matrix(newBagOfWords)
        self.numOfFeatures = self.sNewBagOfWords.shape[1]
    
    def combi(self,array,numOfElem):
        tmp = list(itertools.combinations(array, numOfElem))
        return np.array([list(i) for i in tmp])
    
    def Merit(self,kRcfRff):
        k = kRcfRff[0]
        rcf = kRcfRff[1]
        rff = kRcfRff[2]
        return k*rcf/(math.sqrt(k+k*(k-1)*rff))

    def featureFeatureSU(self,combiList):
        return self.FCMatrix[combiList[0],combiList[1]]

    def rffCombiAverage(self,combiList):
        tmp = np.sum(np.apply_along_axis(self.featureFeatureSU, 0, combiList), axis=0)
        return tmp

    def createFCMatrix(self):
        FCMatrixObj = FCMatrix(self.sNewBagOfWords,self.Y)
        self.FCMatrix = FCMatrixObj.makeFCMatrix()

    def findIndex(self):
        indexFeatures = []
        for i in range(self.sNewBagOfWords.shape[1]):
            indexFeatures.append(i)
        k=1
        pointer = 0
        parentPointer = 0
        fiveBestIndex = []
        parentBestFiveIndex = []
        bestMeritSoFar = 0.0
        indexOfMaxMerit = []
        selectedIndex = []
        testingLastTwo = 0

        while(True):
            if(k==1):
                tmp = []
                tmp.append([k]*len(indexFeatures))
                tmp.append(self.FCMatrix[:,self.numOfFeatures])
                tmp.append([1]*self.numOfFeatures)
                meritList = np.apply_along_axis(self.Merit, 0, tmp)
                
                meritIndexFeature = np.array([meritList, indexFeatures])
                sortedMeritIndexFeature = meritIndexFeature[:,np.argsort(-meritIndexFeature[0])]
                fiveBestIndex = sortedMeritIndexFeature.T[:5]
                
                indexOfMaxMerit = fiveBestIndex[:,1].astype(np.int16).tolist()
                parentBestFiveIndex = indexOfMaxMerit
                
                selectedIndex.append(indexOfMaxMerit[pointer])
                bestMeritSoFar = meritList[indexOfMaxMerit[pointer]]
                indexFeatures = np.delete(indexFeatures, indexOfMaxMerit[pointer])
                k+=1
                
                if(k>self.numOfFeatures):
                    self.selectedIndex = sorted(selectedIndex)
                    break
            else:
                indexCombine = [selectedIndex + [k] for k in indexFeatures]
                tmp = []
                tmp.append([k]*len(indexFeatures))
                tmp.append(np.mean(self.FCMatrix[indexCombine,self.numOfFeatures],axis=1))
                combiList = np.apply_along_axis(self.combi, 1, indexCombine, 2)
                rffCombiAverageList = np.apply_along_axis(self.rffCombiAverage, 2, combiList)
                rffCombiAverageListAverage = np.mean(rffCombiAverageList, axis = 1)
                tmp.append(rffCombiAverageListAverage)
                meritList = np.apply_along_axis(self.Merit, 0, tmp)
                
                meritIndexFeature = np.array([meritList, indexFeatures])
                sortedMeritIndexFeature = meritIndexFeature[:,np.argsort(-meritIndexFeature[0])]
                fiveBestIndex = sortedMeritIndexFeature.T[:5]
                indexOfMaxMerit = fiveBestIndex[:,1].astype(np.int64)
                bestMerit = fiveBestIndex[fiveBestIndex[:,1]==indexOfMaxMerit[0],0]
                
                if(bestMerit > bestMeritSoFar):
                    bestMeritSoFar = bestMerit
                    selectedIndex.append(indexOfMaxMerit[pointer])
                    parentBestFiveIndex = indexOfMaxMerit
                    indexFeatures = np.delete(indexFeatures, indexFeatures.tolist().index(indexOfMaxMerit[pointer]))
                    pointer = 0
                    k+=1
                    
                    if(k>self.numOfFeatures):
                        self.selectedIndex = sorted(selectedIndex)
                        break
                else:
                    indexFeatures = np.append(indexFeatures, selectedIndex[-1])
                    indexFeatures = np.sort(indexFeatures)
                    selectedIndex.pop()
                    if(len(indexOfMaxMerit)==1 and k>1):
                        testingLastTwo += 1
                        pointer = 0
                        if testingLastTwo==1:
                            indexFeatures = indexFeatures[~(indexFeatures == parentBestFiveIndex[1])]
                            selectedIndex.append(parentBestFiveIndex[1])
                        else:
                            indexFeatures = indexFeatures[~(indexFeatures == parentBestFiveIndex[pointer])]
                            selectedIndex.append(parentBestFiveIndex[0])
                        if(testingLastTwo==2 or pointer==len(indexOfMaxMerit)):
                            self.selectedIndex = sorted(selectedIndex)
                            break
                    else:
                        parentPointer = parentPointer + 1
                        if(parentPointer == len(parentBestFiveIndex)):
                            selectedIndex.append(parentBestFiveIndex[0])
                            self.selectedIndex = sorted(selectedIndex)
                            break
                        selectedIndex.append(parentBestFiveIndex[parentPointer])
                        indexFeatures = indexFeatures[~(indexFeatures == parentBestFiveIndex[parentPointer])]
                    if(pointer == 5):
                        self.selectedIndex = sorted(selectedIndex)
                        break
                    
class multinomialNB(object):
    
    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.listClass = None
        self.class_log_prior_ = None
        self.feature_log_prob_ = None
    
    def fit(self, dataTrain, categorydataTrain):
        datasetUniqueWordcount = dataTrain.shape[1] # group by class
        
        self.listClass = np.unique(categorydataTrain)
        separated = [[x for x, t in zip(dataTrain, categorydataTrain) if t == c] for c in np.unique(categorydataTrain)]
        count_sample = dataTrain.shape[0]
        
        self.class_log_prior_ = [np.log10(len(i) / count_sample) for i in separated] # this is prior probability
        count = np.array([np.array(i).sum(axis=0).toarray() for i in separated])

        countAlpha = np.array([np.array(i).sum(axis=0).toarray() for i in separated])  + self.alpha
        
        self.feature_log_prob_ = [np.log10(countAlpha[i,0,:]/(count[i,0,:].sum(axis=0)+datasetUniqueWordcount)) for i in range(countAlpha.shape[0])]
        return self
    
    def predict(self, dataTest):
        return self.listClass[np.argmax(self.__predict_log_proba(dataTest), axis=1)]
    
    def __predict_log_proba(self, dataTest):
        return [(self.feature_log_prob_ * x).sum(axis=1) + self.class_log_prior_ for x in dataTest]
    
class DFWMultinomialNB(object):
    def __init__(self, alpha=1.0, selectedFeature=[]):
        self.alpha = alpha
        self.listClass = None
        self.class_log_prior_ = None
        self.feature_log_prob_ = None
        selectedFeature = [int(i) for i in selectedFeature]
        print(selectedFeature)
        self.deepWeight = np.array(selectedFeature) + np.array([1]*len(selectedFeature))
        self.datasetUniqueWordcount = len(selectedFeature)
        
    def fit(self, dataTrain, categorydataTrain):

        self.listClass = np.unique(categorydataTrain)
        separated = [[x for x, t in zip(dataTrain, categorydataTrain) if t == c] for c in np.unique(categorydataTrain)]
        count_sample = dataTrain.shape[0]

        self.class_log_prior_ = [(np.log10((len(i)+1) / (count_sample + len(separated)))) for i in separated] # this is prior probability

        tmp = []
        for i in range(len(separated)):
            if(np.array(separated[i]).sum(axis = 0).toarray().shape[1]==0):
                tmp.append([0 for j in range(self.datasetUniqueWordcount)])
            else:
                tmp.append(np.array(separated[i]).sum(axis=0).toarray())
        count = np.array(tmp)
        
        weightedCount = np.array([(x * self.deepWeight).tolist() for x in count])
        
        weightedCountAlpha = np.array(weightedCount)  + self.alpha
        
        self.feature_log_prob_ = [np.log10(weightedCountAlpha[i,0,:]/(weightedCount[i,0,:].sum(axis=0)+self.datasetUniqueWordcount)) for i in range(weightedCountAlpha.shape[0])]
        return self

    def predict_log_proba(self, dataTest):
        if(len(dataTest[0]) == 0):
            dataTest = np.zeros((dataTest.shape[0],self.datasetUniqueWordcount), dtype=int)
            return [(self.feature_log_prob_ * x * self.deepWeight).sum(axis=1) + self.class_log_prior_ for x in dataTest]    
        return [(self.feature_log_prob_ * x * self.deepWeight).sum(axis=1) + self.class_log_prior_ for x in dataTest]

    def predict(self, dataTest):
        return self.listClass[np.argmax(self.predict_log_proba(dataTest), axis=1)]
    
class CrossValidation(object):
    def __init__(self, wordcountLst_Prm, categoryLst_Prm, datasetTotal_Prm, firstIndex_Prm):
        self.wordcountLst = wordcountLst_Prm
        self.categoryLst = categoryLst_Prm
        self.datasetTotal = datasetTotal_Prm
        self.k = 10
        self.firstIndex = firstIndex_Prm
        
        self.accArr = []
        self.preArr = []
        self.recArr = []
        self.f1Arr = []
        self.methodCVIDArr = []
        
    def doValidation(self,selectedFeatureLst_Prm = []):
        fold = 0
        if(self.datasetTotal<10):
            self.k = self.datasetTotal
        if(self.k==5):
            kf = KFold(n_splits = self.k, shuffle = False)
        else:
            kf = KFold(n_splits = self.k, random_state = 7129 ,shuffle = True)
        Result = []
        for train_idx,test_idx in kf.split(self.wordcountLst):
            fold = fold + 1
            
            dataset_train = self.wordcountLst[train_idx,:]
            dataset_test = self.wordcountLst[test_idx,:]
            categoryLst_train = np.array(self.categoryLst)[train_idx]
            categoryLst_test = np.array(self.categoryLst)[test_idx]
            
            test_idx = [int(j)+self.firstIndex.astype(int) for j in list(test_idx)]
            
            if(selectedFeatureLst_Prm != []):
                
                MNB = DFWMultinomialNB(alpha = 1, selectedFeature=selectedFeatureLst_Prm).fit(dataset_train,categoryLst_train)
                predictions = MNB.predict(dataset_test.toarray())
            else:
                MNB = multinomialNB(alpha = 1).fit(dataset_train, categoryLst_train)
                predictions = MNB.predict(dataset_test.toarray())


            acc = accuracy_score(list(categoryLst_test), predictions)
            pre = precision_score(list(categoryLst_test), predictions, average = 'macro')
            rec = recall_score(list(categoryLst_test), predictions, average = 'macro')
            f1  = f1_score(list(categoryLst_test), predictions, average = 'macro')
            self.accArr.append(acc)
            self.preArr.append(pre)
            self.recArr.append(rec)
            self.f1Arr.append(f1)

            Result.append(CVResult_Obj(fold,test_idx,predictions))

        return Result    