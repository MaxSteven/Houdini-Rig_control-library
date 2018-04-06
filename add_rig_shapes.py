from hutil.Qt.QtWidgets import *

import hou, json, os

class myWidget (QWidget):
    def __init__(self):
        super(myWidget, self).__init__()
        self.setProperty("houdiniStyle", True)
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        self.grpBox = QGroupBox("Path to file with Settings")
        self.ln_filepath = QLineEdit()
        self.btn_settings = QPushButton("...", clicked=self.setFilePath)
        hbox = QHBoxLayout()
        hbox.addWidget(self.ln_filepath)
        hbox.addWidget(self.btn_settings)
        self.grpBox.setLayout(hbox)
        mainLayout.addWidget(self.grpBox)

        self.grpBox2 = QGroupBox()
        self.lb_shapename = QLabel("Enter Shape Name")
        self.ln_shapename = QLineEdit()
        self.btn_addshape = QPushButton("Add To Library", clicked=self.addNewShape)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.lb_shapename)
        hbox2.addWidget(self.ln_shapename)
        hbox2.addWidget(self.btn_addshape)

        self.grpBox2.setLayout(hbox2)
        mainLayout.addWidget(self.grpBox2) 

        self.comboBox = QComboBox()
        # self.comboBox.addItem("test")         
        mainLayout.addWidget(self.comboBox)
        self.btn_createNull = QPushButton("Create Null")
        mainLayout.addWidget(self.btn_createNull)




        spacerItem = QSpacerItem(40, 400, QSizePolicy.Expanding, QSizePolicy.Expanding)
        mainLayout.addItem(spacerItem)


        self.btn_settings.clicked.connect(self.updateUI)
        # self.ln_filepath.textChanged.connect(self.updateUI)
        self.btn_addshape.clicked.connect(self.updateUI)
        self.btn_createNull.clicked.connect(self.createNull)

    def setFilePath(self):
        _filter = "*.json"
        d = QFileDialog.getOpenFileName(self, "Select Path to Save", hou.hipFile.path(), _filter)
        self.ln_filepath.setText(d[0])



    def addNewShape(self):
        path_file = self.ln_filepath.text()
        sel = (hou.selectedNodes() or [None])[0]
        text_type = self.ln_shapename.text()



        if self.ln_shapename.text():
            points = sel.geometry().points()
            prims = sel.geometry().prims()
            # print prims[0].type()
            if prims[0].type() == hou.primType.BezierCurve:
                pr_type = 2
            elif prims[0].type() == hou.primType.NURBSCurve:
                pr_type = 1
            elif prims[0].type() == hou.primType.Polygon:
                pr_type = 0
            pnt_array = []

            for poly in prims:
                poly_geo = []
                for vtx in poly.vertices():
                    pos = vtx.point().attribValue("P") 
                    poly_geo.append(pos)
                pnt_array.append(poly_geo)

            settings = []
            read = json.load(open(path_file))
            for r in read:
                settings.append(r)

            x = {'type':text_type,'pr_type':pr_type, 'point': pnt_array }
            settings.append(x)
            json.dump(settings, open(path_file, "w"), indent=4)





    def updateUI(self):
        path = self.ln_filepath.text()
        if os.path.exists(path):
            self.comboBox.clear()
            read = json.load(open(path))
            for r in read:
                self.comboBox.addItem(r["type"]) 

    def createNull(self):
        path = self.ln_filepath.text()
        if os.path.exists(path):
            read = json.load(open(path))
            obj = hou.node('obj')
            name = self.comboBox.currentText()
            for r in read:
                if name == r["type"]:
                    geo = obj.createNode("null", name, False)
                    geo.moveToGoodPosition()
                    merge = geo.createNode("merge")
                    merge.moveToGoodPosition()
                    merge.setDisplayFlag(1)
                    curves_array = []
                    for idx, i in enumerate(r['point']):
                        curve = geo.createNode("curve")
                        curve.parm('type').set(r['pr_type'])
                        pList = " ".join([",".join(str(d) for d in x) for x in r['point'][idx]])
                        curve.parm('coords').set(pList)
                        curve.moveToGoodPosition()
                        curves_array.append(curve)
                        
                    for c in curves_array:
                        merge.setNextInput(c)

        
        



def createInterface():
    w = myWidget()
    return w
