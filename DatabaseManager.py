import pymysql
import os
import csv
from SystemMaterial import SFMethod

class DatabaseManager(object):
    def __init__(self, hostStr_Prm, portInt_Prm, userNameStr_Prm, password_Prm, charset_Prm, databaseName_Prm):
        #Build Connection
        self.Conn = pymysql.connect(host=hostStr_Prm, port=portInt_Prm, user = userNameStr_Prm, password = password_Prm, charset = charset_Prm)
        self.ConnCur = self.Conn.cursor()
        self.ConnCur.execute("USE {0}".format(databaseName_Prm))
        self.Conn.commit()
        
    def GetTableData(self,tablenamePrm,datanameLstPrm,columncheckLstPrm,valuecheckLstPrm):
        dataName = ""
        for i in range(0,len(datanameLstPrm)):
            if(i == len(datanameLstPrm)-1):
                dataName += ("{0}".format(datanameLstPrm[i]))
            else:
                dataName += ("{0},".format(datanameLstPrm[i]))
                
        tableCondition = ""
        for i in range(0,len(columncheckLstPrm)):
            if(i == len(columncheckLstPrm)-1):
                tableCondition += ("{0} = \"{1}\"".format(columncheckLstPrm[i],valuecheckLstPrm[i]))
            else:
                tableCondition += ("{0} = \"{1}\" AND ".format(columncheckLstPrm[i],valuecheckLstPrm[i]))
             
        self.ConnCur.execute("SELECT {0} FROM {1} WHERE {2}".format(dataName,tablenamePrm,tableCondition))
        self.Conn.commit()
        Result = self.ConnCur.fetchall()
        return Result
    
    def UpdateTable(self,tablenamePrm,columnnamePrm,newvaluePrm,primarykeyPrm,idPrm):
        executableString = "UPDATE {0} SET {1} = %s WHERE {2} = %s".format(tablenamePrm,columnnamePrm,primarykeyPrm)
        self.ConnCur.execute(executableString,(newvaluePrm,idPrm))
        self.Conn.commit()
        
    def InsertTableData(self,tablenamePrm,columncheckLstPrm,valuecheckLstPrm):
        columncheck = ""
        valuecheck = ""
        for i in range(0,len(columncheckLstPrm)):
            if(i == len(columncheckLstPrm)-1):
                columncheck += ("{0}".format(columncheckLstPrm[i]))
                valuecheck += ("\"{0}\"".format(valuecheckLstPrm[i]))
            else:
                columncheck += ("{0}, ".format(columncheckLstPrm[i]))
                valuecheck += ("\"{0}\", ".format(valuecheckLstPrm[i]))
         
        self.ConnCur.execute("INSERT INTO {0} ({1}) VALUE({2})".format(tablenamePrm,columncheck,valuecheck))
        self.Conn.commit()
        return self.ConnCur.lastrowid
    
    def IsTableExist(self,tablenamePrm,columncheckLstPrm,valuecheckLstPrm):
        tableCondition = ""
        for i in range(0,len(columncheckLstPrm)):
            if(i == len(columncheckLstPrm)-1):
                tableCondition += ("{0} = \"{1}\"".format(columncheckLstPrm[i],valuecheckLstPrm[i]))
            else:
                tableCondition += ("{0} = \"{1}\" AND ".format(columncheckLstPrm[i],valuecheckLstPrm[i]))
        
        self.ConnCur.execute("SELECT * FROM {0} WHERE {1}".format(tablenamePrm,tableCondition))
        self.Conn.commit()
        row_count = self.ConnCur.rowcount
        if(row_count > 0):
            return True
        return False
    
    def IsDatasetExist(self,filelocationPrm):
        _tableName = "dataset"
        columnCheck = ["File_location"]
        valueCheck = [filelocationPrm]
        return self.IsTableExist(_tableName, columnCheck, valueCheck)
    
    def importMethod(self,methodnamePrm,ignumfeaturePrm,mmrnumfeaturePrm,mmrlambdaPrm,isdfwPrm):
        self.ConnCur.execute("INSERT INTO methodfeatureselection (SF_Name, Num_IG_Feature, Num_MMR_Feature, MMR_Lambda, Is_DFW) VALUES(%s,%s,%s,%s,%s)",(methodnamePrm,ignumfeaturePrm,mmrnumfeaturePrm,mmrlambdaPrm,isdfwPrm))
        self.Conn.commit()
        return self.ConnCur.lastrowid
    
    def insertselectedFeature(self,methodnamePrm,FSmethodIdPrm,datasetidPrm,textPrm,textPrm2 = ""):
        columnnamePrm = ""
        if(methodnamePrm == SFMethod.Information_Gain_Maximal_Marginal_Relevance_Feature_Selection.name):
            self.ConnCur.execute("INSERT INTO selectedfeature (SF_ID,Dataset_ID,SelectedFeature_IG,SelectedFeature_MMR) VALUES (\"{1}\",\"{2}\",\"{3}\",\"{4}\")".format(columnnamePrm,FSmethodIdPrm,datasetidPrm,textPrm,textPrm2))
            self.Conn.commit()
            return
        if(methodnamePrm == SFMethod.Information_Gain_Feature_Selection.name):
            columnnamePrm = "SelectedFeature_IG"
        elif(methodnamePrm == SFMethod.Maximal_Marginal_Relevance_Feature_Selection.name):
            columnnamePrm = "SelectedFeature_MMR"    
        self.ConnCur.execute("INSERT INTO selectedfeature (SF_ID,Dataset_ID,{0}) VALUES (\"{1}\",\"{2}\",\"{3}\")".format(columnnamePrm,FSmethodIdPrm,datasetidPrm,textPrm))
        self.Conn.commit()
        
    def getEvaluation(self,datasetID_Prm, selectedMethodPrm, isDfwPrm):
        self.ConnCur.execute("""SELECT * FROM
            (SELECT e.Evaluation_ID, e.Evaluation_Name, e.Accuracy_Mean, e.Presision_Mean, e.Recall_Mean, e.Fmeasure_Mean, mfs.num_ig_feature, mfs.num_MMR_feature, mfs.MMR_Lambda, mfs.Is_DFW
            FROM evaluation e
            LEFT JOIN methodcrossvalidation mcv
            ON e.CV_ID = mcv.CV_ID
            LEFT JOIN methodfeatureselection mfs
            ON mcv.SF_ID = mfs.SF_ID
            WHERE mcv.dataset_ID = %s AND mfs.SF_Name = %s AND mfs.Is_DFW = %s) X
            GROUP BY Evaluation_ID
        """,(datasetID_Prm,selectedMethodPrm, isDfwPrm))
        self.Conn.commit()
        result = self.ConnCur.fetchall()
        
        return result
    
    def getDataresult(self, datasetID_Prm,selectedMethodPrm, isDfwPrm):
        self.ConnCur.execute("""SELECT e.Evaluation_ID, mfs.SF_ID, mcv.CV_Fold, mfs.Num_IG_Feature, mfs.Num_MMR_Feature, mfs.MMR_Lambda, mfs.Is_DFW,
            e.accuracy_mean, e.presision_mean, e.recall_mean, e.fmeasure_mean
            FROM evaluation e
            LEFT JOIN methodcrossvalidation mcv
                ON e.CV_ID = mcv.CV_ID
            LEFT JOIN methodfeatureselection mfs
                ON mcv.SF_ID = mfs.SF_ID
            WHERE mcv.Dataset_ID = %s AND mfs.SF_Name = %s AND mfs.Is_DFW = %s
        """,(datasetID_Prm, selectedMethodPrm, isDfwPrm))
        self.Conn.commit()
        result = self.ConnCur.fetchall()
        
        return result
    
    def getAllEvaluation(self,datasetID_Prm):
        self.ConnCur.execute("""SELECT * FROM
            (SELECT e.Evaluation_ID, e.Evaluation_Name, e.Accuracy_Mean, e.Presision_Mean, e.Recall_Mean, e.Fmeasure_Mean, mfs.num_ig_feature, mfs.num_MMR_feature, mfs.MMR_Lambda, mfs.Is_DFW
            FROM evaluation e
            LEFT JOIN methodcrossvalidation mcv
            ON e.CV_ID = mcv.CV_ID
            LEFT JOIN methodfeatureselection mfs
            ON mcv.SF_ID = mfs.SF_ID
            WHERE mcv.dataset_ID = %s) X
            GROUP BY Evaluation_ID
        """,(datasetID_Prm))
        self.Conn.commit()
        result = self.ConnCur.fetchall()
        
        return result
    
    def getAllDataresult(self, datasetID_Prm):
        self.ConnCur.execute("""SELECT mfs.SF_Name, e.Evaluation_ID, mfs.SF_ID, mcv.CV_Fold, mfs.Num_IG_Feature, mfs.Num_MMR_Feature, mfs.MMR_Lambda, mfs.Is_DFW,
            e.accuracy_mean, e.presision_mean, e.recall_mean, e.fmeasure_mean
            FROM evaluation e
            LEFT JOIN methodcrossvalidation mcv
                ON e.CV_ID = mcv.CV_ID
            LEFT JOIN methodfeatureselection mfs
                ON mcv.SF_ID = mfs.SF_ID
            WHERE mcv.Dataset_ID = %s
        """,(datasetID_Prm))
        self.Conn.commit()
        result = self.ConnCur.fetchall()
        
        return result
    
    def GetLastEvalId(self):
        self.ConnCur.execute("""
            SELECT Evaluation_ID FROM evaluation 
                ORDER BY Evaluation_ID DESC LIMIT 1
        """)
        self.Conn.commit()
        result = self.ConnCur.fetchall()
        if(len(result)>0):
            return int(result[0][0])
        return 0
    
    def UpdateMeanMetric(self, evalID, accMean, preMean, recMean, f1Mean):
        self.ConnCur.execute("""UPDATE evaluation 
        SET 
            Accuracy_Mean = %s,
            Presision_Mean = %s,
            Recall_Mean = %s,
            Fmeasure_Mean = %s
        WHERE Evaluation_ID = %s
        """,(accMean,preMean,recMean,f1Mean,evalID))
        self.Conn.commit()
        
    def getAllProcessRes(self, processResLst_Prm, datasetID_Prm, methodID_Prm = "", methodNameValue_Prm = ""):
        querry = "SELECT newsid, Article_Content, Article_Category FROM newsarticle WHERE dataset_ID = \"{0}\"".format(datasetID_Prm)
        if(processResLst_Prm != []):
            if(len(processResLst_Prm[0]) == 3):
                querry = "SELECT newsid, Article_Content, Article_Category, Article_Casefolding FROM newsarticle WHERE dataset_ID = \"{0}\""
            elif(len(processResLst_Prm[0]) == 4):
                querry = "SELECT newsid, Article_Content, Article_Category, Article_Casefolding, Article_Tokenization FROM newsarticle WHERE dataset_ID = \"{0}\""
            elif(len(processResLst_Prm[0]) == 5):
                querry = "SELECT newsid, Article_Content, Article_Category, Article_Casefolding, Article_Tokenization, Article_StopwordRemoved FROM newsarticle WHERE dataset_ID = \"{0}\""
            elif(len(processResLst_Prm[0]) == 6):
                querry = "SELECT newsid, Article_Content, Article_Category, Article_Casefolding, Article_Tokenization, Article_StopwordRemoved, Article_Stemmed FROM newsarticle WHERE dataset_ID = \"{0}\""
            elif(len(processResLst_Prm[0]) == 7):
                if(methodNameValue_Prm == 1):
                    querry = """
                    SELECT * FROM
                    (
                    SELECT n.newsid, n.Article_Content, n.Article_Category, n.Article_Casefolding, n.Article_Tokenization, n.Article_StopwordRemoved, n.Article_Stemmed, b.BOW_IG
                    FROM newsarticle n
                    LEFT JOIN bagofwords b
                    ON n.newsid = b.newsid
                    WHERE n.dataset_ID = \"{0}\" AND b.SF_ID = \"{1}\"
                    ) X
                    GROUP BY newsid
                    """
                else:
                    querry = """
                    SELECT * FROM
                    (
                    SELECT n.newsid, n.Article_Content, n.Article_Category, n.Article_Casefolding, n.Article_Tokenization, n.Article_StopwordRemoved, n.Article_Stemmed, b.BOW_MMR
                    FROM newsarticle n
                    LEFT JOIN bagofwords b
                    ON n.newsid = b.newsid
                    WHERE n.dataset_ID = \"{0}\" AND b.SF_ID = \"{1}\"
                    ) X
                    GROUP BY newsid
                    """
            if(len(processResLst_Prm[0]) == 8):
                if(methodNameValue_Prm == 1):
                    querry = """
                    SELECT * FROM
                    (
                    SELECT n.newsid, n.Article_Content, n.Article_Category, n.Article_Casefolding, n.Article_Tokenization, n.Article_StopwordRemoved, n.Article_Stemmed, b.BOW_IG, mcv.CV_Fold, t.PredictedCategory
                    FROM newsarticle n
                    LEFT JOIN bagofwords b
                    ON n.newsid = b.newsid
                    LEFT JOIN testresult t
                    ON n.newsid = t.newsid
                    LEFT JOIN methodcrossvalidation mcv
                    ON t.CV_ID = mcv.CV_ID
                    WHERE n.dataset_ID = \"{0}\" AND mcv.SF_ID = \"{1}\" AND b.SF_ID = \"{2}\"
                    ) X
                    GROUP BY newsid
                    """
                else:
                    querry = """
                    SELECT * FROM
                    (
                    SELECT n.newsid, n.Article_Content, n.Article_Category, n.Article_Casefolding, n.Article_Tokenization, n.Article_StopwordRemoved, n.Article_Stemmed, b.BOW_MMR, mcv.CV_Fold, t.PredictedCategory
                    FROM newsarticle n
                    LEFT JOIN bagofwords b
                    ON n.newsid = b.newsid
                    LEFT JOIN testresult t
                    ON n.newsid = t.newsid
                    LEFT JOIN methodcrossvalidation mcv
                    ON t.CV_ID = mcv.CV_ID
                    WHERE n.dataset_ID = \"{0}\" AND mcv.SF_ID = \"{1}\" AND b.SF_ID = \"{2}\"
                    ) X
                    GROUP BY newsid
                    """
        self.ConnCur.execute(querry.format(datasetID_Prm,methodID_Prm,methodID_Prm))
        self.Conn.commit()
        result = self.ConnCur.fetchall()
        
        return result
    
    def getAllProcesss(self, row_Prm, column_Prm, datasetID_Prm, methodID_Prm = "", methodNameValue_Prm = ""):
        querry = "SELECT newsid, Article_Content, Article_Category FROM newsarticle WHERE dataset_ID = \"{0}\"".format(datasetID_Prm)
        if(column_Prm != 0):
            if(column_Prm == 4):
                querry = "SELECT newsid, Article_Content, Article_Category, Article_Casefolding FROM newsarticle WHERE dataset_ID = \"{0}\""
            elif(column_Prm == 5):
                querry = "SELECT newsid, Article_Content, Article_Category, Article_Casefolding, Article_Tokenization FROM newsarticle WHERE dataset_ID = \"{0}\""
            elif(column_Prm == 6):
                querry = "SELECT newsid, Article_Content, Article_Category, Article_Casefolding, Article_Tokenization, Article_StopwordRemoved FROM newsarticle WHERE dataset_ID = \"{0}\""
            elif(column_Prm == 7):
                querry = "SELECT newsid, Article_Content, Article_Category, Article_Casefolding, Article_Tokenization, Article_StopwordRemoved, Article_Stemmed FROM newsarticle WHERE dataset_ID = \"{0}\""
            elif(column_Prm == 8):
                if(methodNameValue_Prm == 1):
                    querry = """
                    SELECT * FROM ( SELECT n.newsid, n.Article_Content, n.Article_Category, n.Article_Casefolding, n.Article_Tokenization, n.Article_StopwordRemoved, n.Article_Stemmed, b.BOW_IG FROM newsarticle n 
                    LEFT JOIN bagofwords b 
                        ON n.newsid = b.newsid 
                    WHERE n.dataset_ID = \"{0}\" AND b.SF_ID = \"{1}\" ) X 
                    GROUP BY newsid
                    """
                else:
                    querry = """
                    SELECT * FROM ( SELECT n.newsid, n.Article_Content, n.Article_Category, n.Article_Casefolding, n.Article_Tokenization, n.Article_StopwordRemoved, n.Article_Stemmed, b.BOW_MMR FROM newsarticle n 
                    LEFT JOIN bagofwords b 
                        ON n.newsid = b.newsid 
                    WHERE n.dataset_ID = \"{0}\" AND b.SF_ID = \"{1}\" ) X 
                    GROUP BY newsid
                    """
            if(column_Prm == 10):
                if(methodNameValue_Prm == 1):
                    querry = """
                    SELECT X.newsid, X.Article_Content, X.Article_Category, X.Article_Casefolding, X.Article_Tokenization, X.Article_StopwordRemoved, X.Article_Stemmed, X.BOW_IG, Y.CV_Fold, Y.PredictedCategory FROM 
                        (SELECT * FROM (SELECT n.newsid, n.Article_Content, n.Article_Category, n.Article_Casefolding, n.Article_Tokenization, n.Article_StopwordRemoved, n.Article_Stemmed, b.BOW_IG FROM newsarticle n 
                            LEFT JOIN bagofwords b 
                                ON n.newsid = b.newsid 
                            WHERE n.dataset_ID = \"{0}\" AND b.SF_ID = \"{1}\") X1 
                            GROUP BY newsid) AS X, 
                        (SELECT * FROM (SELECT mcv.CV_Fold, t.NewsID, t.PredictedCategory FROM testresult t 
                            LEFT JOIN methodcrossvalidation mcv 
                                ON t.CV_ID = mcv.CV_ID 
                            WHERE mcv.Dataset_ID = \"{0}\" AND mcv.SF_ID = \"{1}\") X2 
                            GROUP BY newsid) AS Y
                        WHERE X.newsid = Y.newsid
                    """
                else:
                    querry = """
                    SELECT X.newsid, X.Article_Content, X.Article_Category, X.Article_Casefolding, X.Article_Tokenization, X.Article_StopwordRemoved, X.Article_Stemmed, X.BOW_MMR, Y.CV_Fold, Y.PredictedCategory FROM 
                    (SELECT * FROM (SELECT n.newsid, n.Article_Content, n.Article_Category, n.Article_Casefolding, n.Article_Tokenization, n.Article_StopwordRemoved, n.Article_Stemmed, b.BOW_MMR FROM newsarticle n 
                        LEFT JOIN bagofwords b 
                            ON n.newsid = b.newsid 
                        WHERE n.dataset_ID = \"{0}\" AND b.SF_ID = \"{1}\") X1 
                        GROUP BY newsid) AS X, 
                    (SELECT * FROM (SELECT mcv.CV_Fold, t.NewsID, t.PredictedCategory FROM testresult t 
                        LEFT JOIN methodcrossvalidation mcv 
                            ON t.CV_ID = mcv.CV_ID 
                        WHERE mcv.Dataset_ID = \"{0}\" AND mcv.SF_ID = \"{1}\") X2 
                        GROUP BY newsid) AS Y
                    WHERE X.newsid = Y.newsid
                    """
        querry += str(" LIMIT 200 OFFSET "+ str(row_Prm))
        self.ConnCur.execute(querry.format(datasetID_Prm,methodID_Prm,methodID_Prm))
        self.Conn.commit()
        result = self.ConnCur.fetchall()
        
        return result
    
class NewsDatabase(object):
    def __init__(self):
        self.database = DatabaseManager(hostStr_Prm="localhost", portInt_Prm=3306, userNameStr_Prm="root", password_Prm="password", charset_Prm="utf8", databaseName_Prm="newsclassification3")
        
    def GetDataset(self):
        return self.database.GetTableData("dataset", ["Dataset_ID","Dataset_Name","file_location"], ["Visible"], ["1"])
    
    def SoftDelete(self,datasetID_Prm):
        self.database.UpdateTable("dataset", "Visible", "0", "dataset_ID", datasetID_Prm)
    
    def GetNews(self,datasetID_Prm):
        return self.database.GetTableData("newsarticle", ["NewsID","article_content","article_category","article_casefolding","article_tokenization","article_stopwordremoved","article_stemmed"], ["dataset_id"], [datasetID_Prm])        
    
    def ImportNews(self, filelocationPrm):
        filename = os.path.basename(filelocationPrm)
        self.database.ConnCur.execute("INSERT INTO dataset (Dataset_Name, File_Location, Is_PreProcessed) VALUES(%s,%s,%s)",(filename,filelocationPrm,"0"))
        self.database.Conn.commit()
        
        datasetID = self.database.ConnCur.lastrowid
        
        file1 = open(filelocationPrm, 'r')
        reader = csv.reader(file1)
        for row in reader:
            if row[0] == 'category':
                pass
            else :
                self.database.ConnCur.execute("INSERT INTO newsarticle (Dataset_ID, Article_Content, Article_CaseFolding, Article_Tokenization, Article_StopwordRemoved, Article_Stemmed, Article_Category) VALUES(%s,%s,%s,%s,%s,%s,%s)",(int(datasetID),row[1],"","","","",row[0]))
                self.database.Conn.commit()
        file1.close()   # <---IMPORTANT
        return datasetID
