# -*- coding: utf-8 -*-

from PyQt4 import Qt
from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL

from ui_mergemain import Ui_mergeMain

class mergeMain(QtGui.QDialog, Ui_mergeMain):
    
    def __init__(self, parent, A, B, title=None):
        self.merged = None
        QtGui.QDialog.__init__(self,parent)
        
        self.copyAtoEdit=lambda:self.copyToEdit(self.viewA)
        self.copyBtoEdit=lambda:self.copyToEdit(self.viewB)
        
        self.acceptA=lambda:self.pickResult(self.viewA)
        self.acceptB=lambda:self.pickResult(self.viewB)

        self.setupUi(self)

        HotClear=QtGui.QShortcut(QtGui.QKeySequence('Ctrl+R'), self.finalTxt)
        self.connect(HotClear, SIGNAL('activated()'), self.clearEdit )
        #EditOk=QtGui.QShortcut(QtGui.QKeySequence('Ctrl+Enter'), self.finalTxt)
        #self.connect(EditOk, SIGNAL('activated()'), self.accept )

        if title is not None:
            self.setWindowTitle(title)
            self.banner.setText(self.banner.text()+title)

        self.viewA.setText(A)
        self.viewB.setText(B)

    def copyToEdit(self, sel):
        self.finalTxt.setText(sel.toHtml())

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
