# -*- coding: utf-8 -*-

from PyQt4 import Qt
from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL

from ui_exportmain import Ui_exportMain

class exportMain(QtGui.QDialog, Ui_exportMain):
    
    def __init__(self, parent=None, file=None, title=None):
        QtGui.QDialog.__init__(self,parent)
        
        self.setupUi(self)

        self.model=QtGui.QStandardItemModel()
        root=self.model.invisibleRootItem()
        
        root.appendRow(QtGui.QStandardItem("hello"))
        root.appendRow(QtGui.QStandardItem("world"))
