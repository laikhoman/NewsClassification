from PyQt4 import QtGui, QtCore
import numpy as np

from DatabaseManager import NewsDatabase
from SystemMaterial import BusyProgressBar

class OpenDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self,parent)
        
        width = QtGui.QDesktopWidget().screenGeometry().width()
        height = QtGui.QDesktopWidget().screenGeometry().height()
        framewidth = width*0.2
        frameheight = height*0.5
        
        self.setWindowTitle("Open Dialog")
        self.setGeometry(QtCore.QRect(width/2 - framewidth/2 , height/2 - frameheight/2, framewidth, frameheight))
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        #Input Variable
        self.datasetLst = np.array(NewsDatabase().GetDataset())
        #Result Variable
        self.resultIDSelected = ""
        
        #Select Label
        self.openLbl = QtGui.QLabel("<h3>Open File</h3>",self)
        #Dataset Table
        self.datasetTbl = QtGui.QTableWidget(self)
        self.RefreshImportTable(self.datasetLst)
        #Open Button
        self.okBtn = QtGui.QPushButton("Ok",self)
        self.okBtn.clicked.connect(self.okBtn_Clicked)
        #import Button
        self.addBtn = QtGui.QPushButton("Add",self)
        self.addBtn.clicked.connect(self.addBtn_Clicked)
        #Delete Button
        self.deleteBtn = QtGui.QPushButton("Delete",self)
        self.deleteBtn.clicked.connect(self.deleteBtn_Clicked)
        
        
        Grid = QtGui.QGridLayout(self)
        
        Grid.addWidget(self.openLbl,0,0,1,3)
        Grid.addWidget(self.datasetTbl,1,0,1,3)
        Grid.addWidget(self.deleteBtn,2,0,1,1)
        Grid.addWidget(self.addBtn,2,1,1,1)
        Grid.addWidget(self.okBtn,2,2,1,1)
        
    def RefreshImportTable(self, datasetLst_Prm):
        Datalist = datasetLst_Prm
        
        self.datasetTbl.setRowCount(len(Datalist))
        self.datasetTbl.setColumnCount(1)
        self.datasetTbl.setHorizontalHeaderLabels(["File Name"])
        self.datasetTbl.setVerticalHeaderLabels(['' for i in range(self.datasetTbl.rowCount())])
        self.datasetTbl.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.datasetTbl.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        
        for i in range ( 0, self.datasetTbl.rowCount() ):
            self.datasetTbl.setItem(i,0,QtGui.QTableWidgetItem(str(Datalist[i][1])))
         
    def okBtn_Clicked(self):
        index = self.datasetTbl.currentRow()
        self.resultIDSelected = int(self.datasetLst[index][0])
        
        self.close()
        self.emit(QtCore.SIGNAL("AsignDatabaseID(int)"),self.resultIDSelected)

        
    def deleteBtn_Clicked(self):
        index = self.datasetTbl.currentRow()
        NewsDatabase().SoftDelete(self.datasetLst[index][0])
        
        self.datasetLst = np.array(NewsDatabase().GetDataset())
        self.RefreshImportTable(self.datasetLst)
        
    def addBtn_Clicked(self):
        filelocation = self.__OpenFileDialog()
        
        try:
            if(filelocation not in self.datasetLst[:,2]):
                NewsDatabase().ImportNews(filelocation)
        except IndexError:
            NewsDatabase().ImportNews(filelocation)
            
        self.datasetLst = np.array(NewsDatabase().GetDataset())
        self.RefreshImportTable(self.datasetLst)
    
    def __OpenFileDialog(self):
        dlg = QtGui.QFileDialog()
        dlg.setFileMode(QtGui.QFileDialog.AnyFile)
        dlg.setFilter("CSV files (*.csv)")
        filenames = QtGui.QStringListModel()
        
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            
            return filenames[0]
                
            
class FilterDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        
        width = QtGui.QDesktopWidget().screenGeometry().width()
        height = QtGui.QDesktopWidget().screenGeometry().height()
        framewidth = width*0.2
        frameheight = height*0.5
        
        self.setWindowTitle("Filter Dialog")
        self.setGeometry(QtCore.QRect(width/2 - framewidth/2 , height/2 - frameheight/2, framewidth, frameheight))
        self.setWindowFlags(QtCore.Qt.Popup)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        #input Variable
        self.datasetLst = np.array(NewsDatabase().GetDataset())
        #output Variable
        self.resultIDSelected = ""
        
        #Select Label
        self.selectLbl = QtGui.QLabel("<h3>Open File</h3>",self)
        #Dataset Table
        self.datasetTbl = QtGui.QTableWidget(self)
        self.RefreshImportTable(self.datasetLst)
        #Open Button
        self.filterBtn = QtGui.QPushButton("Filter",self)
        self.filterBtn.clicked.connect(self.filterBtn_Clicked)
        
        Grid = QtGui.QGridLayout(self)
        Grid.setRowStretch(1,1)
        
        Grid.addWidget(self.selectLbl,0,0)
        Grid.addWidget(self.datasetTbl,1,0,1,3)
        Grid.addWidget(self.filterBtn,2,2)
        
    def RefreshImportTable(self, datasetLst_Prm):
        Datalist = datasetLst_Prm
        
        self.datasetTbl.setRowCount(len(Datalist))
        self.datasetTbl.setColumnCount(1)
        self.datasetTbl.setHorizontalHeaderLabels(["File Location"])
        self.datasetTbl.setVerticalHeaderLabels(['' for i in range(self.datasetTbl.rowCount())])
        self.datasetTbl.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.datasetTbl.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        
        for i in range ( 0, self.datasetTbl.rowCount() ):
            self.datasetTbl.setItem(i,0,QtGui.QTableWidgetItem(str(Datalist[i][1])))
            
    def filterBtn_Clicked(self):
        index = self.datasetTbl.currentRow()
        self.resultIDSelected = self.datasetLst[index][0]
        
        self.close()
        self.emit(QtCore.SIGNAL("DONE(QString)"),self.resultIDSelected) 
            
class ParameterDialog(QtGui.QDialog):
    def __init__(self, parent, SelectedFeatureMthdInt_Prm, maxInput_Prm):
        QtGui.QDialog.__init__(self)
        
        width = QtGui.QDesktopWidget().screenGeometry().width()
        height = QtGui.QDesktopWidget().screenGeometry().height()
        framewidth = width*0.2
        frameheight = height*0.1
        
        self.setWindowTitle("Parameter Dialog")
        self.setGeometry(QtCore.QRect(width/2 - framewidth/2, height/2 -frameheight/2, framewidth, frameheight))
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        #Lamda MMR Combobox
        self.mmrLambdaCbx = QtGui.QComboBox(self)
        for i in range(0 , 11):
            self.mmrLambdaCbx.addItem(str(i / 10))
        self.mmrLambdaCbx.hide()
        #DFW Combobox
        self.dfwstateCbx = QtGui.QComboBox(self)
        self.dfwstateCbx.addItem("False")
        self.dfwstateCbx.addItem("True")
        self.dfwstateCbx.hide()
        #Parameter Label
        self.parameterLbl = QtGui.QLabel("<h3>Parameter Input :</h3>",self)
        #IG Feature Label
        self.ignumfeaturetLbl = QtGui.QLabel("input Number of Feature IG",self)
        self.ignumfeaturetLbl.hide()        
        #MMR Feature Label
        self.mmrnumfeatureLbl = QtGui.QLabel("input Number of Feature MMR",self)
        self.mmrnumfeatureLbl.hide()
        #Lambda MMR Label
        self.mmrlambdaLbl = QtGui.QLabel("input Lambda",self)
        self.mmrlambdaLbl.hide()
        #DFW Label
        self.dfwstateLbl = QtGui.QLabel("Deep Feature Weighting ?",self)
        self.dfwstateLbl.hide()
        #IG Feature Text Field
        self.ignumfeatureTxt = QtGui.QSpinBox(self)
        self.ignumfeatureTxt.setMaximum(maxInput_Prm)
        self.ignumfeatureTxt.hide()
        #MMR Feature Text Field
        self.mmrnumfeatureTxt = QtGui.QSpinBox(self)
        self.mmrnumfeatureTxt.setMaximum(maxInput_Prm)
        self.mmrnumfeatureTxt.hide()
        #OK Button
        self.oKBtn = QtGui.QPushButton("OK",self)
        self.oKBtn.clicked.connect(self.okBtn_Clicked)
        
        Grid = QtGui.QGridLayout(self)
        Grid.setColumnStretch(0,1)
        
        Grid.addWidget(self.parameterLbl,0,0)
        Grid.addWidget(self.ignumfeaturetLbl,1,0)
        Grid.addWidget(self.ignumfeatureTxt,1,1)
        Grid.addWidget(self.mmrnumfeatureLbl,2,0)
        Grid.addWidget(self.mmrnumfeatureTxt,2,1)
        Grid.addWidget(self.mmrlambdaLbl,3,0)
        Grid.addWidget(self.mmrLambdaCbx,3,1)
        Grid.addWidget(self.dfwstateLbl,4,0)
        Grid.addWidget(self.dfwstateCbx,4,1)
        Grid.addWidget(self.oKBtn,5,1)
        
        if(SelectedFeatureMthdInt_Prm == 1):
            self.__IGinputenable()
        elif(SelectedFeatureMthdInt_Prm == 2):
            self.__MMRinputenable()
        else:
            self.__IGinputenable()
            self.__MMRinputenable()
            self.__DFWinputenable()
        
    def __IGinputenable(self):
        self.ignumfeaturetLbl.show()
        self.ignumfeatureTxt.show()
    
    def __MMRinputenable(self):
        self.mmrnumfeatureLbl.show()
        self.mmrnumfeatureTxt.show()
        self.mmrlambdaLbl.show()
        self.mmrLambdaCbx.show()
        
    def __DFWinputenable(self):
        self.dfwstateLbl.show()
        self.dfwstateCbx.show()
        
    def okBtn_Clicked(self):
        self.emit(QtCore.SIGNAL("DONE(QString, QString, QString, QString)"),str(self.ignumfeatureTxt.text()), str(self.mmrnumfeatureTxt.text()), self.mmrLambdaCbx.currentText(), self.dfwstateCbx.currentText())
        
class saveDialog(QtGui.QDialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        
        width = QtGui.QDesktopWidget().screenGeometry().width()
        height = QtGui.QDesktopWidget().screenGeometry().height()
        framewidth = width*0.2
        frameheight = height*0.1
        
        self.setWindowTitle("Save Dialog")
        self.setGeometry(QtCore.QRect(width/2 - framewidth/2 , height/2 - frameheight/2, framewidth, frameheight))
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowFlags(QtCore.Qt.Popup)
        #Data Result name Label
        self.dataResultNameLbl = QtGui.QLabel("<h3>Save Result:</h3>")
        #Data Result name Text Field
        self.dataResultNameTxt = QtGui.QLineEdit()
        
        self.saveBtn = QtGui.QPushButton("Save")
        self.saveBtn.clicked.connect(self.saveBtn_Clicked)
        
        Grid = QtGui.QGridLayout()
        Grid.addWidget(self.dataResultNameLbl,0,0)
        Grid.addWidget(self.dataResultNameTxt,1,0,1,2)
        Grid.addWidget(self.saveBtn,2,1)
        
        self.setLayout(Grid)
    
    def saveBtn_Clicked(self):
        self.close()
        self.emit(QtCore.SIGNAL("StoreEvaluation(QString)"), self.dataResultNameTxt.text())
        
class ProgressDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        
        width = QtGui.QDesktopWidget().screenGeometry().width()
        height = QtGui.QDesktopWidget().screenGeometry().height()
        framewidth = width*0.2
        frameheight = height*0.05
        
        self.setGeometry(QtCore.QRect(width/2 - framewidth/2, height/2 - frameheight/2, framewidth, frameheight))
        self.setWindowTitle("Progress Dialog")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        self.progressBar = BusyProgressBar()
        
        Grid = QtGui.QGridLayout(self)
        
        Grid.addWidget(self.progressBar,0,0)
        
    def OpenProgressDialog(self, statusName_Prm):
        self.progressBar.setText(statusName_Prm)
        self.show()
        self.progressBar.setValue(0)
        
        

        