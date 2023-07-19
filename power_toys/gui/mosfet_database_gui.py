import  sys
from PyQt5.QtWidgets import  *
from ..gui.ui.ui_mosfet_database_gui import Ui_MainWindow
from ..components.mosfet import MOSFET
from ..model_params import mosfet_param_list
from ..data.database import component_session
import sqlalchemy
import pyperclip
from PyQt5 import QtWidgets, QtCore


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.mos = None
        self.init_item_list()
        self.show()
    def get_mos_from_ui(self):
        try:
            mos = MOSFET(
                id        =   self.ui.id.currentText(),
                rdson     =   float(self.ui.rdson.text())*1e-3,
                vbr       =   float(self.ui.vbr.text()),
                vgsth     =   float(self.ui.vgsth.text()),
                rg        =   float(self.ui.rg.text()),
                qg        =   float(self.ui.qg.text())*1e-9,
                qgd       =   float(self.ui.qgd.text())*1e-9,
                qg_soft   =   float(self.ui.qg_soft.text())*1e-9,
                cosse     =   float(self.ui.cosse.text())*1e-12,
                cosst     =   float(self.ui.cosst.text())*1e-12,
                qrr       =   float(self.ui.qrr.text())*1e-9,
                qgs2      =   float(self.ui.qgs2.text())*1e-9,
                vplateau  =   float(self.ui.vplateau.text()),
                kdyn      =   float(self.ui.kdyn.text()),
                ktemp     =   float(self.ui.ktemp.text()),
                vgs       =   float(self.ui.vgs.text()),
                vgs_min   =   float(self.ui.vgs_min.text()),
                footprint =   self.ui.footprint.text()
            )
            return mos
        except:
            return
    def save(self):
        self.mos = self.get_mos_from_ui()
        self.mos.save_to_db()
        QMessageBox.information(self,"Info","Success")

    def load(self):
        try:
            self.id = self.ui.id.currentText()
            m = MOSFET.load_from_lib(_id=self.id)
            self.mos = m
            self.ui.rdson.setText(f"{float(m.rdson*1e3):.1f}")
            self.ui.vbr.setText(f"{float(m.vbr):.1f}")
            self.ui.vgsth.setText(f"{float(m.vgsth):.1f}")
            self.ui.rg.setText(f"{float(m.rg):.1f}")
            self.ui.qg.setText(f"{float(m.qg*1e9):.1f}")
            self.ui.qgd.setText(f"{float(m.qgd*1e9):.1f}")
            self.ui.qg_soft.setText(f"{float(float(m.qg_soft)*1e9):.1f}")
            self.ui.cosse.setText(f"{float(m.cosse*1e12):.1f}")
            self.ui.cosst.setText(f"{float(m.cosst*1e12):.1f}")
            self.ui.qrr.setText(f"{float(m.qrr*1e9):.1f}")
            self.ui.qgs2.setText(f"{float(m.qgs2*1e9):.1f}")
            self.ui.vplateau.setText(f"{float(m.vplateau):.1f}")
            self.ui.kdyn.setText(f"{float(m.kdyn):.1f}")
            self.ui.ktemp.setText(f"{float(m.ktemp):.1f}")
            self.ui.vgs.setText(f"{float(m.vgs):.1f}")
            self.ui.vgs_min.setText(f"{float(m.vgs_min):.1f}")
            self.ui.footprint.setText(m.footprint)
            self.update_FoM()
        except TypeError:
            print("Not found")
        except:
            return

    def update_db(self):
        self.mos = self.get_mos_from_ui()
        self.mos.update_to_db()
        print(type(self.mos.vgs_min))
        QMessageBox.information(self,"Info","Success")

    def check_id(self):
        self.id = self.ui.id.text()
        if(self.id):
            m = MOSFET.load_from_lib(_id=self.id)
            if m and m.id:
                self.load()
                self.update_FoM()
                
    def update_FoM(self):
        FoM = self.mos.rdson*self.mos.qg
        NFoM = self.mos.rdson*self.mos.cosst
        NFoMoss = self.mos.rdson*self.mos.cosse
        self.ui.NFoM.setText(f"{NFoM*1e15:.0f}")
        self.ui.FoM.setText(f"{FoM*1e12:.0f}")
        self.ui.NFoMoss.setText(f"{NFoMoss*1e15:.0f}")
    
    def load_by_condition(self):
        condition = ''
        for i in range(4):
            param_select = getattr(self.ui,f"param{i+1}_select").currentText()
            param_condition = getattr(self.ui,f"param{i+1}_condition").currentText()
            param_value = getattr(self.ui,f"param{i+1}_value").text()
            if(param_value) == '':
                continue
            if(i != 0):
                logic = getattr(self.ui,f"logic{i}").currentText()
                condition += f" {logic} "

            if(param_select == 'id'):
                condition += f"{param_select} {param_condition} '{param_value}'"
            else:
                condition += f"{param_select} {param_condition} {param_value}"
            
        query = component_session.query(MOSFET).filter(sqlalchemy.text(condition))
        results = query.all()
        self.ui.id.clear()
        for result in results:
            self.ui.id.addItem(result.id)
    
    def init_item_list(self):
        mosfets = component_session.query(MOSFET).all()
        self.ui.id.clear()
        for result in mosfets:
            self.ui.id.addItem(result.id)
    
    def copy_id(self):
        id = self.ui.id.currentText()
        pyperclip.copy(id)

QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())