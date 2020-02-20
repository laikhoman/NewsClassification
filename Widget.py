from PyQt4 import QtGui, QtCore
from wordcloud import WordCloud
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np

from SystemMaterial import selectedFeatureMethod_Obj, SFMethod, BagOfWords_Obj, EvValue
from DatabaseManager import NewsDatabase
from Dialog import ProgressDialog, ParameterDialog, FilterDialog
from Thread import CasefoldingThrd, TokenizationThrd, RemoveStopwordThrd,\
    StemmingThrd, IGFindFeaturesThrd, ClasifyDataThrd, MMRFindFeatureThrd,\
    IGMMRFindFeatureThrd, GetProcessDetailThrd

class ProcessPage(QtGui.QWidget):
    def __init__(self, parent, selectedMethod_Prm):
        QtGui.QWidget.__init__(self)
        self.newsDatabase = NewsDatabase()
        
        self.databaseID = None 
        self.newsLst = None
        self.dataCorpus = []
        #self.processResLst = None
        self.EnableSave = False
        self.SelectedFeature = []
        self.SelectedFeatureCFSIdx = []
        
        #Input Variable
        self.selectedMethod = selectedMethod_Prm
        
        #Data Tabel
        self.showdataTbl = QtGui.QTableWidget(self)
        self.showdataTbl.cellClicked.connect(self.Refreshtabpage)
        #Page
        self.dataTblPageInt = QtGui.QSpinBox(self)
        self.dataTblPageInt.valueChanged.connect(self.ShowTablePage)
        
        #Text Preprocessing Label
        self.preprocessLbl = QtGui.QLabel("<h2>Text Preprocessing</h2>",self)
        self.preprocessLbl.hide()
        #Feature Selection
        self.featureselectionLbl = QtGui.QLabel("<h2>Feature Selection</h2>",self)
        self.featureselectionLbl.hide()
        #Page Label
        self.dataTblPageLbl = QtGui.QLabel("Page",self)
        #Casefolding Button
        self.casefoldingBtn = QtGui.QPushButton("Casefolding",self)
        self.casefoldingBtn.clicked.connect(self.casefoldingBtn_Clicked)
        self.casefoldingBtn.hide()
        #Tokenization Button
        self.tokenizationBtn = QtGui.QPushButton("Tokenization",self)
        self.tokenizationBtn.clicked.connect(self.tokenizationBtn_Clicked)
        self.tokenizationBtn.hide()
        #Stopword Removal Button
        self.removeStopwordBtn = QtGui.QPushButton("Remove Stopword",self)
        self.removeStopwordBtn.clicked.connect(self.removeStopwordBtn_Clicked)
        self.removeStopwordBtn.hide()
        #Stemming Button
        self.stemmingBtn = QtGui.QPushButton("Porter Stemming",self)
        self.stemmingBtn.clicked.connect(self.stemmingBtn_Clicked)
        self.stemmingBtn.hide()
        #Information Gain Feature Selection Button
        self.featureselectionBtn = QtGui.QPushButton(self.selectedMethod,self)
        self.featureselectionBtn.clicked.connect(self.FeatureSelectionBtn_Clicked)
        self.featureselectionBtn.hide()
        #Naive Bayes Deep Feature Weighting Button
        self.dfwnbBtn = QtGui.QPushButton("DFW-Naive Bayes",self)
        self.dfwnbBtn.clicked.connect(self.dfwBtn_Clicked)
        self.dfwnbBtn.hide()
        #Naive Bayes Button
        self.nbBtn = QtGui.QPushButton("Naive Bayes",self)
        self.nbBtn.clicked.connect(self.nbBtn_Clicked)
        self.nbBtn.hide()
        #Algorithm Tab Page
        self.detailTab = QtGui.QTabWidget(self)
        self.processdetailTab = QtGui.QWidget()
        
        self.wordclouddetailTab = QtGui.QWidget()
        self.WordcloudGrid = QtGui.QGridLayout(self.wordclouddetailTab)
        self.wordcloudfigure = Figure(facecolor="white")
        self.canvas = FigureCanvas(self.wordcloudfigure)
        self.WordcloudGrid.addWidget(self.canvas,0,0)
        
        self.processdetailGrid = QtGui.QGridLayout(self.processdetailTab)
        self.processdetailTxt = QtGui.QPlainTextEdit()
        self.processdetailTxt.setReadOnly(True)
        self.processdetailGrid.addWidget(self.processdetailTxt,0,0)
       
        self.detailTab.addTab(self.processdetailTab, "Detail View")
        self.detailTab.addTab(self.wordclouddetailTab, "Word Cloud View")
        
        Grid = QtGui.QGridLayout(self)
        Grid.setColumnStretch(2,5)
        Grid.setColumnStretch(1,1)
        Grid.setColumnStretch(0,1)
        Grid.setRowStretch(6,1)
        
        Grid.addWidget(self.preprocessLbl,0,0,1,2)
        Grid.addWidget(self.casefoldingBtn,1,0)
        Grid.addWidget(self.tokenizationBtn,1,1)
        Grid.addWidget(self.removeStopwordBtn,2,0)
        Grid.addWidget(self.stemmingBtn,2,1)
        Grid.addWidget(self.featureselectionLbl,3,0,1,2)
        Grid.addWidget(self.featureselectionBtn,4,0,1,2)
        Grid.addWidget(self.dfwnbBtn,5,0,1,2)
        Grid.addWidget(self.nbBtn,5,0,1,2)
        Grid.addWidget(self.detailTab,6,0,1,2)
        Grid.addWidget(self.showdataTbl,1,2,8,4)     
        Grid.addWidget(self.dataTblPageInt,0,4)
        Grid.addWidget(self.dataTblPageLbl,0,3)
        
    
    def ShowTablePage(self, PageInt_Prm):
        self.showdataTbl.setRowCount(0)
        headerlist = ["News ID", "Content", "Category","Case Folding", "Tokenization", "Stopword Removed", "stemmed", str(self.selectedMethod),"Fold","Predicted Category"]
        Horizontalheader = []
        
        maxRow = 200
        maxPage = (self.totalData-1)/200 + 1
        self.dataTblPageInt.setMaximum(maxPage)
        
        Table = NewsDatabase().database.getAllProcesss((PageInt_Prm-1)*maxRow, self.columnState, self.databaseID)
        if(self.columnState > 7):
            Table = NewsDatabase().database.getAllProcesss((PageInt_Prm-1)*maxRow, self.columnState, self.databaseID, self.selectedFeatureMethodID, self.selectedFeatureMethodValue)
        
        for i in range(0 , len(Table[0])):
            Horizontalheader.append(headerlist[i])
            
        self.showdataTbl.setRowCount(len(Table))
        self.showdataTbl.setColumnCount(len(Table[0]))
        
        self.showdataTbl.setHorizontalHeaderLabels([i for i in Horizontalheader])
        self.showdataTbl.setVerticalHeaderLabels(['' for i in range(self.showdataTbl.rowCount())])
        self.showdataTbl.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.showdataTbl.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        
        for i in range (0, len(Table) ):
            for j in range (0, self.showdataTbl.columnCount()):
                self.showdataTbl.setItem(i,j,QtGui.QTableWidgetItem(str(Table[i][j])))
        
    def RefreshTable(self, CurrentPage_Prm):
        self.ShowTablePage(CurrentPage_Prm.value())
        
        
        """for i in range(0 , columncountInt_Prm):
            Horizontalheader.append(headerlist[i])
            
        self.showdataTbl.setRowCount(len(Table))
        self.showdataTbl.setColumnCount(columncountInt_Prm)
        self.showdataTbl.setHorizontalHeaderLabels([i for i in Horizontalheader])
        self.showdataTbl.setVerticalHeaderLabels(['' for i in range(self.showdataTbl.rowCount())])
        self.showdataTbl.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.showdataTbl.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        
        for i in range (0, maxRow ):
            for j in range (0, self.showdataTbl.columnCount()):
                self.showdataTbl.setItem(i,j,QtGui.QTableWidgetItem(str(Table[i][j])))"""
    
    def Refreshtabpage(self, row, column):        
        stemcolumnIdxInt = 6
        self.__GenerateWordcloud(row, stemcolumnIdxInt)
        
        self.progressDialog = ProgressDialog()
        self.progressDialog.OpenProgressDialog("Get Detail . .")
        self.progressDialog.progressBar.setRange(0,0)
        
        self.newsLst = np.array(NewsDatabase().GetNews(self.databaseID))
        getProcessDetailThrd = GetProcessDetailThrd(row, self.showdataTbl, self.dataCorpus, self.selectedMethod, self.SelectedFeature)
        self.connect(getProcessDetailThrd, QtCore.SIGNAL("DONE(QString)"),self.GetProcessDetail)
        getProcessDetailThrd.start()
        
    def GetProcessDetail(self, result):
        self.processdetailTxt.setPlainText(result)
        self.progressDialog.close()
              
    def AsignDatabaseID(self, databaseID_Prm):
        self.progressDialog = ProgressDialog()
        self.progressDialog.OpenProgressDialog("Loading your file")
        
        self.databaseID = databaseID_Prm
        self.newsLst = np.array(NewsDatabase().GetNews(self.databaseID))
        #self.processResLst = np.array([])
        #self.processResLst = self.__AppendColumn(self.processResLst, self.newsLst[:,0])
        #self.processResLst = self.__AppendColumn(self.processResLst, self.newsLst[:,1])
        #self.processResLst = self.__AppendColumn(self.processResLst, self.newsLst[:,2])
        
        self.totalData = len(self.newsLst)
        self.columnState = 3
        
        self.progressDialog.close()
        
        self.dataTblPageInt.setValue(1)
        self.RefreshTable(self.dataTblPageInt)
        self.preprocessLbl.show()
        self.casefoldingBtn.show() 
        
    
    def casefoldingBtn_Clicked(self):
        self.progressDialog = ProgressDialog()
        self.progressDialog.OpenProgressDialog("Casefolding !!")
        
        if("" in self.newsLst[:,3]): #Access Casefolding            
            threadProcess = CasefoldingThrd(self.newsLst)
            self.connect(threadProcess, QtCore.SIGNAL("Done(QStringList)"), self.__AsignCasefolding, QtCore.Qt.QueuedConnection)
            self.connect(threadProcess, QtCore.SIGNAL("SetProgressBar(int)"), self.__SetProgressBar, QtCore.Qt.QueuedConnection)
            threadProcess.start()
            
        else:
            #self.processResLst = self.__AppendColumn(self.processResLst, self.newsLst[:,3])
            self.columnState = 4
            self.progressDialog.close()
            
            self.RefreshTable(self.dataTblPageInt)
                
        self.tokenizationBtn.show()
        self.casefoldingBtn.setDisabled(True)
    
    def tokenizationBtn_Clicked(self):
        self.progressDialog = ProgressDialog()
        self.progressDialog.OpenProgressDialog("Tokenization !!")
        
        if("" in self.newsLst[:,4]): #Access Tokenization        
            self.newsLst = np.array(NewsDatabase().GetNews(self.databaseID))
            threadProcess = TokenizationThrd(self.newsLst)
            self.connect(threadProcess, QtCore.SIGNAL("Done(QStringList)"), self.__AsignTokenization, QtCore.Qt.QueuedConnection)
            self.connect(threadProcess, QtCore.SIGNAL("SetProgressBar(int)"), self.__SetProgressBar, QtCore.Qt.QueuedConnection)
            threadProcess.start()
            
        else:
            #self.processResLst = self.__AppendColumn(self.processResLst, self.newsLst[:,4])
            self.columnState = 5
            self.progressDialog.close()
            
            self.RefreshTable(self.dataTblPageInt)
                    
            self.removeStopwordBtn.show()
            self.tokenizationBtn.setDisabled(True)
        
    def removeStopwordBtn_Clicked(self):
        self.progressDialog = ProgressDialog()
        self.progressDialog.OpenProgressDialog("Remove Stopword !!")
        
        if("" in self.newsLst[:,5]): #Access Stopword Removed    
            self.newsLst = np.array(NewsDatabase().GetNews(self.databaseID))    
            threadProcess = RemoveStopwordThrd(self.newsLst)
            self.connect(threadProcess, QtCore.SIGNAL("Done(QStringList)"), self.__AsignRemoveStopword, QtCore.Qt.QueuedConnection)
            self.connect(threadProcess, QtCore.SIGNAL("SetProgressBar(int)"), self.__SetProgressBar, QtCore.Qt.QueuedConnection)
            threadProcess.start()
            
        else:
            #self.processResLst = self.__AppendColumn(self.processResLst, self.newsLst[:,5])
            self.columnState = 6
            self.progressDialog.close()
            
            self.RefreshTable(self.dataTblPageInt)
                
        self.stemmingBtn.show()
        self.removeStopwordBtn.setDisabled(True)
        
    def stemmingBtn_Clicked(self):
        self.progressDialog = ProgressDialog()
        self.progressDialog.OpenProgressDialog("Stemming !!")
        
        if("" in self.newsLst[:,6]): #Access Stemmed        
            self.newsLst = np.array(NewsDatabase().GetNews(self.databaseID))
            threadProcess = StemmingThrd(self.newsLst)
            self.connect(threadProcess, QtCore.SIGNAL("Done(QStringList)"), self.__AsignStemming, QtCore.Qt.QueuedConnection)
            self.connect(threadProcess, QtCore.SIGNAL("SetProgressBar(int)"), self.__SetProgressBar, QtCore.Qt.QueuedConnection)
            threadProcess.start()
            
        else:
            #self.processResLst = self.__AppendColumn(self.processResLst, self.newsLst[:,6])
            self.columnState = 7
            
            self.dataIDLst = np.array(NewsDatabase().database.GetTableData("newsarticle", ["NewsID"], ["dataset_id"], [self.databaseID]))[:,0]
            self.dataCorpus = np.array(NewsDatabase().database.GetTableData("newsarticle", ["article_stemmed"], ["dataset_id"], [self.databaseID]))[:,0]
            self.dataCategoryLst = np.array(NewsDatabase().database.GetTableData("newsarticle", ["article_category"], ["dataset_ID"], [self.databaseID]))[:,0]
            self.BOW = BagOfWords_Obj(self.dataCorpus, 1000)
            
            self.progressDialog.close()
            
            self.RefreshTable(self.dataTblPageInt)
                
            self.featureselectionLbl.show()
            self.featureselectionBtn.show()
            self.stemmingBtn.setDisabled(True)
        
    def FeatureSelectionBtn_Clicked(self):                
        if(self.selectedMethod == SFMethod.Information_Gain_Feature_Selection.name):
            self.parameterDialog = ParameterDialog(self,SFMethod.Information_Gain_Feature_Selection.value, len(self.BOW.uniqueFeatureLst))
        elif(self.selectedMethod == SFMethod.Maximal_Marginal_Relevance_Feature_Selection.name):
            self.parameterDialog = ParameterDialog(self, SFMethod.Maximal_Marginal_Relevance_Feature_Selection.value, len(self.BOW.uniqueFeatureLst))
        elif(self.selectedMethod == SFMethod.Information_Gain_Maximal_Marginal_Relevance_Feature_Selection.name):
            self.parameterDialog = ParameterDialog(self, SFMethod.Information_Gain_Maximal_Marginal_Relevance_Feature_Selection.value, len(self.BOW.uniqueFeatureLst))
        
        self.parameterDialog.show()
        self.connect(self.parameterDialog, QtCore.SIGNAL("DONE(QString, QString, QString, QString)"), self.__AsignFeatureSelectionMethod)
        
    def __AsignFeatureSelectionMethod(self, igThreshold, mmrThreshold, mmrLambda, dfwState):
        self.parameterDialog.close()
        mmrLambda = float(mmrLambda)
        
        try : igThreshold = int(igThreshold)
        except ValueError: igThreshold = 0
        try : mmrThreshold = int(mmrThreshold)
        except ValueError: mmrThreshold = 0
        
        if(dfwState == "True"):
            dfwState = 1
        else:
            dfwState = 0

        if(self.selectedMethod == SFMethod.Information_Gain_Feature_Selection.name):
            self.selectedFeatureMethodValue = SFMethod.Information_Gain_Feature_Selection.value
            self.selectedFeatureMethod = selectedFeatureMethod_Obj(SFMethod.Information_Gain_Feature_Selection.name, igThreshold, mmrThreshold, mmrLambda, dfwState)
            self.selectedFeatureMethodID = self.__saveDatabaseMethodID(self.selectedFeatureMethod)
            self.__InfoGain()
        elif(self.selectedMethod == SFMethod.Maximal_Marginal_Relevance_Feature_Selection.name):
            self.selectedFeatureMethodValue = SFMethod.Maximal_Marginal_Relevance_Feature_Selection.value
            self.selectedFeatureMethod = selectedFeatureMethod_Obj(SFMethod.Maximal_Marginal_Relevance_Feature_Selection.name, igThreshold, mmrThreshold, mmrLambda, dfwState)
            self.selectedFeatureMethodID = self.__saveDatabaseMethodID(self.selectedFeatureMethod)
            self.__MMRFs()
        elif(self.selectedMethod == SFMethod.Information_Gain_Maximal_Marginal_Relevance_Feature_Selection.name):
            self.selectedFeatureMethodValue = SFMethod.Information_Gain_Maximal_Marginal_Relevance_Feature_Selection.value
            self.selectedFeatureMethod = selectedFeatureMethod_Obj(SFMethod.Information_Gain_Maximal_Marginal_Relevance_Feature_Selection.name, igThreshold, mmrThreshold, mmrLambda, dfwState)
            self.selectedFeatureMethodID = self.__saveDatabaseMethodID(self.selectedFeatureMethod)
            self.__InfoGainMMRFs()
            
        
    def nbBtn_Clicked(self):
        self.progressDialog = ProgressDialog()
        self.progressDialog.OpenProgressDialog("Clasifying Data : Validate CV k-fold")
        
        clasifyDataThrd = ClasifyDataThrd(self.databaseID, self.selectedFeatureMethodID, self.SelectedFeature, self.dataCorpus, self.dataIDLst, self.dataCategoryLst)
        self.connect(clasifyDataThrd, QtCore.SIGNAL("SetProgressBar(int)"),self.__SetProgressBar)
        self.connect(clasifyDataThrd, QtCore.SIGNAL("DONE(QStringList, QStringList)"), self.__AsignNBClasify)
        self.connect(clasifyDataThrd, QtCore.SIGNAL("GetEvaluation(QStringList, QStringList, QStringList, QStringList)"), self.__AsignEvaluation)
        clasifyDataThrd.start()
        
    def dfwBtn_Clicked(self):
        self.progressDialog = ProgressDialog()
        self.progressDialog.OpenProgressDialog("Clasifying Data : Validate CV k-fold")
        
        clasifyDataThrd = ClasifyDataThrd(self.databaseID, self.selectedFeatureMethodID, self.SelectedFeature, self.dataCorpus, self.dataIDLst, self.dataCategoryLst, self.SelectedFeatureCFSIdx)
        self.connect(clasifyDataThrd, QtCore.SIGNAL("SetProgressBar(int)"),self.__SetProgressBar)
        self.connect(clasifyDataThrd, QtCore.SIGNAL("DONE(QStringList, QStringList)"), self.__AsignNBClasify)
        self.connect(clasifyDataThrd, QtCore.SIGNAL("GetEvaluation(QStringList, QStringList, QStringList, QStringList)"), self.__AsignEvaluation)
        clasifyDataThrd.start()
        
    def __GenerateWordcloud(self, row, column):
        if(self.showdataTbl.columnCount() > 6):    
            self.wordcloudtext = self.showdataTbl.item(row, column).text()
            wc = WordCloud(width=350,height=350, stopwords="", background_color="white").generate(self.wordcloudtext)
            self.wordcloudfigure.figimage(wc.to_array())
            
            self.canvas.draw()
    
    def __saveDatabaseMethodID(self, selectedFeatureMethodObj_Prm):
        Result = 0
        selectedFeatureMethod = selectedFeatureMethodObj_Prm
        tableData = self.newsDatabase.database.GetTableData("methodfeatureselection", ["SF_ID"], ["SF_name","num_ig_feature","num_mmr_feature","FORMAT(mmr_lambda,2)","Is_DFW"], [selectedFeatureMethod.Name, selectedFeatureMethod.IGThreshold, selectedFeatureMethod.MMRThreshold,str("\"+{0}+\"").format(selectedFeatureMethod.MMRLambda),selectedFeatureMethod.IsDFW])
        
        if(tableData != ()):
            Result = tableData[0][0]
        else:
            Result = self.newsDatabase.database.importMethod(selectedFeatureMethod.Name, selectedFeatureMethod.IGThreshold, selectedFeatureMethod.MMRThreshold, selectedFeatureMethod.MMRLambda, selectedFeatureMethod.IsDFW)
        
        return Result
    
    def __AsignCasefolding(self, result):
        #self.processResLst = self.__AppendColumn(self.processResLst, result)
        self.columnState = 4
        self.progressDialog.close()
        
        self.RefreshTable(self.dataTblPageInt)
    
    def __AsignTokenization(self, result):
        #self.processResLst = self.__AppendColumn(self.processResLst, result)
        self.columnState = 5
        self.progressDialog.close()
        
        self.RefreshTable(self.dataTblPageInt)
        
        self.removeStopwordBtn.show()
        self.tokenizationBtn.setDisabled(True)
        
    def __AsignRemoveStopword(self, result):
        #self.processResLst = self.__AppendColumn(self.processResLst, result)
        self.columnState = 6
        self.progressDialog.close()
        
        self.RefreshTable(self.dataTblPageInt)
        
    def __AsignStemming(self, result):
        #self.processResLst = self.__AppendColumn(self.processResLst, result)
        self.columnState = 7
        
        self.dataIDLst = np.array(NewsDatabase().database.GetTableData("newsarticle", ["NewsID"], ["dataset_id"], [self.databaseID]))[:,0]
        self.dataCorpus = np.array(NewsDatabase().database.GetTableData("newsarticle", ["article_stemmed"], ["dataset_id"], [self.databaseID]))[:,0]
        self.dataCategoryLst = np.array(NewsDatabase().database.GetTableData("newsarticle", ["article_category"], ["dataset_ID"], [self.databaseID]))[:,0]
        self.BOW = BagOfWords_Obj(self.dataCorpus, 1000)
        
        self.progressDialog.close()
        
        NewsDatabase().database.UpdateTable("Dataset", "Is_Preprocessed", "1", "Dataset_ID", self.databaseID)
        self.RefreshTable(self.dataTblPageInt)
        
        self.featureselectionLbl.show()
        self.featureselectionBtn.show()
        self.stemmingBtn.setDisabled(True)
        
    def __InfoGain(self):
        self.progressDialog = ProgressDialog()
        self.progressDialog.OpenProgressDialog("Selecting Feature !!")
        self.progressDialog.progressBar.setRange(0,0)
        
        igFindFeaturesThrd = IGFindFeaturesThrd(self.selectedFeatureMethod.IGThreshold, self.dataCorpus, self.databaseID, self.selectedFeatureMethodID, self.dataIDLst)
        self.connect(igFindFeaturesThrd, QtCore.SIGNAL("DONE(QStringList, QStringList)"),self.__AsignSelectedFeature)
        igFindFeaturesThrd.start()
        
    def __MMRFs(self):
        self.progressDialog = ProgressDialog()
        self.progressDialog.OpenProgressDialog("Selecting Feature !!")
        self.progressDialog.progressBar.setRange(0,0)
        
        
        mmrFindFeature = MMRFindFeatureThrd(self.selectedFeatureMethod.MMRThreshold, self.selectedFeatureMethod.MMRLambda, self.databaseID, self.selectedFeatureMethodID, self.dataCorpus, self.dataIDLst, self.dataCategoryLst)
        self.connect(mmrFindFeature, QtCore.SIGNAL("DONE(QStringList, QStringList)"), self.__AsignSelectedFeature)
        mmrFindFeature.start()
        
    def __InfoGainMMRFs(self):
        self.progressDialog = ProgressDialog()
        self.progressDialog.OpenProgressDialog("Selecting Feature !!")
        self.progressDialog.progressBar.setRange(0,0)
        
        self.dataCategoryLst = np.array(NewsDatabase().database.GetTableData("newsarticle", ["article_category"], ["dataset_ID"], [self.databaseID]))[:,0]
        
        igmmrFindFeature = IGMMRFindFeatureThrd(self.selectedFeatureMethod.IGThreshold, self.selectedFeatureMethod.MMRThreshold, self.selectedFeatureMethod.MMRLambda, self.selectedFeatureMethod.IsDFW, self.databaseID, self.selectedFeatureMethodID, self.dataCorpus, self.dataIDLst, self.dataCategoryLst)
        self.connect(igmmrFindFeature, QtCore.SIGNAL("DONE(QStringList, QStringList)"), self.__AsignSelectedFeature, QtCore.Qt.QueuedConnection)
        self.connect(igmmrFindFeature, QtCore.SIGNAL("DONE(QStringList, QStringList, QStringList)"), self.__AsignSelectedFeatureDFW, QtCore.Qt.QueuedConnection)
        igmmrFindFeature.start()
    
    def __AsignSelectedFeature(self, bowresult, result):
        
        self.SelectedFeature = result
        #self.processResLst = self.__AppendColumn(self.processResLst, bowresult)
        if(self.selectedMethod == SFMethod.Information_Gain_Feature_Selection.name):
            tmp = 1
        else:
            tmp = 2
        self.columnState = 8
        self.progressDialog.close()
        
        self.RefreshTable(self.dataTblPageInt)
        
        self.nbBtn.show()
        self.featureselectionBtn.setDisabled(True)
        
    def __AsignSelectedFeatureDFW(self, bowresult, result, selectedCFS):
        self.SelectedFeature = result
        self.SelectedFeatureCFSIdx = selectedCFS
        #self.processResLst = self.__AppendColumn(self.processResLst, bowresult)
        self.columnState = 8
        self.progressDialog.close()
        
        self.RefreshTable(self.dataTblPageInt)
        
        self.dfwnbBtn.show()
        self.featureselectionBtn.setDisabled(True)
        
    def __AsignNBClasify(self, result, result2):
        #self.processResLst = self.__AppendColumn(self.processResLst, result)
        #self.processResLst = self.__AppendColumn(self.processResLst, result2)
        if(self.selectedMethod == SFMethod.Information_Gain_Feature_Selection.name):
            tmp = 1
        else:
            tmp = 2
        self.columnState = 10
        
        self.foldArr = result
        
        self.progressDialog.close()
        
        self.RefreshTable(self.dataTblPageInt)
        
        self.nbBtn.setDisabled(True)
        self.dfwnbBtn.setDisabled(True)
        self.EnableSave = True
        
    def __AsignEvaluation(self, resultacc, resultpre, resultrec, resultf1):
        self.accArr = [float(i) for i in resultacc]
        #print(self.accArr)
        self.preArr = [float(i) for i in resultpre]
        #print(self.preArr)
        self.recArr = [float(i) for i in resultrec]
        #print(self.recArr)
        self.f1Arr = [float(i) for i in resultf1]
        #print(self.f1Arr)
    
    def __AppendColumn(self, arr1, arr2):
        arr1 = np.array(arr1)
        arr2 = np.array([arr2]).T
        res = []
        try:
            res = np.hstack((arr1,arr2))
        except ValueError:
            res = arr2    
        return res
    
    def __SetProgressBar(self, value):
        self.progressDialog.progressBar.setRange(0,100)
        self.progressDialog.progressBar.setValue(value)

class ViewResult(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
                
        self.filterDialog = FilterDialog(self)
        self.connect(self.filterDialog, QtCore.SIGNAL("DONE(QString)"),self.__AsignDatabaseID)
        self.filterDialog.show()
        
        self.ListDataResultLbl = QtGui.QLabel("List Data Result")
        
        self.ListDataResultLstVw = QtGui.QListWidget()
        self.ListDataResultLstVw.setSelectionMode(QtGui.QListWidget.MultiSelection)
        self.ListDataResultLstVw.itemClicked.connect(self.__ListDataResultLstVw_Clicked)
        
        self.TabPage = QtGui.QTabWidget()
        self.TableView = QtGui.QWidget()
        self.GraphView = QtGui.QWidget()
        
        TableGrid = QtGui.QGridLayout(self.TableView)
        self.showdataTbl = QtGui.QTableWidget()
        self.showdataTbl.hide()
        self.showdataTbl2 = QtGui.QTableWidget()
        self.showdataTbl2.hide()
        self.showdataTbl3 = QtGui.QTableWidget()
        self.showdataTbl3.hide()
        self.showdataTbl4 = QtGui.QTableWidget()
        self.showdataTbl4.hide()
        
        TableGrid.addWidget(self.showdataTbl,0,0)
        TableGrid.addWidget(self.showdataTbl2,0,1)
        TableGrid.addWidget(self.showdataTbl3,0,2)
        TableGrid.addWidget(self.showdataTbl4,0,3)
        self.TableView.setLayout(TableGrid)
        
        GraphGrid = QtGui.QGridLayout()
        GraphGrid.setRowStretch(4,1)
        GraphGrid.setColumnStretch(1,1)
        EvValueLbl = QtGui.QLabel("Choose Y Parameter")
        EvValueBtn = QtGui.QPushButton("Load")
        EvValueBtn.clicked.connect(self.EvValueBtn_Clicked)
        
        self.GraphNextBtn = QtGui.QPushButton("Next")
        self.GraphNextBtn.clicked.connect(self.GraphNextBtn_Clicked)
        self.IsNext = False
        self.GraphFullView = QtGui.QPushButton("Back Full View")
        self.GraphFullView.clicked.connect(self.EvValueBtn_Clicked)
        self.GraphFullView.hide()
        
        self.EvValueCbx = QtGui.QComboBox()
        self.EvValueCbx.addItem(EvValue.Accuracy.name)
        self.EvValueCbx.addItem(EvValue.Presision.name)
        self.EvValueCbx.addItem(EvValue.Recall.name)
        self.EvValueCbx.addItem(EvValue.Fmeasure.name)
        
        GraphGrid.addWidget(EvValueLbl,0,0)
        GraphGrid.addWidget(self.EvValueCbx,1,0)
        GraphGrid.addWidget(EvValueBtn,2,0)
        GraphGrid.addWidget(self.GraphNextBtn,5,1)
        GraphGrid.addWidget(self.GraphFullView,5,2)
        
        self.graphFig = Figure(facecolor="Gray")
        self.graphFig.subplots_adjust(left=0.2, right=0.9, bottom=0.08, top=0.95,wspace=1,hspace=0.5)
        self.canvas = FigureCanvas(self.graphFig)
        MyToolbar = NavigationToolbar(self.canvas,self.GraphView)
        self.canvas.mpl_connect("button_press_event", self.onclick_selectSubPlot)
        GraphGrid.addWidget(MyToolbar,0,1)
        GraphGrid.addWidget(self.canvas,1,1,4,2)
        self.GraphView.setLayout(GraphGrid)
        
        self.TabPage.addTab(self.TableView, "Evaluation Table")
        self.TabPage.addTab(self.GraphView, "Evaluation Graph")
        
        Grid = QtGui.QGridLayout(self)
        Grid.setColumnStretch(1,1)
        
        Grid.addWidget(self.ListDataResultLbl,0,0)
        Grid.addWidget(self.ListDataResultLstVw,1,0,1,2)
        Grid.addWidget(self.TabPage,2,0,1,2)
        
    def __AsignDatabaseID(self, databaseIDPrm):
        self.datasetID = databaseIDPrm
        self.EvaluationData = NewsDatabase().database.getAllEvaluation(self.datasetID)
        self.ResultData = NewsDatabase().database.getAllDataresult(self.datasetID)
        
        for i in self.EvaluationData:
            Evaluation = QtGui.QListWidgetItem()
            Evaluation.setText(i[1])
            Evaluation.setData(QtCore.Qt.UserRole+1,i[0])
            
            self.ListDataResultLstVw.addItem(Evaluation)        
    
    def __ListDataResultLstVw_Clicked(self):          
        selectedList = self.ListDataResultLstVw.selectedItems()
        selectedEvaluationID = [i.data(QtCore.Qt.UserRole+1) for i in selectedList]
        
        self.showdataTbl.hide()
        self.showdataTbl2.hide()
        self.showdataTbl3.hide()
        self.showdataTbl4.hide()
        
        dataLstIG = []
        dataLstMMR = []
        dataLstIGMMR = []
        dataLstIGMMRDFW = []
        
        for i in self.ResultData:
            if(i[0] == SFMethod.Information_Gain_Feature_Selection.name and i[1] in selectedEvaluationID):
                dataLstIG.append(i)
            if(i[0] == SFMethod.Maximal_Marginal_Relevance_Feature_Selection.name and i[1] in selectedEvaluationID):
                dataLstMMR.append(i)
            if(i[0] == SFMethod.Information_Gain_Maximal_Marginal_Relevance_Feature_Selection.name and int(i[7]) == 0 and i[1] in selectedEvaluationID):
                dataLstIGMMR.append(i)
            if(i[0] == SFMethod.Information_Gain_Maximal_Marginal_Relevance_Feature_Selection.name and int(i[7]) == 1 and i[1] in selectedEvaluationID):
                dataLstIGMMRDFW.append(i)

        if(dataLstIG != []):                
            self.__refreshTable(self.showdataTbl,dataLstIG)
        if(dataLstMMR != []):
            self.__refreshTable(self.showdataTbl2,dataLstMMR)
        if(dataLstIGMMR != []):
            self.__refreshTable(self.showdataTbl3,dataLstIGMMR)
        if(dataLstIGMMRDFW != []):
            self.__refreshTable(self.showdataTbl4,dataLstIGMMRDFW)
        
        self.__redrawCanvas(self.EvValueCbx.currentText(),selectedEvaluationID)
    
    def __refreshTable(self, dataTable, dataLst):
        dataTable.clearContents()
        headerlist = ["Evaluation ID","Method ID","Fold","Num. Feature IG","Num. Feature MMR","MMR Lambda","DFW","Accuracy_Mean","Presision_Mean","Recall_Mean","Fmeasure_Mean"]
        Table = dataLst
        
        dataTable.setRowCount(len(Table))
        dataTable.setColumnCount(len(headerlist))
        dataTable.setHorizontalHeaderLabels(headerlist)
        dataTable.setVerticalHeaderLabels(['' for i in range(dataTable.rowCount())])
        dataTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        dataTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        
        for i in range(dataTable.rowCount()):
            for j in range(dataTable.columnCount()):
                dataTable.setItem(i,j,QtGui.QTableWidgetItem(str(Table[i][j+1])))
        dataTable.show()
        
    
    def onclick_selectSubPlot(self,event):
        if(self.GraphFullView.isHidden()):            
            findaxIdx = [i for i in range(len(self.ax)) if self.ax[i] == event.inaxes]
            try:
                self.selectedIdx = findaxIdx[0]
            except IndexError:
                pass
            if(self.IsNext and self.selectedIdx == 5): pass
            else:
                if(self.IsNext): self.selectedIdx += 6
                
                self.graphFig.clf()
                selectedList = self.ListDataResultLstVw.selectedItems()
                selectedEvaluationID = [i.data(QtCore.Qt.UserRole+1) for i in selectedList]
                axLegend =  self.__drawPlot(1, 1, self.selectedIdx, self.EvValueCbx.currentText(), selectedEvaluationID)
                
                self.graphFig.tight_layout()
                self.canvas.draw_idle()
                self.GraphFullView.show()
        
                
    def EvValueBtn_Clicked(self):
        self.GraphFullView.hide()
        
        selectedList = self.ListDataResultLstVw.selectedItems()
        selectedEvaluationID = [i.data(QtCore.Qt.UserRole+1) for i in selectedList]
        selectedEvValue = self.EvValueCbx.currentText()
            
        self.__redrawCanvas(selectedEvValue, selectedEvaluationID)
        
                
    def GraphNextBtn_Clicked(self):
        if(self.IsNext == True):
            self.IsNext = False
            self.GraphNextBtn.setText("Next")
        elif(self.IsNext == False):
            self.IsNext = True
            self.GraphNextBtn.setText("Back")
        self.EvValueBtn_Clicked()
    
    def __redrawCanvas(self, EvValue_Prm, EvaluationIDLst_Prm):
        self.graphFig.clf()
        self.ax = []
        row = 3
        column = 2
        for i in range(12):
            if(i>10 and self.IsNext):
                self.ax.append(self.__showGraphLegend(row,column,6))
            elif(i > 5 and self.IsNext):
                self.ax.append(self.__drawPlot(row, column, i, EvValue_Prm, EvaluationIDLst_Prm))
            elif(i <= 5 and not self.IsNext):
                self.ax.append(self.__drawPlot(row, column, i, EvValue_Prm, EvaluationIDLst_Prm))
            
            self.graphFig.tight_layout()
            self.canvas.draw_idle()
            
    
    def __drawPlot(self, rowPrm, columnPrm, plotIdx, EvValue_Prm, EvaluationIDLst_Prm):
        Idx = "{0}{1}".format(rowPrm,columnPrm)
        if(Idx == "11"):
            Idx = "111"
        elif(self.IsNext):
            Idx += "{0}".format(plotIdx-5)
        else:
            Idx += "{0}".format(plotIdx+1)
        
        result = self.graphFig.add_subplot(int(Idx))
        result.set_xlabel('number of features')
        result.set_ylabel(EvValue_Prm)
        result.set_title("{0}".format(plotIdx/10))
        
        Lambda = float(plotIdx/10)
        XParameter = self.__getXParameter(Lambda, EvaluationIDLst_Prm)
        YParameter = self.__getYParameter(Lambda, EvValue_Prm, EvaluationIDLst_Prm)
        
        maxX = 0
        minX = 99999999
        maxY = 0
        minY = 99999999
        
        for i in range(len(XParameter)):
            
            tmp1 = XParameter[i]
            tmp2 = YParameter[i]
            if(tmp1 != []):
                maxX_tmp = max(XParameter[i][j] for j in range(len(XParameter[i])))
                minX_tmp = min(XParameter[i][j] for j in range(len(XParameter[i])))
                minY_tmp = min(YParameter[i][j] for j in range(len(YParameter[i])))
                maxY_tmp = max(YParameter[i][j] for j in range(len(YParameter[i])))
                
                XParameter[i], YParameter[i] = (list(j) for j in zip(*sorted(zip(tmp1, tmp2))))
            
                maxX = max(maxX, maxX_tmp)
                minX = min(minX, minX_tmp)
                minY = min(minY, minY_tmp)
                maxY = max(maxY, maxY_tmp)
        
        result.plot(XParameter[0],YParameter[0],'r.-',label="IG + MNB", linewidth=0.4)
        result.plot(XParameter[1],YParameter[1],'g.-',label="MMR-FS + MNB", linewidth=0.4)
        result.plot(XParameter[2],YParameter[2],'b.-',label="IG-MMR-FS + MNB", linewidth=0.4)
        result.plot(XParameter[3],YParameter[3],'k.-',label="IG-MMR-FS + CFS + DFWMNB", linewidth=0.4)
        
        
        result.set_xlim(minX * 0.5,maxX * 1.1)
        result.set_ylim(minY * 0.5,maxY * 1.1)
            
        return result
    
    def __showGraphLegend(self, rowPrm, columnPrm, pltIdx):
        idx = "{0}{1}".format(rowPrm,columnPrm)
        idx += "{0}".format(pltIdx)
        result = self.graphFig.add_subplot(int(idx),frameon=False)
        
        result.plot([],[],'r.-',label="IG + MNB")
        result.plot([],[],'g.-',label="MMR-FS + MNB")
        result.plot([],[],'b.-',label="IG-MMR-FS + MNB")
        result.plot([],[],'k.-',label="IG-MMR-FS + CFS + DFWMNB")
        
        result.set_xticks([])
        result.set_yticks([])
        result.set_facecolor("Gray")
        result.legend()
        
        return result
            
    def __getYParameter(self, Lambda_Prm, EvValue_Prm, EvaluationIDLst_Prm):
        resultIGY = []
        resultMMRY = []
        resultIGMMRY = []
        resultIGMMRDFWY = []
        
        CurrentEvValue = EvValue.getValue(EvValue_Prm)
        
        for i in range(len(self.EvaluationData)):
            if(self.EvaluationData[i][0] in EvaluationIDLst_Prm):
                if(int(self.EvaluationData[i][9]) == 1 and float(self.EvaluationData[i][8]) == Lambda_Prm):
                    resultIGMMRDFWY.append(self.EvaluationData[i][CurrentEvValue+1])
                if(int(self.EvaluationData[i][6]) != 0 and int(self.EvaluationData[i][7]) != 0 and float(self.EvaluationData[i][8]) == Lambda_Prm and int(self.EvaluationData[i][9]) == 0):
                    resultIGMMRY.append(self.EvaluationData[i][CurrentEvValue+1])
                if(int(self.EvaluationData[i][6]) == 0 and int(self.EvaluationData[i][7]) != 0 and float(self.EvaluationData[i][8]) == Lambda_Prm):
                    resultMMRY.append(self.EvaluationData[i][CurrentEvValue+1])
                if(int(self.EvaluationData[i][6]) != 0 and int(self.EvaluationData[i][7]) == 0):
                    resultIGY.append(self.EvaluationData[i][CurrentEvValue+1])
                    
        result = []
        result.append(resultIGY)
        result.append(resultMMRY)
        result.append(resultIGMMRY)
        result.append(resultIGMMRDFWY)
        
        return result
    
    def __getXParameter(self, Lambda_Prm, EvaluationIDLst_Prm):
        resultIGX = []
        resultMMRX = []
        resultIGMMRX = []
        resultIGMMRDFWX = []
        
        for i in range(len(self.EvaluationData)):
            if(self.EvaluationData[i][0] in EvaluationIDLst_Prm):
                if(int(self.EvaluationData[i][9]) == 1 and float(self.EvaluationData[i][8]) == Lambda_Prm):
                    resultIGMMRDFWX.append(self.EvaluationData[i][7])
                if(int(self.EvaluationData[i][6]) > 0 and int(self.EvaluationData[i][7]) > 0 and float(self.EvaluationData[i][8]) == Lambda_Prm and int(self.EvaluationData[i][9]) == 0):
                    resultIGMMRX.append(self.EvaluationData[i][7])
                if(int(self.EvaluationData[i][6]) == 0 and int(self.EvaluationData[i][7]) > 0 and float(self.EvaluationData[i][8]) == Lambda_Prm):
                    resultMMRX.append(self.EvaluationData[i][7])
                if(int(self.EvaluationData[i][6]) > 0 and int(self.EvaluationData[i][7]) == 0):
                    resultIGX.append(self.EvaluationData[i][6])
        result = []
        result.append(resultIGX)
        result.append(resultMMRX)
        result.append(resultIGMMRX)
        result.append(resultIGMMRDFWX)
        
        return result
          
    