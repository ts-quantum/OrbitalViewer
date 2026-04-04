from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
# Wichtig: Dieser Import registriert die 3D-Projektion
from mpl_toolkits.mplot3d import Axes3D
from PyQt5 import QtCore

class MplWidget(QWidget):
    def __init__(self, parent=None):
        super(MplWidget, self).__init__(parent)

        # 1. Figur erstellen
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # 2. 3D-Achsen hinzufügen (projection='3d')
        self.axes = self.figure.add_subplot(111, projection='3d')

        # 3. Toolbar hinzufügen
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setIconSize(QtCore.QSize(14, 14))
        
        # 4. Layout
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.axes.axis('off')
