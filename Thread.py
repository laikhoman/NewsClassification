from PyQt4 import QtCore
from Algorithm import Textpreprocessing, infoGainDoc, CrossValidation, mmrFS,\
    cfs
from DatabaseManager import NewsDatabase
from SystemMaterial import BagOfWords_Obj, SFMethod
from cacheManager import cacheManager
import pymysql
from datetime import datetime                    

class CasefoldingThrd(QtCore.QThread):
    def __init__(self, datasetLst_Prm):
        super(CasefoldingThrd,self).__init__()
        
        self.dataIDLst = datasetLst_Prm[:,0]
        self.dataLst = datasetLst_Prm[:,1]
        self.newsDatabase = NewsDatabase()
    
    def __del__(self):
        self.wait()
    
    def run(self):
        resultCasefolding = []
        for i in range (0, len(self.dataLst)):
            Preprocess = Textpreprocessing(self.dataLst[i])
            casefolded = Preprocess.casefolding()
            
            resultCasefolding.append(casefolded)
            self.newsDatabase.database.UpdateTable("newsarticle", "article_casefolding", casefolded, "newsid", str(self.dataIDLst[i]))
            
            progressValue = i/len(self.dataLst) * 100 
            self.emit(QtCore.SIGNAL("SetProgressBar(int)"), progressValue)            
        
        self.emit(QtCore.SIGNAL("Done(QStringList)"), resultCasefolding)

class TokenizationThrd(QtCore.QThread):
    def __init__(self, datasetLst_Prm):
        super(TokenizationThrd,self).__init__()
        
        self.dataIDLst = datasetLst_Prm[:,0]
        self.dataLst = datasetLst_Prm[:,3]
        self.newsDatabase = NewsDatabase()
    
    def __del__(self):
        self.wait()
    
    def run(self):
        resultTokenization = []
        for i in range (0, len(self.dataLst)):
            Preprocess = Textpreprocessing(self.dataLst[i])
            tokenization = Preprocess.tokenization()
            
            resultTokenization.append(tokenization)
            self.newsDatabase.database.UpdateTable("newsarticle", "article_tokenization", tokenization, "newsid", str(self.dataIDLst[i]))
            
            progressValue = i/len(self.dataLst) * 100 
            self.emit(QtCore.SIGNAL("SetProgressBar(int)"), progressValue) 
            
        self.emit(QtCore.SIGNAL("Done(QStringList)"), resultTokenization)
        
class RemoveStopwordThrd(QtCore.QThread):
    def __init__(self, datasetLst_Prm):
        super(RemoveStopwordThrd,self).__init__()
        
        self.dataIDLst = datasetLst_Prm[:,0]
        self.dataLst = datasetLst_Prm[:,4]
        self.newsDatabase = NewsDatabase()
    
    def __del__(self):
        self.wait()
    
    def run(self):
        resultRemoveStopword = []
        for i in range (0, len(self.dataLst)):
            Preprocess = Textpreprocessing(self.dataLst[i])
            removeStopword = Preprocess.removeStopwords()
            
            resultRemoveStopword.append(removeStopword)
            self.newsDatabase.database.UpdateTable("newsarticle", "article_stopwordremoved", removeStopword, "newsid", str(self.dataIDLst[i]))
            
            progressValue = i/len(self.dataLst) * 100 
            self.emit(QtCore.SIGNAL("SetProgressBar(int)"), progressValue) 
            
        self.emit(QtCore.SIGNAL("Done(QStringList)"), resultRemoveStopword)
        
class StemmingThrd(QtCore.QThread):
    def __init__(self, datasetLst_Prm):
        super(StemmingThrd,self).__init__()
        
        self.dataIDLst = datasetLst_Prm[:,0]
        self.dataLst = datasetLst_Prm[:,5]
        self.newsDatabase = NewsDatabase()
    
    def __del__(self):
        self.wait()
    
    def run(self):
        resultStemming = []
        for i in range (0, len(self.dataLst)):
            Preprocess = Textpreprocessing(self.dataLst[i])
            Stemmed = Preprocess.Stemming()
            
            resultStemming.append(Stemmed)
            self.newsDatabase.database.UpdateTable("newsarticle", "article_stemmed", Stemmed, "newsid", str(self.dataIDLst[i]))
            
            progressValue = i/len(self.dataLst) * 100 
            self.emit(QtCore.SIGNAL("SetProgressBar(int)"), progressValue) 
            
        self.emit(QtCore.SIGNAL("Done(QStringList)"), resultStemming)
        
class IGFindFeaturesThrd(QtCore.QThread):   
    def __init__(self,thresholdPrm,datacorpusPrm, databaseID_Prm, selectedFeatureMethodID_Prm, newsIDLst_Prm):
        super(IGFindFeaturesThrd,self).__init__()
        
        self.igfeatureselector = infoGainDoc(thresholdPrm, datacorpusPrm)
        self.threshold = thresholdPrm
        self.selectedFeatureMethodID = selectedFeatureMethodID_Prm
        self.databaseID = databaseID_Prm
        self.cacheManager = cacheManager()
        self.dataCorpus = datacorpusPrm
        self.maxFeature = 1000
        self.newsIDLst = newsIDLst_Prm
        
    def __saveDatabaseBOW(self, selectedFeatureLst_Prm):
        BOWIG = BagOfWords_Obj(self.dataCorpus,self.maxFeature)
        self.TextLst = BOWIG.getWordCountinTextLstWithSelectedFeature(selectedFeatureLst_Prm)
        newsID = self.newsIDLst
        
        try:
            for i in range (len(self.TextLst)):
                NewsDatabase().database.InsertTableData("bagofwords", ["SF_ID","NewsID","BOW_IG"], [self.selectedFeatureMethodID,newsID[i],self.TextLst[i]])
            try:        
                text = ', '.join(selectedFeatureLst_Prm[:-1]) + ', ' + selectedFeatureLst_Prm[-1]
                NewsDatabase().database.insertselectedFeature(SFMethod.Information_Gain_Feature_Selection.name, self.selectedFeatureMethodID, self.databaseID, text)
            except IndexError:
                print("Use IG but not IG")
        except pymysql.err.IntegrityError:
            print("Thread Integrity error")    
    
    def __del__(self):
        self.wait()
    
    def run(self):
        Result = []
        tableData = NewsDatabase().database.GetTableData("selectedfeature", ["selectedfeature_ig"], ["SF_ID","Dataset_ID"], [self.selectedFeatureMethodID,self.databaseID])
        
        if(tableData != ()):
            Result = tableData[0][0].split(", ")
        else:
            if(self.cacheManager.IsSelectedFeatureExist(SFMethod.Information_Gain_Feature_Selection.name, self.databaseID)):
                IndexLst = self.cacheManager.getFileIndexLst(SFMethod.Information_Gain_Feature_Selection.name, self.databaseID, self.threshold)
                Result = self.igfeatureselector.getSelectedResult(IndexLst_Prm=IndexLst)
            else:
                FeatureIGResult = self.igfeatureselector.findFeatures()
                Result = self.igfeatureselector.getSelectedResult()
                self.cacheManager.saveSelectedFeaturefile("news_Clasification_Cache/igDoc/",FeatureIGResult, self.databaseID)
            
        self.__saveDatabaseBOW(Result)
        
        self.emit(QtCore.SIGNAL("DONE(QStringList, QStringList)"),self.TextLst, Result)

class MMRFindFeatureThrd(QtCore.QThread):
    def __init__(self,thresholdPrm, lambdaPrm, databaseID_Prm, selectedFeatureMethodID_Prm, dataCorpus_Prm, dataIDLst_Prm, dataCategoryLst_Prm, IGSelectedfeaturePrm = []):
        super(MMRFindFeatureThrd,self).__init__()
        
        self.selectedFeatureMethodID = selectedFeatureMethodID_Prm
        self.databaseID = databaseID_Prm
        self.dataCorpus = dataCorpus_Prm
        self.dataIDLst = dataIDLst_Prm
        self.dataCategoryLst = dataCategoryLst_Prm
        self.maxFeature = 1000
        self.threshold = thresholdPrm
        self.MMRlambda = lambdaPrm 
        self.cacheManager = cacheManager()
        
    
    def __saveDatabaseBOW(self, selectedFeatureLst_Prm, selectedFeatureLst_Prm2 = []):
        BOWMMR = BagOfWords_Obj(self.dataCorpus,self.maxFeature)
        self.TextLst = BOWMMR.getWordCountinTextLstWithSelectedFeature(selectedFeatureLst_Prm)
        newsID = self.dataIDLst
        try:
            for i in range (len(self.TextLst)):
                NewsDatabase().database.InsertTableData("bagofwords", ["SF_ID","NewsID","BOW_MMR"], [self.selectedFeatureMethodID,newsID[i],self.TextLst[i]])
                
            text = ', '.join(selectedFeatureLst_Prm[:-1]) + ', ' + selectedFeatureLst_Prm[-1]
            NewsDatabase().database.insertselectedFeature(SFMethod.Maximal_Marginal_Relevance_Feature_Selection.name, self.selectedFeatureMethodID, self.databaseID, text)
        except pymysql.err.IntegrityError:
            print("Thread Integrity Error")
     
    def run(self):
        Result = []
        tableData = NewsDatabase().database.GetTableData("selectedfeature", ["selectedfeature_MMR"], ["SF_ID","Dataset_ID"], [self.selectedFeatureMethodID,self.databaseID])
                
        if(tableData != ()):
            Result = tableData[0][0].split(", ")
        else:
            newsCategory = self.dataCategoryLst
            self.dataCorpus = self.dataCorpus
            mmrfeatureselector = mmrFS(self.threshold,self.MMRlambda,self.dataCorpus,newsCategory)
            

            if(self.cacheManager.IsSelectedFeatureExist(SFMethod.Maximal_Marginal_Relevance_Feature_Selection.name, self.databaseID) == False):
                self.cacheManager.saveSelectedFeaturefile("news_Clasification_Cache/igMMRClass/", mmrfeatureselector.getIndexigMMR(), self.databaseID)
                self.cacheManager.saveSelectedFeaturefile("news_Clasification_Cache/igMMRClassPair/", mmrfeatureselector.getIndexIGPairMMR(), self.databaseID)
                                
            igMMRClass_filename = "news_Clasification_Cache/igMMRClass/{0}.csv".format(self.databaseID)
            igMMRClassPair_filename = "news_Clasification_Cache/igMMRClassPair/{0}.csv".format(self.databaseID)
            igMMRClassDf = self.cacheManager.readAsDataframe(igMMRClass_filename)
            igMMRClassPairDf = self.cacheManager.readAsDataframe(igMMRClassPair_filename)
                
            Result = mmrfeatureselector.doMMRFS(igMMRClassDf, igMMRClassPairDf)
            
        self.__saveDatabaseBOW(Result)
        
        self.emit(QtCore.SIGNAL("DONE(QStringList, QStringList)"),self.TextLst, Result)
        
class IGMMRFindFeatureThrd(QtCore.QThread):
    def __init__(self,IGthresholdPrm, MMRthresholdPrm, lambdaPrm, isdfwPrm, databaseID_Prm, selectedFeatureMethodID_Prm, dataCorpus_Prm, dataIDLst_Prm, dataCategoryLst_Prm):
        super(IGMMRFindFeatureThrd,self).__init__()
        
        self.maxFeature = 1000
        self.igThreshold = IGthresholdPrm
        self.mmrThreshold = MMRthresholdPrm
        self.mmrLambda = lambdaPrm
        self.isdfw = isdfwPrm
        self.databaseID = databaseID_Prm
        self.selectedFeatureMethodID = selectedFeatureMethodID_Prm
        self.dataCorpus = dataCorpus_Prm
        self.dataIDLst = dataIDLst_Prm
        self.dataCategoryLst = dataCategoryLst_Prm
        self.cacheManager = cacheManager()
    
    def __saveDatabaseBOW(self, selectedFeatureLst_Prm, selectedFeatureLst_Prm2 = []):
        self.BOWIGMMR = BagOfWords_Obj(self.dataCorpus,self.maxFeature)
        self.TextLst = self.BOWIGMMR.getWordCountinTextLstWithSelectedFeature(selectedFeatureLst_Prm2)
        self.TextLst2 = self.BOWIGMMR.getWordCountinTextLstWithSelectedFeature(selectedFeatureLst_Prm)
        newsID = self.dataIDLst
        try:
            for i in range (len(self.TextLst)):
                NewsDatabase().database.InsertTableData("bagofwords", ["SF_ID","NewsID","BOW_IG","BOW_MMR"], [self.selectedFeatureMethodID,newsID[i],self.TextLst[i],self.TextLst2[i]])
                
            text1 = ', '.join(selectedFeatureLst_Prm2[:-1]) + ', ' + selectedFeatureLst_Prm2[-1]
            text2 = ', '.join(selectedFeatureLst_Prm[:-1]) + ', ' + selectedFeatureLst_Prm[-1]
            NewsDatabase().database.insertselectedFeature(SFMethod.Information_Gain_Maximal_Marginal_Relevance_Feature_Selection.name, self.selectedFeatureMethodID, self.databaseID, text1,text2)
        except pymysql.err.IntegrityError:
            print("Thread Integrity Error")
    
    def IGFindFeature(self):
        self.igfeatureselector = infoGainDoc(self.igThreshold, self.dataCorpus)
        Result = []
        tableData = NewsDatabase().database.GetTableData("selectedfeature", ["selectedfeature_ig"], ["SF_ID","Dataset_ID"], [self.selectedFeatureMethodID,self.databaseID])
        
        if(tableData != ()):
            Result = tableData[0][0].split(", ")
        else:
            if(self.cacheManager.IsSelectedFeatureExist(SFMethod.Information_Gain_Feature_Selection.name, self.databaseID)):
                IndexLst = self.cacheManager.getFileIndexLst(SFMethod.Information_Gain_Feature_Selection.name, self.databaseID, self.igThreshold)
                Result = self.igfeatureselector.getSelectedResult(IndexLst_Prm=IndexLst)
            else:
                FeatureIGResult = self.igfeatureselector.findFeatures()
                Result = self.igfeatureselector.getSelectedResult()
                self.cacheManager.saveSelectedFeaturefile("news_Clasification_Cache/igDoc/",FeatureIGResult, self.databaseID)
                
        return Result
    
    def __selectedFeatureCFS(self,dataCorpusLst_Prm, categoryLst_Prm, selectedFeature=[]):
        selectedIndexCFS = []
        textIgMmrFeature = ', '.join(selectedFeature[:-1]) + ', ' + selectedFeature[-1]
        fileLocation = 'news_Clasification_Cache/cfs/' + 'cfs_featureIGMMR_index' + str(self.databaseID) + '.csv'
        if(self.cacheManager.isCFSFileExists(self.databaseID)):
            if(self.cacheManager.isIGMMRFeatureExistsInCfsFile(textIgMmrFeature,fileLocation)):
                selectedIndexCFS = self.cacheManager.getSelectedIndexCfs(textIgMmrFeature, fileLocation)
            else:
                cfsSelector = cfs(dataCorpusLst_Prm.tolist(), categoryLst_Prm.tolist(),selectedFeature, self.maxFeature)
                cfsSelector.createFCMatrix()
                cfsSelector.findIndex()
                for i in range(len(selectedFeature)):
                    if(i in cfsSelector.selectedIndex):
                        selectedIndexCFS.append("1")
                    else: selectedIndexCFS.append("0")
                strSelectedIndexCFS = [x for x in selectedIndexCFS]    
                selectedFeaturesCFS = [selectedFeature[i] for i in cfsSelector.selectedIndex]
                textSelectedIndexCFS = ', '.join(strSelectedIndexCFS[:-1]) + ', ' + strSelectedIndexCFS[-1]
                textSelectedFeatureCFS = ', '.join(selectedFeaturesCFS[:-1]) + ', ' + selectedFeaturesCFS[-1] 
                self.cacheManager.saveSelectedFeatureCFS(textIgMmrFeature, textSelectedIndexCFS, textSelectedFeatureCFS, fileLocation)
        else:
            self.cacheManager.makeNewCFSFile(self.databaseID)
            cfsSelector = cfs(dataCorpusLst_Prm.tolist(), categoryLst_Prm.tolist(),selectedFeature, self.maxFeature)
            cfsSelector.createFCMatrix()
            cfsSelector.findIndex()
            for i in range(len(selectedFeature)):
                if(i in cfsSelector.selectedIndex):
                    selectedIndexCFS.append("1")
                else: selectedIndexCFS.append("0")
            strSelectedIndexCFS = [x for x in selectedIndexCFS]    
            selectedFeaturesCFS = [selectedFeature[i] for i in cfsSelector.selectedIndex]
            textSelectedIndexCFS = ', '.join(strSelectedIndexCFS[:-1]) + ', ' + strSelectedIndexCFS[-1]
            textSelectedFeatureCFS = ', '.join(selectedFeaturesCFS[:-1]) + ', ' + selectedFeaturesCFS[-1] 
            self.cacheManager.saveSelectedFeatureCFS(textIgMmrFeature, textSelectedIndexCFS, textSelectedFeatureCFS, fileLocation)

        return selectedIndexCFS
    
    def run(self):
        Result = []
        tableData = NewsDatabase().database.GetTableData("selectedfeature", ["selectedfeature_IG","selectedfeature_MMR"], ["SF_ID","Dataset_ID"], [self.selectedFeatureMethodID,self.databaseID])
        
        if(tableData != ()):
            selectedFeatureIG = tableData[0][0].split(", ")
            Result = tableData[0][1].split(", ")
        else:
            newsCategory = self.dataCategoryLst
            dataCorpus = self.dataCorpus
            selectedFeatureIG = self.IGFindFeature()
            
            mmrfeatureselector = mmrFS(self.mmrThreshold,self.mmrLambda,dataCorpus,newsCategory,selectedFeatureIG)
            
            if(self.cacheManager.IsSelectedFeatureExist(SFMethod.Information_Gain_Maximal_Marginal_Relevance_Feature_Selection.name, self.databaseID,self.igThreshold) == False):
                self.cacheManager.saveSelectedFeaturefile("news_Clasification_Cache/igMMRHybirdClass/{0}_".format(self.igThreshold), mmrfeatureselector.getIndexigMMR(), self.databaseID)
                self.cacheManager.saveSelectedFeaturefile("news_Clasification_Cache/igMMRHybirdClassPair/{0}_".format(self.igThreshold), mmrfeatureselector.getIndexIGPairMMR(), self.databaseID)
                
            igMMRClass_filename = "news_Clasification_Cache/igMMRHybirdClass/{0}_{1}.csv".format(self.igThreshold,self.databaseID)
            igMMRClassPair_filename = "news_Clasification_Cache/igMMRHybirdClassPair/{0}_{1}.csv".format(self.igThreshold,self.databaseID)
            igMMRClassDf = self.cacheManager.readAsDataframe(igMMRClass_filename)
            igMMRClassPairDf = self.cacheManager.readAsDataframe(igMMRClassPair_filename)
                
            Result = mmrfeatureselector.doMMRFS(igMMRClassDf, igMMRClassPairDf)
            
        self.__saveDatabaseBOW(Result, selectedFeatureIG)
            
        if(self.isdfw == 0):
            self.emit(QtCore.SIGNAL("DONE(QStringList, QStringList)"), self.TextLst2, Result)
        else:
            selectedFeatureIGMMR = Result
            self.selectedIndexCFS = self.__selectedFeatureCFS(self.dataCorpus,self.dataCategoryLst,selectedFeatureIGMMR)
            self.emit(QtCore.SIGNAL("DONE(QStringList, QStringList, QStringList)"), self.TextLst2, Result, self.selectedIndexCFS)
            
class GetProcessDetailThrd(QtCore.QThread):
    def __init__(self, row, tabledata_Prm, dataCorpus_Prm, selectedMethod_Prm, selectedFeaturePrm):
        super(GetProcessDetailThrd,self).__init__()
        self.tabledata = tabledata_Prm
        self.dataCorpus = dataCorpus_Prm
        self.selectedMethod = selectedMethod_Prm
        self.selectedFeature = selectedFeaturePrm
        self.row = row
        
    def run(self):
        Result = "Process Detail :\n\n"
        if(self.tabledata.columnCount() > 2):
            Result += "-> Content Article : {0}\n".format(self.tabledata.item(self.row,1).text())
            Result += "-> Category Article : {0}\n\n".format(self.tabledata.item(self.row,2).text())
        if(self.tabledata.columnCount() > 3):
            Result += "1. Casefolding Result:\n{0}\n\n".format(self.tabledata.item(self.row,3).text())
        if(self.tabledata.columnCount() > 4):
            Result += "2. Tokenization Result:\n{0}\n\n".format(self.tabledata.item(self.row,4).text())
        if(self.tabledata.columnCount() > 5):
            Result += "3. Stopword Removed Result:\n{0}\n\n".format(self.tabledata.item(self.row,5).text())
            
        if(self.tabledata.columnCount() > 6):
            stemmedLst = self.dataCorpus
            BOW = BagOfWords_Obj(stemmedLst,1000)
            if(self.tabledata.columnCount() > 6):
                Result += "4. Stemming Algorithm (Total Unique Feature : {0})\n".format(len(BOW.uniqueFeatureLst))
                for i in range (0,len(BOW.uniqueFeatureLst)):
                    WordFreq = 0
                    #for j in range(0,len(BOW.get2dArrayform())):
                    WordFreq += BOW.wordCountLst[:,i].sum(axis=0)
                    Result += "- {0} : {1}\n".format(BOW.uniqueFeatureLst[i],WordFreq[0,0])
            if(self.tabledata.columnCount() > 7):
                Result += "\n5. {0}'s Result :\n".format(self.selectedMethod)
                tmp1 = BOW.get2dArrayform()[self.row]
                tmp2 = BOW.uniqueFeatureLst
                    
                sorted1, sorted2 = (list(j) for j in zip(*sorted(zip(tmp1, tmp2))))
                
                for idx in range (0,len(BOW.uniqueFeatureLst)):
                    i = len(BOW.uniqueFeatureLst)-1 - idx
                    if(sorted2[i] in self.selectedFeature):
                        Result += "- {0} : {1}\n".format(sorted2[i],sorted1[i])
            
        if(self.tabledata.columnCount() > 8):
            Result += "\n6. Fold: {0}\n\n7. Predicted Category: {1}".format(self.tabledata.item(self.row,8).text(), self.tabledata.item(self.row,9).text())
        
        self.emit(QtCore.SIGNAL("DONE(QString)"),Result)
                
class ClasifyDataThrd(QtCore.QThread):
    def __init__(self, databaseID_Prm, selectedFeatureMethodID_Prm, mainselectedFeatureLst_Prm, dataCorpus_Prm, dataIDLst_Prm, dataCategoryLst_Prm, selectedFeatureLst_Prm = []):
        super(ClasifyDataThrd,self).__init__()
        
        self.databaseID = databaseID_Prm
        self.selectedFeatureMethodID = selectedFeatureMethodID_Prm
        self.selectedFeature = mainselectedFeatureLst_Prm
        self.selectedFeatureCFS = selectedFeatureLst_Prm
        self.maxFeature = 1000
        self.dataCorpus = dataCorpus_Prm
        self.newsCategory = dataCategoryLst_Prm
        self.newsID = dataIDLst_Prm
    
    def __del__(self):
        self.wait()
     
    def run(self):
        BOW = BagOfWords_Obj(self.dataCorpus,self.maxFeature)
        selectedFeatureIdx = BOW.filterWordcount(self.selectedFeature)
        
        nbClasify_CV = CrossValidation(selectedFeatureIdx, self.newsCategory,len(self.newsID),self.newsID[0])  
        if(self.selectedFeatureCFS != []):
            
            CrossValidateResult = nbClasify_CV.doValidation(selectedFeatureLst_Prm=self.selectedFeatureCFS)
        else:
            CrossValidateResult = nbClasify_CV.doValidation()
              
        fold_arr = []
        predicted_arr = []
        for i in range(0, len(CrossValidateResult)):            
            if(not NewsDatabase().database.IsTableExist("methodcrossvalidation", ["Dataset_ID","SF_ID","CV_fold"], [self.databaseID,self.selectedFeatureMethodID,CrossValidateResult[i].Fold])):
                CVMethodID = NewsDatabase().database.InsertTableData("methodcrossvalidation", ["Dataset_ID","SF_ID","CV_fold"], [self.databaseID,self.selectedFeatureMethodID,CrossValidateResult[i].Fold])
            else:
                CVMethodID = NewsDatabase().database.GetTableData("methodcrossvalidation", ["CV_ID"], ["Dataset_ID","SF_ID","CV_fold"], [self.databaseID,self.selectedFeatureMethodID,CrossValidateResult[i].Fold])[0][0]
                
            for j in range(0, len(CrossValidateResult[i].PredictedCategory)):
                fold_arr.append(str(CrossValidateResult[i].Fold))
                NewsDatabase().database.InsertTableData("testresult", ["CV_ID","NewsID","datetimetesting","predictedcategory"], [CVMethodID,CrossValidateResult[i].TextIdx[j],datetime.now().strftime('%Y-%m-%d %H:%M:%S'),CrossValidateResult[i].PredictedCategory[j]])
                predicted_arr.append(CrossValidateResult[i].PredictedCategory[j])
                
                ProgressValue = ((i*len(CrossValidateResult[i].PredictedCategory))+j)/len(CrossValidateResult)/len(CrossValidateResult[i].PredictedCategory) * 100
                self.emit(QtCore.SIGNAL("SetProgressBar(int)"),ProgressValue)
        
        
        self.accArr = [str(i) for i in nbClasify_CV.accArr]
        self.preArr = [str(i) for i in nbClasify_CV.preArr]
        self.recArr = [str(i) for i in nbClasify_CV.recArr]
        self.f1Arr = [str(i) for i in nbClasify_CV.f1Arr]
        
        self.emit(QtCore.SIGNAL("DONE(QStringList, QStringList)"), fold_arr, predicted_arr) 
        self.emit(QtCore.SIGNAL("GetEvaluation(QStringList, QStringList, QStringList, QStringList)"),self.accArr, self.preArr, self.recArr, self.f1Arr)             