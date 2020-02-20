from Widget import ProcessPage, ViewResult
from Dialog import OpenDialog, saveDialog
from DatabaseManager import NewsDatabase
from SystemMaterial import SFMethod

from PyQt4 import QtGui,QtCore
import sys

class mainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(mainWindow,self).__init__()
        
        width = QtGui.QDesktopWidget().screenGeometry().width()
        height = QtGui.QDesktopWidget().screenGeometry().height()
        framewidth = width * 1
        frameheight = height * 1
        
        self.setGeometry(QtCore.QRect(width/2 - framewidth/2, height/2 - frameheight/2, framewidth, frameheight))
        self.setWindowTitle("News Classification")
        self.setWindowIcon(QtGui.QIcon(''))
        
        #Set MenuBar
        menuBar = QtGui.QMenuBar()
            
        menuBar_file = QtGui.QMenu("File",self)
        menuBar_file_open = QtGui.QAction("Open",self)
        menuBar_file_open.triggered.connect(self.menuBar_file_open_Clicked)
        menuBar_file_save = QtGui.QAction("Save",self)
        menuBar_file_save.triggered.connect(self.menuBar_file_save_Clicked)
        #menuBar_file_viewrslt.triggered.connect(self.Resultpage)
        
        menuBar_file_exit = QtGui.QAction("Exit",self)
        menuBar_file_exit.setShortcut("esc")
        menuBar_file_exit.triggered.connect(sys.exit)
        
        menuBar_file.addAction(menuBar_file_open)
        menuBar_file.addAction(menuBar_file_save)
        menuBar_file.addAction(menuBar_file_exit)
        
        menuBar_process = QtGui.QMenu("Process",self)
        menuBar_process_IG = QtGui.QAction("Information Gain Feature Selection",self)
        menuBar_process_IG.triggered.connect(self.menuBar_process_IG_Clicked)
        menuBar_process_MMR = QtGui.QAction("Maximal Marginal Relevance Feature Selection",self)
        menuBar_process_MMR.triggered.connect(self.menuBar_process_MMR_Clicked)
        menuBar_process_IGMMR = QtGui.QAction("Information Gain Maximal Marginal Relevance Feature Selection",self)
        menuBar_process_IGMMR.triggered.connect(self.menuBar_process_IGMMR_Clicked)
        
        menuBar_process.addAction(menuBar_process_IG)
        menuBar_process.addAction(menuBar_process_MMR)
        menuBar_process.addAction(menuBar_process_IGMMR)
        
        menuBar_evaluate = QtGui.QMenu("Evaluate",self)
        menuBar_evaluate_Compare = QtGui.QAction("Compare",self)
        menuBar_evaluate_Compare.triggered.connect(self.menuBar_evaluate_Clicked)
        
        menuBar_evaluate.addAction(menuBar_evaluate_Compare)
        
        menuBar.addMenu(menuBar_file)
        menuBar.addMenu(menuBar_process)
        menuBar.addMenu(menuBar_evaluate)
        self.setMenuBar(menuBar)
        
        self.newsDatabase = NewsDatabase()
        self.showMaximized()
    
    def menuBar_process_IG_Clicked(self):
        try:        
            self.processPage = ProcessPage(self, SFMethod.Information_Gain_Feature_Selection.name)
            self.processPage.AsignDatabaseID(self.databaseID)
                    
            self.setCentralWidget(self.processPage)
            self.showMaximized()
        except AttributeError:
            self.__generateWarningDialog("Oopss!!\nNo File was opened at the moment !!")
        
    def menuBar_process_MMR_Clicked(self):
        try:
            self.processPage = ProcessPage(self, SFMethod.Maximal_Marginal_Relevance_Feature_Selection.name)
            self.processPage.AsignDatabaseID(self.databaseID)
                
            self.setCentralWidget(self.processPage)
            self.showMaximized()
        except AttributeError:
            self.__generateWarningDialog("Oopss!!\nNo File was opened at the moment !!")
            
    def menuBar_process_IGMMR_Clicked(self):
        try:
            self.processPage = ProcessPage(self, SFMethod.Information_Gain_Maximal_Marginal_Relevance_Feature_Selection.name)
            self.processPage.AsignDatabaseID(self.databaseID)
            
            self.setCentralWidget(self.processPage)
            self.showMaximized()
        except AttributeError:
            self.__generateWarningDialog("Oopss!!\nNo File was opened at the moment !!")
    
    def menuBar_file_open_Clicked(self):
        self.openDialog = OpenDialog(self)
        self.openDialog.show()
        self.connect(self.openDialog, QtCore.SIGNAL("AsignDatabaseID(int)"), self.__AsignDatabaseID)
        
    def menuBar_file_save_Clicked(self):
        try:
            if(self.processPage.EnableSave):
                self.saveDialog = saveDialog(self)
                self.saveDialog.show()
                self.connect(self.saveDialog, QtCore.SIGNAL("StoreEvaluation(QString)"), self.__StoreEvaluation)
            else:
                self.__generateWarningDialog("Finish the clasification beforehand")
        except AttributeError:
            self.__generateWarningDialog("No Evaluation to Save!!")
        
    def menuBar_evaluate_Clicked(self):
        self.evaluatePage = ViewResult() 
        self.setCentralWidget(self.evaluatePage)
        self.showMaximized()
    
    def __StoreEvaluation(self, resultname):
        lastEvalId = NewsDatabase().database.GetLastEvalId()
        evaluationID = lastEvalId + 1
        evalName = resultname
        foldArr = [i for i in self.processPage.foldArr]
        CVMethodID = NewsDatabase().database.GetTableData("methodcrossvalidation", ["CV_ID"], ["Dataset_ID","SF_ID"], [self.processPage.databaseID, self.processPage.selectedFeatureMethodID])
        
        for i in range(len(CVMethodID)):
            NewsDatabase().database.InsertTableData("evaluation", ["Evaluation_ID","CV_ID","Evaluation_Name","Accuracy","Presision","Recall","Fmeasure"], [evaluationID,CVMethodID[i][0],evalName,float(self.processPage.accArr[i]),float(self.processPage.preArr[i]),float(self.processPage.recArr[i]),float(self.processPage.f1Arr[i])])
            
        accMean = float(sum(self.processPage.accArr)/len(self.processPage.accArr))
        preMean = float(sum(self.processPage.preArr)/len(self.processPage.preArr))
        recMean = float(sum(self.processPage.recArr)/len(self.processPage.recArr))
        f1Mean = float(sum(self.processPage.f1Arr)/len(self.processPage.f1Arr))
        NewsDatabase().database.UpdateMeanMetric(evaluationID,accMean,preMean,recMean,f1Mean)
        
    def __AsignDatabaseID(self, databaseID_Prm):
        self.databaseID = databaseID_Prm
    
    def __generateWarningDialog(self,warningStr_Prm):
        errordialog = None
        errordialog = QtGui.QMessageBox()
        errordialog.setIcon(QtGui.QMessageBox.Warning)
        errordialog.setText(warningStr_Prm)
        errordialog.addButton(QtGui.QMessageBox.Ok)
        errordialog.exec_()

app = QtGui.QApplication(sys.argv)
GUI = mainWindow()
sys.exit(app.exec_())