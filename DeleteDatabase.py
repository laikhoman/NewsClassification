from DatabaseManager import DatabaseManager
import os

def deleteAllFile():
        dirPath1 = "./news_clasification_cache/igDoc"
        fileList1 = os.listdir(dirPath1)
        for fileName in fileList1:
            os.remove(dirPath1+"/"+fileName)
            
        dirPath2 = "./news_clasification_cache/igMMRClass"
        fileList2 = os.listdir(dirPath2)
        for fileName in fileList2:
            os.remove(dirPath2+"/"+fileName)
            
        dirPath3 = "./news_clasification_cache/igMMRClassPair"
        fileList3 = os.listdir(dirPath3)
        for fileName in fileList3:
            os.remove(dirPath3+"/"+fileName)
            
        dirPath4 = "./news_clasification_cache/igMMRHybirdClass"
        fileList4 = os.listdir(dirPath4)
        for fileName in fileList4:
            os.remove(dirPath4+"/"+fileName)
            
        dirPath5 = "./news_clasification_cache/igMMRHybirdClassPair"
        fileList5 = os.listdir(dirPath5)
        for fileName in fileList5:
            os.remove(dirPath5+"/"+fileName)
            
        dirPath6 = "./news_clasification_cache/cfs"
        fileList6 = os.listdir(dirPath6)
        for fileName in fileList6:
            os.remove(dirPath6+"/"+fileName)
            
def doResetAllTable():
    Database = DatabaseManager(hostStr_Prm="localhost", portInt_Prm=3306, userNameStr_Prm="root", password_Prm="", charset_Prm="utf8", databaseName_Prm="newsclassification03")
    Database.ConnCur.execute("""
        SET FOREIGN_KEY_CHECKS = 0;
    """)
    Database.ConnCur.execute("""
        TRUNCATE TABLE evaluation
    """)
    Database.ConnCur.execute("""
        TRUNCATE TABLE testresult
    """)
    Database.ConnCur.execute("""
        TRUNCATE TABLE methodcrossvalidation
    """)
    Database.ConnCur.execute("""
        TRUNCATE TABLE selectedfeature
    """)
    Database.ConnCur.execute("""
        TRUNCATE TABLE bagofwords
    """)
    Database.ConnCur.execute("""
        TRUNCATE TABLE methodfeatureselection
    """)
    Database.ConnCur.execute("""
        TRUNCATE TABLE newsarticle
    """)
    Database.ConnCur.execute("""
        TRUNCATE TABLE dataset
    """)
    Database.ConnCur.execute("""
        SET FOREIGN_KEY_CHECKS = 1;
    """)
    Database.Conn.commit()
    deleteAllFile()
            
doResetAllTable()