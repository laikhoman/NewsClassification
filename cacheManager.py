import os
import csv
import pandas
from SystemMaterial import SFMethod

class cacheManager(object):
    def __init__(self):
        cachePath = "./news_Clasification_Cache/"
        if not os.path.exists(cachePath):
            os.makedirs(cachePath)
    
        cachePath = "./news_Clasification_Cache/igDoc/"
        if not os.path.exists(cachePath):
            os.makedirs(cachePath)
        
        cachePath = "./news_Clasification_Cache/igMMRClass/"
        if not os.path.exists(cachePath):
            os.makedirs(cachePath)
            
        cachePath = "./news_Clasification_Cache/igMMRClassPair/"
        if not os.path.exists(cachePath):
            os.makedirs(cachePath)
            
        cachePath = "./news_Clasification_Cache/igMMRHybirdClass/"
        if not os.path.exists(cachePath):
            os.makedirs(cachePath)
            
        cachePath = "./news_Clasification_Cache/igMMRHybirdClassPair/"
        if not os.path.exists(cachePath):
            os.makedirs(cachePath)
            
        cachePath = "./news_Clasification_Cache/cfs/"
        if not os.path.exists(cachePath):
            os.makedirs(cachePath)
            
    def IsSelectedFeatureExist(self,methodnamePrm,datasetidPrm, igThreshold=""):
        Result = False
        if(methodnamePrm == SFMethod.Information_Gain_Feature_Selection.name):
            _filename= '/news_Clasification_Cache/igDoc/' + str(datasetidPrm) + '.csv'
            # check if file exist
            for file in os.listdir("./news_Clasification_Cache/igDoc/"):
                if '/news_Clasification_Cache/igDoc/' + file == _filename:
                    Result = True
                    break
        elif(methodnamePrm == SFMethod.Maximal_Marginal_Relevance_Feature_Selection.name):
            _filename= '/news_Clasification_Cache/igMMRClass/' + str(datasetidPrm) + '.csv'
            for file in os.listdir("./news_Clasification_Cache/igMMRClass/"):
                
                if '/news_Clasification_Cache/igMMRClass/' + file == _filename:
                    Result = True
                    break
        elif(methodnamePrm == SFMethod.Information_Gain_Maximal_Marginal_Relevance_Feature_Selection.name):
            _filename= '/news_Clasification_Cache/igMMRHybirdClass/' + str(igThreshold) + "_" + str(datasetidPrm) + '.csv'
            for file in os.listdir("./news_Clasification_Cache/igMMRHybirdClass/"):
                if '/news_Clasification_Cache/igMMRHybirdClass/' + file == _filename:
                    Result = True
                    break
        return Result
    
    def isCFSFileExists(self,datasetidPrm):
        Result = False
        _filename = '/news_Clasification_Cache/cfs/' + 'cfs_featureIGMMR_index' + str(datasetidPrm) + '.csv'
        for file in os.listdir("./news_Clasification_Cache/cfs/"):
            if '/news_Clasification_Cache/cfs/' + file == _filename:
                Result = True
                break
        return Result
    
    def isIGMMRFeatureExistsInCfsFile(self, textIgMmrFeaturePrm, fileLocationPrm):
        Result = False
        file1 = open(fileLocationPrm, 'r')
        reader = csv.reader(file1)
        for row in reader:
            if(textIgMmrFeaturePrm==row[0]):
                Result = True
        file1.close()   # <---IMPORTANT    
        return Result
    
    def getSelectedIndexCfs(self,textIgMmrFeaturePrm, fileLocationPrm):
        Result = []
        file1 = open(fileLocationPrm, 'r')
        reader = csv.reader(file1)
        for row in reader:
            if(textIgMmrFeaturePrm==row[0]):
                tmp1 = row[1].split(", ")
                Result = [x for x in tmp1]
        file1.close()   # <---IMPORTANT 
        return Result
    
    def saveSelectedFeatureCFS(self,textIgMmrFeaturePrm,textSelectedIndexCFSPrm,textSelectedFeatureCFSPrm,fileLocationPrm):
        # Do the writing
        file1 = open(fileLocationPrm, 'a', newline='')
        writer = csv.writer(file1)
        writer.writerows([[textIgMmrFeaturePrm,textSelectedIndexCFSPrm,textSelectedFeatureCFSPrm]])
        file1.close()
    
    def makeNewCFSFile(self, datasetidPrm):
        _filename = 'news_Clasification_Cache/cfs/' + 'cfs_featureIGMMR_index' + str(datasetidPrm) + '.csv'
        with open(_filename, 'wb') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    
    def saveSelectedFeaturefile(self,saveLocationPrm,selectedfeaturePrm,datasetidPrm):
        # to write n IG MMR
        fileLoc = saveLocationPrm + str(datasetidPrm) + '.csv'
        with open(fileLoc, 'wb') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL) 
        
        newArr = []
        for i in range(selectedfeaturePrm.shape[0]):
            tmp = selectedfeaturePrm[i,:]
            newArr.append(tmp)
        # Do the writing
        file2 = open(fileLoc, 'w', newline='')
        writer = csv.writer(file2)
        writer.writerows(newArr)
        file2.close()  
        
    def getFileIndexLst(self,methodnamePrm,datasetidPrm, igThreshold_Prm):
        # Do the reading
        Result = 0
        if(methodnamePrm == SFMethod.Information_Gain_Feature_Selection.name):
            fileLoc = './news_Clasification_Cache/igDoc/' + str(datasetidPrm) + '.csv'
            file1 = open(fileLoc, 'r')
            csvfile = csv.reader(file1)
            
            indexList = []
            counter = 0
            for row in csvfile:
                indexList.append(row[1])
                counter = counter + 1
                if(counter==igThreshold_Prm):
                    break
                
            if(len(indexList) > 0):
                Result = indexList
                
            file1.close()   # <---IMPORTANT
            
        return Result
    
    def saveMMRSelectedFeaturefile(self,selectedMMRFeatureLstPrm,datasetidPrm):
        fileLoc = '/news_Clasification_Cache/igMMRClass' + str(datasetidPrm) + '.csv'
        newArr = []
        for i in range(selectedMMRFeatureLstPrm[1]):
            tmp = [selectedMMRFeatureLstPrm[0,i]]
            newArr.append(tmp)
        # Do the writing
        file2 = open(fileLoc, 'w', newline='')
        writer = csv.writer(file2)
        writer.writerows(newArr)
        file2.close()
        
    def readAsDataframe(self,fileLoc):
        return pandas.read_csv(fileLoc,header=None)