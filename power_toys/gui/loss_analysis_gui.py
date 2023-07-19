from ..gui.ui.ui_loss_analysis_gui import Ui_MainWindow
import  sys
from PyQt5.QtWidgets import  *
from PyQt5 import QtWidgets, QtCore
from ..components.mosfet import MOSFET
from ..topology.buck import BUCK
from ..data.database import component_session
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from power_toys.components.inductor import Inductor

class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.series = QPieSeries()
        self.plot_line()
        self.filter_mosfet()
        self.init_ind()
        self.show()

    def plot_line(self):
        # 创建一个饼图系列
        self.series.append("con", 1)
        self.series.append("on", 0)
        self.series.append("off", 0)
        self.series.append("dri", 0)
        self.series.append("cap", 0)
        self.series.append("qrr", 0)

        # 创建一个图表，并添加饼图系列
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.legend().setAlignment(Qt.AlignRight)  # 将图例放在右边
        self.chart.setTheme(QChart.ChartThemeBlueNcs)  # 设置暗色主题
        # 创建一个图表视图，用于显示图表
        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

        # 创建一个垂直布局，并添加图表视图
        layout = QVBoxLayout()
        layout.addWidget(chart_view)

        # 将布局设置到QFrame上
        self.plot_frame.setLayout(layout)
        # self.setCentralWidget(chart_view)

    def refresh_plot(self):
        self.series.clear()
        self.series.append("con", self.loss_con)
        self.series.append("on", self.loss_on)
        self.series.append("off", self.loss_off)
        self.series.append("dri", self.loss_dri)
        self.series.append("cap", self.loss_cap)
        self.series.append("qrr", self.loss_qrr)
        self.series.append("Inductor DC loss",self.buck.p_ind_dc())
        self.series.append("Inductor AC loss",self.buck.p_ind_ac())
        self.chart.createDefaultAxes()

    def loss_analysis(self):
        vin =   float(self.value_vin.text())
        vo =    float(self.value_vo.text())
        fs =    float(self.value_fs.text())
        po =    float(self.value_po.text())
        ncell = float(self.value_ncell.text())
        ind =   float(self.value_ind.text())
        mos1_para = float(self.value_mos1_parallel.text())
        mos2_para = float(self.value_mos2_parallel.text())
        mos1 = MOSFET.load_from_lib(self.value_mos1.currentText().split(':')[1].strip())
        mos2 = MOSFET.load_from_lib(self.value_mos2.currentText().split(':')[1].strip())

        ind_series = self.value_ind_series.currentText()
        ind_value = float(self.value_ind_inductance.currentText()[:-2])*1e-6
        ind_id = Inductor.id_from_inductance(ind_value,ind_series)

        if(mos1 != None and mos2 != None):
            self.buck = BUCK(
                vin=vin,
                vo=vo,
                Ncell = ncell,
                q_active=mos1.parallel(mos1_para),
                q_passive=mos2.parallel(mos2_para),
                ind=Inductor(ind_id),
                fs = fs,
                ro = vo**2/po
                )
            self.loss_con = self.buck.p_con(BUCK.ACTIVE_MOS)+self.buck.p_con(BUCK.PASSIVE_MOS)
            self.loss_on = self.buck.p_on(BUCK.ACTIVE_MOS)+self.buck.p_on(BUCK.PASSIVE_MOS)
            self.loss_off = self.buck.p_off(BUCK.ACTIVE_MOS)+self.buck.p_off(BUCK.PASSIVE_MOS)
            self.loss_cap = self.buck.p_cap(BUCK.ACTIVE_MOS)+self.buck.p_cap(BUCK.PASSIVE_MOS)
            self.loss_dri = self.buck.p_dri(BUCK.ACTIVE_MOS)+self.buck.p_dri(BUCK.PASSIVE_MOS)
            self.loss_qrr = self.buck.p_qrr(BUCK.ACTIVE_MOS)+self.buck.p_qrr(BUCK.PASSIVE_MOS)
            self.loss_ind_dc = self.buck.p_ind_dc()
            self.loss_ind_ac = self.buck.p_ind_ac()
            self.temp_ind = self.buck.temp_ind()
            self.value_loss_con.setText(f"{self.loss_con:.2f}W")
            self.value_loss_on.setText(f"{self.loss_on:.2f}W")
            self.value_loss_off.setText(f"{self.loss_off:.2f}W")
            self.value_loss_cap.setText(f"{self.loss_cap:.2f}W")
            self.value_loss_dri.setText(f"{self.loss_dri:.2f}W")
            self.value_loss_qrr.setText(f"{self.loss_qrr:.2f}W")
            self.value_ind_30per.setText(f"{self.buck.volt_sec/(0.3*self.buck.io)*1e6:.2f}uH")
            
            self.value_loss_total.setText(f"{self.buck.p_total():.2f}W")
            self.value_loss_eff.setText(f"{self.buck.efficiency*100:.1f}%")
            if(self.loss_ind_dc < 0):
                self.value_loss_ind_dc.setText("饱和")
                self.value_loss_ind_ac.setText("饱和")
                self.value_temp_ind.setText("饱和")
            else:
                self.value_loss_ind_dc.setText(f"{self.loss_ind_dc:.2f}W")
                self.value_loss_ind_ac.setText(f"{self.loss_ind_ac:.2f}W")
                self.value_temp_ind.setText(f"{self.temp_ind:.2f}°C")
            self.refresh_plot()
    
    def filter_mosfet(self):
        try:
            vin = float(self.value_vin.text())
            ncell = float(self.value_ncell.text())
        except:
            return
        mosfets = component_session.query(MOSFET).order_by(MOSFET.vbr,MOSFET.rdson).filter(MOSFET.vbr>=1.3*(vin/ncell)).all()
        self.value_mos1.clear()
        self.value_mos2.clear()
        for result in mosfets:
            self.value_mos1.addItem(f"{result.vbr}V/{result.rdson*1000:.1f}mR: {result.id}")
            self.value_mos2.addItem(f"{result.vbr}V/{result.rdson*1000:.1f}mR: {result.id}")
    
    def update_FoM(self):
        try:
            mos1 = MOSFET.load_from_lib(self.value_mos1.currentText().split(':')[1].strip())
            mos2 = MOSFET.load_from_lib(self.value_mos2.currentText().split(':')[1].strip())
            self.value_FoM1.setText(f"{mos1.FoM*1e12:.1f}")
            self.value_FoM2.setText(f"{mos2.FoM*1e12:.1f}")
        except IndexError:
            return
    
    def update_inductance(self):
        ind_list = Inductor.list_all()
        ind_series = self.value_ind_series.currentText()
        self.value_ind_inductance.clear()
        inductance_list = []
        for ind in ind_list:
            ind_inst = Inductor(ind)
            if(ind_inst.series == ind_series):
                inductance_list.append(ind_inst.inductance)
        
        inductance_list = sorted(inductance_list)
        for inductance in inductance_list:
            self.value_ind_inductance.addItem(f"{inductance*1e6:.2f}uH")
    
    def init_ind(self):
        ind_list = Inductor.list_all()
        self.value_ind_series.clear()
        for ind in ind_list:
            ind_inst = Inductor(ind)
            if(self.value_ind_series.findText(ind_inst.series) == -1):
                self.value_ind_series.addItem(ind_inst.series)


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())