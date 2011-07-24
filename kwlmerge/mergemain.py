# -*- coding: utf-8 -*-

from PyQt4 import Qt
from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL

from ui_mergemain import Ui_mergeMain

class mergeMain(QtGui.QDialog, Ui_mergeMain):
    
    def __init__(self, parent, possibilities, title=None):
        if len(possibilities)<2:
            raise ValueError('Two possibilities are needed to merge')

        QtGui.QDialog.__init__(self,parent)

        self.changeA=lambda i:self.srcSelect(self.viewA,i)
        self.changeB=lambda i:self.srcSelect(self.viewB,i)
        
        self.copyAtoEdit=lambda:self.copyToEdit(self.srcA)
        self.copyBtoEdit=lambda:self.copyToEdit(self.srcB)
        
        self.acceptA=lambda:self.pickResult(self.srcA)
        self.acceptB=lambda:self.pickResult(self.srcB)

        self.setupUi(self)

        HotClear=QtGui.QShortcut(QtGui.QKeySequence('Ctrl+R'), self.finalTxt)
        self.connect(HotClear, SIGNAL('activated()'), self.clearEdit )
        #EditOk=QtGui.QShortcut(QtGui.QKeySequence('Ctrl+Enter'), self.finalTxt)
        #self.connect(EditOk, SIGNAL('activated()'), self.accept )

        if title is not None:
            self.setWindowTitle(title)
            self.banner.setText(self.banner.text()+title)

        self.data=[]

        for name, value in possibilities:
            self.srcA.addItem(name)
            self.srcB.addItem(name)
            self.data.append(value)

        self.srcA.setCurrentIndex(1) # ensure onChange action is triggered

        self.srcA.setCurrentIndex(0)
        self.srcB.setCurrentIndex(1)

    def srcSelect(self, txt, idx):
        if idx>=0 and idx<len(self.data):
            txt.setText(self.data[idx])
        else:
            txt.setText('')

    def copyToEdit(self, sel):
        idx=sel.currentIndex()

        if idx>=0 and idx<len(self.data):
            self.finalTxt.append(self.data[idx])

    def pickResult(self, sel):
        self.copyToEdit(sel)
        self.accept()

    def clearEdit(self):
        cur = self.finalTxt.textCursor()
        cur.select(Qt.QTextCursor.Document)
        cur.removeSelectedText()

    def editChanged(self):
        txt= self.finalTxt.toPlainText()
        self.acceptBtn.setEnabled(not txt.isEmpty())

    def accept(self):
        self.merged=str(self.finalTxt.toPlainText())
        QtGui.QDialog.accept(self)
