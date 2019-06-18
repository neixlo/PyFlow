from Qt import QtCore
from Qt import QtGui
import Qt
from PyFlow.UI import RESOURCES_DIR
from PyFlow.UI.Utils.Settings import *
from PyFlow.UI.Canvas.UICommon import *
from PyFlow.UI.Canvas.Painters import NodePainter
from PyFlow.UI.Canvas.UINodeBase import UINodeBase,InputTextField
from PyFlow.UI.Widgets.TextEditDialog import TextEditDialog
from PyFlow.UI.Widgets.QtSliders import pyf_ColorSlider
from PyFlow.UI.Widgets.PropertiesFramework import CollapsibleFormWidget
from Qt.QtWidgets import QGraphicsTextItem, QGraphicsWidget, QGraphicsItem

class UIstickyNote(UINodeBase):
    def __init__(self, raw_node):
        super(UIstickyNote, self).__init__(raw_node)
        self.color = QtGui.QColor(255, 255, 136)
        self.color.setAlpha(255)
        self.labelTextColor = QtGui.QColor(0, 0, 0, 255)
        self.resizable = True

        self.textInput = InputTextField("Text Goes Here", self, singleLine=False)
        self.textInput.setPos(QtCore.QPointF(5, self.nodeNameWidget.boundingRect().height()))
        self.textInput.document().contentsChanged.connect(self.updateSize)
        self.textWidget = QGraphicsWidget()
        self.textWidget.setGraphicsItem(self.textInput)
        self.nodeLayout.addItem(self.textWidget)
        self.updateSize()

    def serializationHook(self):
        original = super(UIstickyNote, self).serializationHook()
        original["color"] = self.color.rgba()
        original["textColor"] = self.labelTextColor.rgba()
        original["currentText"] = self.textInput.toHtml()
        return original

    def postCreate(self, jsonTemplate=None):
        super(UIstickyNote, self).postCreate(jsonTemplate=jsonTemplate)
        if "color" in jsonTemplate["wrapper"]:
            self.color = QtGui.QColor.fromRgba(jsonTemplate["wrapper"]["color"])
        if "textColor" in jsonTemplate["wrapper"]:
            self.labelTextColor = QtGui.QColor.fromRgba(jsonTemplate["wrapper"]["textColor"])
        if "currentText" in jsonTemplate["wrapper"]:
            self.textInput.setHtml(jsonTemplate["wrapper"]["currentText"])

    def mouseDoubleClickEvent(self, event):
        self.textInput.setFlag(QGraphicsWidget.ItemIsFocusable,True)
        self.textInput.setFocus()
        super(UIstickyNote, self).mouseDoubleClickEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            if value == False:
                self.textInput.clearFocus()
                self.textInput.setFlag(QGraphicsWidget.ItemIsFocusable,False)
        return super(UIstickyNote, self).itemChange(change, value)

    def aboutToCollapse(self, futureCollapseState):
        if not futureCollapseState:
            self.textInput.show()
        else:
            self.textInput.hide()

    def paint(self, painter, option, widget):
        NodePainter.asCommentNode(self, painter, option, widget)
        self.updateSize()

    def mouseMoveEvent(self, event):
        super(UIstickyNote, self).mouseMoveEvent(event)
        self.updateSize()

    def updateSize(self):
        self.textInput.setTextWidth(self.boundingRect().width()-10)
        newHeight = self.textInput.boundingRect().height()+self.nodeNameWidget.boundingRect().height() + 5
        if self._rect.height() < newHeight:
            self._rect.setHeight(newHeight)
            try:
                self.updateNodeShape()
            except:
                pass
        self.minHeight = newHeight

    def updateColor(self,color):
        res = QtGui.QColor(color[0],color[1],color[2],color[3])
        if res.isValid():
            self.color = res
            self.update() 

    def updateTextColor(self,color):
        res = QtGui.QColor(color[0],color[1],color[2],color[3])
        if res.isValid():
            self.labelTextColor = res
            self.textInput.setDefaultTextColor(res)
            self.update() 

    def createInputWidgets ( self,propertiesWidget):
        inputsCategory = super(UIstickyNote, self).createInputWidgets(propertiesWidget)
        appearanceCategory = CollapsibleFormWidget(headName="Appearance")
        pb = pyf_ColorSlider(type="int",alpha=True,startColor=list(self.color.getRgbF()))
        pb.valueChanged.connect(self.updateColor)
        appearanceCategory.addWidget("Color", pb)
        pb = pyf_ColorSlider(type="int",alpha=True,startColor=list(self.labelTextColor.getRgbF()))
        pb.valueChanged.connect(self.updateTextColor)
        appearanceCategory.addWidget("TextColor", pb)        
        propertiesWidget.addWidget(appearanceCategory)