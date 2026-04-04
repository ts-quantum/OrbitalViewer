from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5 import QtCore

class MplWidget_2d(QWidget):
    def __init__(self, parent=None):
        super(MplWidget_2d, self).__init__(parent)
        
        # 1. Figur und Canvas erstellen
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        # 2. Toolbar erstellen (benötigt den Canvas und das Parent-Widget)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # 3. Layout erstellen und Elemente hinzufügen
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.toolbar) # Toolbar oben
        self.layout.addWidget(self.canvas)  # Plot darunter
        self.toolbar.setIconSize(QtCore.QSize(14, 14))
        
        # Achsen für den Zugriff von außen vorbereiten
        self.axes = self.figure.add_subplot(111)
