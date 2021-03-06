import sys
import os
import random
import pyqtgraph as pg
import numpy as np
import nmrglue as ng
import warnings
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QColorDialog

warnings.filterwarnings('ignore')


class Ui_MainWindow(object):
    spectra = {}
    current_spectrum = None

    def setup_ui(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1450, 920)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.graphics_view = pg.PlotWidget(self.centralwidget)
        self.mouse_clicked = True
        self.peak_box = None

        # Control Object
        self.c = Control()

        # Contour Spectrum
        # self.graphics_view.setEnabled(False)
        self.graphics_view.setGeometry(QtCore.QRect(190, 70, 1211, 811))
        self.graphics_view.setObjectName("graphics_view")
        self.graphics_view.showGrid(x=True, y=True, alpha=0.5)
        self.graphics_view.getViewBox().invertX(True)
        self.graphics_view.getViewBox().invertY(True)
        self.graphics_view.enableAutoRange()

        # Mouse Location
        self.graphics_view.scene().sigMouseMoved.connect(self.on_mouse_move)
        self.graphics_view.scene().sigMouseClicked.connect(self.on_mouse_click)

        # P0 Slider
        self.p0_slider = QtWidgets.QSlider(self.centralwidget)
        self.p0_slider.setGeometry(QtCore.QRect(360, 40, 221, 21))
        self.p0_slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.p0_slider.setObjectName("p0_slider")
        self.p0_slider.setMinimum(-180.0)
        self.p0_slider.setMaximum(180.0)
        self.p0_slider.setValue(0.0)
        self.p0_slider.setSingleStep(0.1)
        self.p0_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.p0_slider.setTickInterval(30)
        self.p0_window = QtWidgets.QLineEdit(self.centralwidget)
        self.p0_window.setGeometry(QtCore.QRect(590, 40, 41, 21))
        self.p0_window.setObjectName("p0_window")
        self.p0_window.setText(str(self.p0_slider.value()))
        self.p0_window.textChanged.connect(self.set_p0)

        self.p0_slider.valueChanged.connect(self.p0_phase)

        # P1 Slider
        self.p1_slider = QtWidgets.QSlider(self.centralwidget)
        self.p1_slider.setGeometry(QtCore.QRect(680, 40, 221, 21))
        self.p1_slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.p1_slider.setObjectName("p1_slider")
        self.p1_slider.setMinimum(-180.0)
        self.p1_slider.setMaximum(180.0)
        self.p1_slider.setValue(0.0)
        self.p1_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.p1_slider.setTickInterval(30)
        self.p1_window = QtWidgets.QLineEdit(self.centralwidget)
        self.p1_window.setGeometry(QtCore.QRect(910, 40, 41, 21))
        self.p1_window.setObjectName("p1_window")
        self.p1_window.setText(str(self.p1_slider.value()))
        self.p1_window.textChanged.connect(self.set_p1)

        self.p1_slider.valueChanged.connect(self.p1_phase)

        # Contour Level Control
        self.set_contour_level = QtWidgets.QSpinBox(self.centralwidget)
        self.set_contour_level.setGeometry(QtCore.QRect(240, 30, 71, 31))
        self.set_contour_level.setObjectName("set_contour_level")
        self.set_contour_level.setValue(15)
        self.set_contour_level.valueChanged.connect(self.c.depth)

        # Labels
        self.contour_level_label = QtWidgets.QLabel(self.centralwidget)
        self.contour_level_label.setGeometry(QtCore.QRect(190, 40, 60, 16))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.contour_level_label.setFont(font)
        self.contour_level_label.setObjectName("contour_level_label")
        self.p0_label = QtWidgets.QLabel(self.centralwidget)
        self.p0_label.setGeometry(QtCore.QRect(330, 40, 60, 16))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.p0_label.setFont(font)
        self.p0_label.setObjectName("p0_label")
        self.p1_label = QtWidgets.QLabel(self.centralwidget)
        self.p1_label.setGeometry(QtCore.QRect(650, 40, 60, 16))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.p1_label.setFont(font)
        self.p1_label.setObjectName("p1_label")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 70, 171, 211))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.groupBox.setFont(font)
        self.groupBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.groupBox.setObjectName("groupBox")
        self.file_label = QtWidgets.QLabel(self.groupBox)
        self.file_label.setGeometry(QtCore.QRect(10, 40, 60, 16))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.file_label.setFont(font)
        self.file_label.setObjectName("file_label")

        # Add Spectrum Button
        self.add_button = QtWidgets.QPushButton(self.groupBox)
        self.add_button.setGeometry(QtCore.QRect(40, 70, 61, 31))
        self.add_button.setObjectName("add_button")
        font = QtGui.QFont()
        font.setPointSize(13)
        self.add_button.setFont(font)
        self.add_button.clicked.connect(self.open_file_dialog)

        # Remove Spectrum Button
        self.remove_button = QtWidgets.QPushButton(self.groupBox)
        self.remove_button.setGeometry(QtCore.QRect(100, 70, 71, 31))
        self.remove_button.setObjectName("remove_button")
        self.remove_button.setFont(font)
        try:
            self.remove_button.clicked.connect(self.remove_spectrum)
        except AttributeError:
            pass

        # Spectrum Selector
        self.file_selector = QtWidgets.QComboBox(self.groupBox)
        self.file_selector.setGeometry(QtCore.QRect(40, 35, 131, 31))
        self.file_selector.setObjectName("file_selector")
        self.current_spectrum = self.file_selector.currentData()
        self.file_selector.activated[str].connect(self.on_selection)

        # Color Selector
        self.color_selector = QtWidgets.QPushButton(self.groupBox)
        self.color_selector.setGeometry(QtCore.QRect(40, 100, 131, 32))
        self.color_selector.setText("")
        self.color_selector.setObjectName("color_selector")
        self.color_selector.clicked.connect(self.open_color_dialog)

        # Toggle Contours
        self.contour_box = QtWidgets.QCheckBox(self.groupBox)
        self.contour_box.setGeometry(QtCore.QRect(0, 140, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.contour_box.setFont(font)
        self.contour_box.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.contour_box.setObjectName("contour_box")
        self.contour_box.stateChanged.connect(self.set_spectrum_visibility)

        # Toggle Peaks
        self.peaks_box = QtWidgets.QCheckBox(self.groupBox)
        self.peaks_box.setGeometry(QtCore.QRect(70, 140, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.peaks_box.setFont(font)
        self.peaks_box.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.peaks_box.setObjectName("peaks_box")
        self.peaks_box.stateChanged.connect(self.set_peak_visibility)

        font = QtGui.QFont()
        font.setPointSize(13)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(0, 100, 51, 31))
        self.label_5.setObjectName("label_5")
        self.label_5.setFont(font)

        # Toggle X-Slice
        self.x_slice_box = QtWidgets.QCheckBox(self.groupBox)
        self.x_slice_box.setGeometry(QtCore.QRect(0, 170, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.x_slice_box.setFont(font)
        self.x_slice_box.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.x_slice_box.setObjectName("x_slice_box")
        self.x_slice_box.stateChanged.connect(self.show_x_slice)

        # Toggle Y-Slice
        self.y_slice_box = QtWidgets.QCheckBox(self.groupBox)
        self.y_slice_box.setGeometry(QtCore.QRect(70, 170, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.y_slice_box.setFont(font)
        self.y_slice_box.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.y_slice_box.setObjectName("y_slice_box")
        self.y_slice_box.stateChanged.connect(self.show_y_slice)

        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(40, 10, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1450, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 280, 171, 431))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_2.setObjectName("groupBox_2")
        self.listWidget = QtWidgets.QListWidget(self.groupBox_2)
        self.listWidget.setGeometry(QtCore.QRect(0, 30, 171, 391))
        self.listWidget.setObjectName("listWidget")

        self.listWidget.itemSelectionChanged.connect(self.selection_changed)

        self.v_line = pg.InfiniteLine(angle=90, movable=False)
        self.h_line = pg.InfiniteLine(angle=0, movable=False)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.contour_level_label.setText(_translate("MainWindow", "Level:"))
        self.p0_label.setText(_translate("MainWindow", "P0:"))
        self.p1_label.setText(_translate("MainWindow", "P1:"))
        self.groupBox.setTitle(_translate("MainWindow", "Spectrum"))
        self.file_label.setText(_translate("MainWindow", "File:"))
        self.contour_box.setText(_translate("MainWindow", "Contour"))
        self.peaks_box.setText(_translate("MainWindow", "Peaks"))
        self.x_slice_box.setText(_translate("MainWindow", "X-Slice"))
        self.y_slice_box.setText(_translate("MainWindow", "Y-Slice"))
        self.label_7.setText(_translate("MainWindow", "test"))
        self.add_button.setText(_translate("MainWindow", "Add"))
        self.remove_button.setText(_translate("MainWindow", "Remove"))
        self.label_5.setText(_translate("MainWindow", " Color:"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Peaks"))

    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(options=options)
        if fileName:
            self.add_spectrum(Spectrum(fileName))
        # try:
        #     if fileName:
        #         self.add_spectrum(Spectrum(fileName))
        # except:
        #     print('Error: Could not open file')

    def open_color_dialog(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.change_color(color.name())

    def add_spectrum(self, spectrum):
        if not spectrum.__str__() in self.spectra:
            if self.current_spectrum is None:
                self.graphics_view.enableAutoRange()

            for i in range(spectrum.spec_start, spectrum.spec_start + spectrum.spec_depth):
                print(f'Loading isocurve {i - spectrum.spec_start + 1} of {spectrum.spec_depth}')
                self.graphics_view.addItem(spectrum.contours[i])
            self.spectra[spectrum.__str__()] = spectrum
            self.file_selector.addItem(spectrum.__str__())
            self.current_spectrum = spectrum
            self.color_selector.setStyleSheet(f'background-color: {spectrum.get_color()}')
            self.on_selection()
            self.display_peaks(spectrum)
            self.list_peaks()

            self.graphics_view.disableAutoRange()
        else:
            print('Error: Spectrum is already loaded')

    def remove_spectrum(self):
        s = self.current_spectrum
        try:
            for i in range(len(s.contours)):
                self.graphics_view.removeItem(s.contours[i])
            self.graphics_view.removeItem(s.scatter_plot)
            self.spectra.pop(s.__str__())
            spec_index = self.file_selector.currentIndex()
            self.file_selector.removeItem(spec_index)
            self.graphics_view.removeItem(self.xslice_line)
            self.graphics_view.removeItem(self.yslice_line)
            self.color_selector.setStyleSheet("")
            self.contour_box.setChecked(False)
            self.peaks_box.setChecked(False)
            self.current_spectrum = None
            print(f'Removed {s.__str__()}')
        except (KeyError, AttributeError):
            print('Error: No spectrum selected')

    def on_selection(self):
        print(self.file_selector.currentText())
        self.current_spectrum = self.spectra[self.file_selector.currentText()]
        self.set_contour_level.setValue(self.current_spectrum.spec_start)
        self.color_selector.setStyleSheet(f'background-color: {self.current_spectrum.get_color()}')
        self.contour_box.setChecked(self.current_spectrum.get_visibility())
        self.peaks_box.setChecked(self.current_spectrum.get_peak_visibility())
        self.x_slice_box.setChecked(self.current_spectrum.get_xslice_state())
        self.y_slice_box.setChecked(self.current_spectrum.get_yslice_state())
        self.list_peaks()

    def on_mouse_click(self):
        print(self.p.x(), self.p.y())

    def on_mouse_move(self, point):
        self.p = self.graphics_view.plotItem.vb.mapSceneToView(point)
        self.label_7.setText(f'x: {round(self.p.x(), 3)} , y: {round(self.p.y(), 3)}')

        self.v_line.setValue(self.p.x())
        self.h_line.setValue(self.p.y())

        try:
            if self.current_spectrum is not None and self.current_spectrum.get_xslice_state():
                x_pos = self.current_spectrum.xslice_data(self.p.y(), self.p0_slider.value())
                self.xslice_line.setData(x_pos[0], x_pos[1])

            if self.current_spectrum is not None and self.current_spectrum.get_yslice_state():
                y_pos = self.current_spectrum.yslice_data(self.p.x())
                self.yslice_line.setData(y_pos[0], y_pos[1])
        except IndexError:
            pass

    def change_depth(self, spectrum):
        val = self.set_contour_level.value()
        if val > spectrum.spec_start:
            print(f'spectrum depth: {val}')
            self.graphics_view.removeItem(spectrum.contours[spectrum.spec_start])
            spectrum.spec_start = val
            self.graphics_view.addItem(spectrum.contours[spectrum.spec_start + spectrum.spec_depth])
        elif val < spectrum.spec_start:
            print(f'spectrum depth: {val}')
            self.graphics_view.removeItem(spectrum.contours[spectrum.spec_start + spectrum.spec_depth])
            spectrum.spec_start = val
            self.graphics_view.addItem(spectrum.contours[spectrum.spec_start])

    def change_color(self, color):
        s = self.current_spectrum
        for i in range(len(s.contours)):
            s.contours[i].setPen(color)
        s.set_color(color)
        self.color_selector.setStyleSheet(f'background-color: {s.get_color()}')

    def set_spectrum_visibility(self, state=True):
        s = self.current_spectrum
        print(f'{s.__str__()} visibility {True if state == 2 else False}')
        if state:
            s.set_visibility(True)
            for i in range(len(s.contours)):
                s.contours[i].setPen(s.get_color())

        else:
            s.set_visibility(False)
            for i in range(len(s.contours)):
                s.contours[i].setPen(None)

    def set_peak_visibility(self, state=False):
        s = self.current_spectrum
        if state:
            s.scatter_plot.setPen('w')
            s.set_peak_visibility(True)
        else:
            s.scatter_plot.setPen(None)
            s.set_visibility(False)
            self.graphics_view.removeItem(self.peak_box)

    def show_x_slice(self, state=False):
        if state:
            self.graphics_view.addItem(self.h_line)
            self.xslice_line = pg.PlotCurveItem()
            self.graphics_view.addItem(self.xslice_line)
            self.current_spectrum.set_xslice_state(True)
        else:
            self.graphics_view.removeItem(self.h_line)
            self.graphics_view.removeItem(self.xslice_line)
            self.current_spectrum.set_xslice_state(False)

    def show_y_slice(self, state=False):
        if state:
            self.graphics_view.addItem(self.v_line)
            self.yslice_line = pg.PlotCurveItem()
            self.graphics_view.addItem(self.yslice_line)
            self.current_spectrum.set_yslice_state(True)
        else:
            self.graphics_view.removeItem(self.v_line)
            self.graphics_view.removeItem(self.yslice_line)
            self.current_spectrum.set_yslice_state(False)

    def display_peaks(self, spectrum):
        self.graphics_view.addItem(spectrum.scatter_plot)

    def p0_phase(self):
        self.p0_window.setText(str(self.p0_slider.value()))
        # if self.current_spectrum is not None and self.current_spectrum.get_xslice_state():
        #     x_pos = self.current_spectrum.xslice_data(self.p.y(), self.p0_slider.value())
        #     self.xslice_line.setData(x_pos[0], x_pos[1])

    def set_p0(self, val):
        self.p0_slider.setValue(float(val))

    def p1_phase(self):
        self.p1_window.setText(str(self.p1_slider.value()))

    def set_p1(self, val):
        self.p1_slider.setValue(float(val))

    def list_peaks(self):
        s = self.current_spectrum
        self.listWidget.clear()
        for i, (x, y) in enumerate(zip(s.peak_xlocations_ppm, s.peak_ylocations_ppm)):
            item = QtWidgets.QListWidgetItem(f'{i+1}: {round(x, 3)}, {round(y, 3)} ', self.listWidget)
            self.listWidget.addItem(item)

    def selection_changed(self):
        s = self.current_spectrum
        row_index = self.listWidget.currentRow()
        scale= (s.x1 - s.x0)/(s.y1 - s.y0)
        self.graphics_view.removeItem(self.peak_box)
        if s.get_peak_visibility():
            self.peak__highlight_box = pg.QtGui.QGraphicsRectItem(s.peak_xlocations_ppm[row_index] - 0.05, s.peak_ylocations_ppm[row_index]-0.3, 0.1, 0.66)
            self.peak_highlight_box.setPen(pg.mkPen('w'))
            self.graphics_view.addItem(self.peak__highlight_box)

class Spectrum:
    contour_start = 10  # contour level start value
    contour_num = 50  # number of contour levels
    contour_factor = 1.7
    spec_start = 15
    spec_depth = 15
    pthres = 50000


    def __init__(self, file):
        self.dic, self.data = ng.pipe.read(str(file))
        self.dic, self.data = ng.pipe_proc.rev(self.dic, self.data)
        self.file = file
        self.color = "%06x" % random.randint(0, 0xFFFFFF)
        self.contours = []
        self.display()
        self.contour_visibility = True
        self.peak_visibility = False
        self.xslice = False
        self.yslice = False
        self.current_p0_shift = 0.0

    def __str__(self):
        return str(os.path.basename(self.file))

    def __del__(self):
        return None

    def display(self):
        self.dic['FDF1QUADFLAG'] = 1.0
        self.uc_x = ng.pipe.make_uc(self.dic, self.data, dim=1)
        self.uc_y = ng.pipe.make_uc(self.dic, self.data, dim=0)
        peaks = ng.analysis.peakpick.pick(self.data.real, self.pthres, table=True, algorithm='connected',
                                          msep=[0.5, 1.5],
                                          cluster=True)
        self.x0, self.x1 = self.uc_x.ppm_limits()
        self.y0, self.y1 = self.uc_y.ppm_limits()
        self.peak_xlocations_ppm = [self.uc_x.ppm(i) for i in peaks['X_AXIS']]
        self.peak_ylocations_ppm = [self.uc_y.ppm(i) for i in peaks['Y_AXIS']]

        # Data is rotated: indices for dimensions are flipped from this point onward
        self.data = np.rot90(self.data)

        for x in range(self.contour_num):
            l = self.contour_start * self.contour_factor ** x
            c = pg.IsocurveItem(data=self.data, level=l, pen=self.color)
            c.translate(self.x0, self.y0)
            c.scale((self.x1 - self.x0) / self.data.shape[0], (self.y1 - self.y0) / self.data.shape[1])
            self.contours.append(c)

        # Flip peaks about x-axis
        self.mid = self.x1 - 0.5 * (self.x1 - self.x0)
        for i in range(len(self.peak_xlocations_ppm)):
            self.peak_xlocations_ppm[i] = 2 * self.mid - self.peak_xlocations_ppm[i]

        self.peaks_list = zip(self.peak_xlocations_ppm, self.peak_ylocations_ppm)
        self.scatter_plot = pg.ScatterPlotItem(pos=self.peaks_list, pen=None, brush=None, symbol='x', size=12)

        self.xslice_dataset = self.data
        self.yslice_dataset = self.data

    def xslice_data(self, y_pos, new_shift):
        self.xslice_dataset = ng.proc_base.ps(self.xslice_dataset, p0=new_shift - self.current_p0_shift)
        self.current_p0_shift = new_shift

        slice_int = round(self.uc_y.f(y_pos, 'PPM'))
        test_range_x = (self.x0 - self.x1) / self.xslice_dataset.shape[0]
        x = np.array([i * test_range_x for i in range(1, self.xslice_dataset.shape[0] + 1)])
        x += self.x1
        xslice = np.array(self.xslice_dataset.real[:, slice_int])
        y = np.array([self.uc_y.ppm(i) for i in xslice])
        y = y[::-1]
        y /= 3000
        y += y_pos
        data = (x, y)
        return data

    def yslice_data(self, x_pos):
        slice_int = round(self.uc_x.f(x_pos, 'PPM'))
        test_range_y = (self.y0 - self.y1) / self.data.shape[1]
        y = np.array([i * test_range_y for i in range(1, self.data.shape[1] + 1)])
        y += self.y1
        yslice = np.array(self.data.real[slice_int, :])
        x = np.array([self.uc_y.ppm(i) for i in yslice])
        x = x[::-1]
        x /= 10000
        x += x_pos
        data = (x, y)
        return data

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color

    def get_visibility(self):
        return self.contour_visibility

    def set_visibility(self, state):
        self.contour_visibility = state

    def get_peak_visibility(self):
        return self.peak_visibility

    def set_peak_visibility(self, state):
        self.peak_visibility = state

    def set_xslice_state(self, state):
        self.xslice = state

    def get_xslice_state(self):
        return self.xslice

    def set_yslice_state(self, state):
        self.yslice = state

    def get_yslice_state(self):
        return self.yslice



class Control:
    def depth(self):
        ui.change_depth(ui.current_spectrum)

    def add(self):
        pass


app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setup_ui(MainWindow)

screen = app.primaryScreen()
size = screen.size()

layout = pg.GraphicsLayout()
ax = pg.PlotItem()
layout.addItem(ax)


def main():
    MainWindow.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
