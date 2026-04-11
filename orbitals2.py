import sys, os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QStyledItemDelegate, QStyle, QFileDialog
from PyQt5.QtGui import QColor, QLinearGradient, QBrush
from PyQt5.QtCore import Qt, QRect, pyqtSignal
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import threading

from modules.custom import plot, plot2, plot_2d_grid, plot_orbital
from modules.custom import plot_hyb_orb, plot_osc, plot_osc_offline, plot_trans, plot_trans_offline
from modules.custom import export_to_pov_mesh2_hyb, export_to_pov_mesh2_orb
from modules.basis import get_psi_num

from modules.window import Ui_MainWindow

"""
macOS:
python3.13 -m nuitka --standalone --macos-create-app-bundle --macos-app-name="OrbitalViewer" --enable-plugin=pyqt5 --enable-plugin=numpy --enable-plugin=matplotlib --enable-plugin=anti-bloat --include-package=modules --include-package-data=modules --nofollow-import-to=pytest --nofollow-import-to=setuptools --jobs=8 --output-dir=dist --remove-output orbitals2.py

"""

class ColormapDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # 1. Draw the standard background (hover/selection highlights)
        painter.save()
        QApplication.style().drawControl(QStyle.CE_ItemViewItem, option, painter)
        
        # 2. Define the layout: Text on left, Gradient on right
        # We split the rect: 40% for text, 60% for the gradient
        rect = option.rect
        text_width = int(rect.width() * 0.4)
         # Define the gradient area (right side)
        grad_rect = QRect(
            int(rect.left() + text_width + 5), 
            int(rect.top() + 2), 
            int(rect.width() - text_width - 10), 
            int(rect.height() - 4)
        )
        
        # 3. Draw the Colormap Name (Text)
        cmap_name = index.data(Qt.DisplayRole)
        painter.drawText(rect.left() + 5, rect.top(), text_width, rect.height(),
                         Qt.AlignVCenter | Qt.AlignLeft, cmap_name)
        
        # 4. Draw the Gradient Example
        try:
            cmap = plt.get_cmap(cmap_name)
            gradient = QLinearGradient(grad_rect.topLeft(), grad_rect.topRight())
            
            # Sample 10 points to create the visual gradient
            for stop in np.linspace(0, 1, 10):
                r, g, b, a = cmap(stop)
                gradient.setColorAt(stop, QColor.fromRgbF(r, g, b, a))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawRect(grad_rect)
        except Exception:
            pass # Fallback if colormap name is invalid
            
        painter.restore()

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    # define Signals for the interaction between different Threads
    # (GUI and background Thread)
    # to control pbar status and to emit error messages to label
    # must be defined on class level
    progress_signal = pyqtSignal(int) # to update pbar
    status_signal = pyqtSignal(str) # for error messages
    progress_signal_osc = pyqtSignal(int)
    status_signal_osc = pyqtSignal(str)
    def __init__(self):
        super(MainWindow, self).__init__()
        # 1. Load ui Files
        self.setupUi(self)
# Transition
        self.play_trans.clicked.connect(self.play_trans_clicked)
        self.stop_trans.clicked.connect(self.stop_trans_clicked)
        self.pause_trans.clicked.connect(self.pause_trans_clicked)
        self.save_trans.clicked.connect(self.save_trans_clicked)
        # connect previously defined signals to procedures
        self.progress_signal.connect(self.pbar_trans.setValue)
        self.progress_signal.connect(self.handle_progress)
        self.status_signal.connect(self.label_save_trans.setText)
# Oscillation
        self.colorBox_osc.setItemDelegate(ColormapDelegate())
        colors=['PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu',
                      'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',
                      'berlin', 'managua', 'vanimo']
        self.colorBox_osc.addItems(colors)
        self.color_osc='PiYG'
        self.colorBox_osc.currentTextChanged.connect(self.color_osc_changed)
        self.play_osc.clicked.connect(self.play_osc_clicked)
        self.stop_osc.clicked.connect(self.stop_osc_clicked)
        self.pause_osc.clicked.connect(self.pause_osc_clicked)
        self.save_osc.clicked.connect(self.save_osc_clicked)
        # connect previously defined signals to procedures
        self.progress_signal_osc.connect(self.pbar_osc.setValue)
        self.progress_signal_osc.connect(self.handle_progress_osc)
        self.status_signal_osc.connect(self.label_save_osc.setText)
# Hybridization
        hyb=["sp", "sp2", "sp3", "dsp2", "sd3", "d2sp3", "sp3d", "sp3d3"]
        self.Select_Hyb.addItems(hyb)
        self.init_3d_orb_plt(self.hyb_widget,self.hyb_widget.axes)
        self.Plot_Hyb.clicked.connect(self.plt_hyb_clicked)
        self.hyb_widget_2.canvas.mpl_connect('button_press_event', self.on_sub_hyb_click)
        self.hyb_export.clicked.connect(self.hyb_export_clicked)
        fig2=self.hyb_widget_2.figure
        fig2.clf()
# Orbitals
        self.init_3d_orb_plt(self.orbital_widget, self.orbital_widget.axes)
        self.Plot_Orbital.clicked.connect(self.plt_orb_clicked)
        self.Export_Orbital.clicked.connect(self.export_orb_clicked)
# Spherical Harmonics 
        # 2. Set up initial parameters
        self.colorBox.setItemDelegate(ColormapDelegate())
        colors=['PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu',
                      'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',
                      'berlin', 'managua', 'vanimo']
        self.colorBox.addItems(colors)
        global color, l, m
        color='PiYG'
        l=0
        m=0
        plot(self.plot_widget,self.plot_widget.axes,l,m,color)
        plot2(self.plot_widget2,self.plot_widget2.axes, l,m,color)
        fig=self.plot_widget3.figure
        fig.clf()
        # 3. define events
        self.colorBox.currentTextChanged.connect(self.color_changed)
        self.plotButton.clicked.connect(self.plot_clicked)
        self.Input_m.textChanged.connect(self.m_changed)
        self.Input_l.textChanged.connect(self.l_changed)
        self.plot_widget3.canvas.mpl_connect('button_press_event', self.on_subplot_click)

# 4. define procedures
# Transition
    def play_trans_clicked(self):
        N = int(self.Edit_frames_trans.text())
        T=float(self.Edit_Time_trans.text())
        n_points=int(self.Edit_Points_trans.text())
        n1=int(self.Edit_n1.text())
        n2=int(self.Edit_n2.text())
        l1=int(self.Edit_l1.text())
        l2=int(self.Edit_l2.text())
        m1=int(self.Edit_m1.text())
        m2=int(self.Edit_m2.text())
        self.ani=plot_trans(self.pbar_image_trans,self.trans_widget, self.trans_widget.axes, n1, l1, m1, n2, l2, m2, n_points, N, T)
        self.ani._is_running = True 
        self.pause_trans.setText('Pause')

    def stop_trans_clicked(self):
        if hasattr(self,'ani') and self.ani is not None:
            self.ani.event_source.stop()
    
    def pause_trans_clicked(self):
        # Query internal status of the event_source
        if self.ani._is_running:
            # Animation is running -> pause
            self.ani.pause()
            self.ani._is_running = False
            self.pause_trans.setText('Resume')
        else:
            # Animation is paused -> play
            self.ani.resume()
            self.ani._is_running = True
            self.pause_trans.setText('Pause')

    def handle_progress(self, value):
        if value == -1:  # "Thread finished" Signal
            self.pbar_trans.setValue(0)
            self.label_save_trans.setText("Export completed. Resuming...")
        
        # Re-start Animation safely
            if hasattr(self, 'ani') and self.ani is not None:
                self.trans_widget.canvas.setVisible(True)
                self.ani.event_source.start() 
                self.trans_widget.canvas.draw_idle()
            else:
                self.pbar_trans.setValue(value)
    
    def run_safe_export(self, fname, Type, p):
        try:
            self.status_signal.emit("Exporting (isolated)...")
        
            # create new matplotlib figure without GUI connection
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_agg import FigureCanvasAgg
        
            # new, invisible figure
            export_fig = Figure(figsize=(8, 6), dpi=150)
            canvas = FigureCanvasAgg(export_fig)
            ax = export_fig.add_subplot(111, projection='3d')

            # Initialize new animation using existing functions
            # (calculate_psi and add_iso_surface must be available in the module)
            export_ani = plot_trans_offline(export_fig, ax , p)
            
            def cb(curr, tot):
                self.progress_signal.emit(int((curr/tot)*100))
            match Type:
                case '.mp4':
                    export_ani.save(fname, writer='ffmpeg', fps=25, progress_callback=cb)
                case '.gif':
                    export_ani.save(fname, writer='pillow', fps=25, progress_callback=cb)
                case _:
                    e='wrong video format'
                    self.status_signal.emit(f"Error: {e}")
            self.status_signal.emit("Export completed")
        except Exception as e:
            self.status_signal.emit(f"Error: {e}")
        finally:
            self.progress_signal.emit(-1)

    def save_trans_clicked(self):
        path, filter = QFileDialog.getSaveFileName(
                    None, 
                    "Export as mp4 or gif", 
                    f'video', 
                    "MP4 Video (*.mp4);; GIF File (*.gif)"
                    )
        if path:
            Type=os.path.splitext(os.path.basename(path))[1]
            if hasattr(self, 'ani') and self.ani is not None:
                # 1. Pause Animation 
                self.ani.event_source.stop()
                # 2. Collect data
                params = {
                    'N' : int(self.Edit_frames_trans.text()),
                    'T' : int(self.Edit_Time_trans.text()),
                    'n_points' : int(self.Edit_Points_trans.text()),
                    'n1' : int(self.Edit_n1.text()),
                    'n2' : int(self.Edit_n2.text()),
                    'l1' : int(self.Edit_l1.text()),
                    'l2':  int(self.Edit_l2.text()),
                    'm1' : int(self.Edit_m1.text()),
                    'm2':  int(self.Edit_m2.text()),
                }

                # 3. Start Thread
                export_thread = threading.Thread(target=self.run_safe_export, 
                                             args=(path, Type, params,))
                export_thread.daemon = True
                export_thread.start()

# Oscillation
    def color_osc_changed(self,value):
        self.color_osc=value
 
    def play_osc_clicked(self):
        N = int(self.Edit_frames_osc.text())
        T=float(self.Edit_Time_osc.text())
        n_points=int(self.Edit_Points_osc.text())
        n=int(self.Edit_n_osc.text())
        l=int(self.Edit_l_osc.text())
        m=int(self.Edit_m_osc.text())
        self.ani2=plot_osc(self.pbar_image_osc,self.osc_widget,self.color_osc, n, l, m, n_points, N, T)
        self.ani2._is_running = True 
        self.pause_osc.setText('Pause')

    def stop_osc_clicked(self):
        if hasattr(self,'ani2') and self.ani2 is not None:
            self.ani2.event_source.stop()
    
    def pause_osc_clicked(self):
        # # Query internal status of the event_source
        if self.ani2._is_running:
            # Animation running -> pause
            self.ani2.pause()
            self.ani2._is_running = False
            self.pause_osc.setText('Resume')
        else:
            # Animation paused -> re-start
            self.ani2.resume()
            self.ani2._is_running = True
            self.pause_osc.setText('Pause')

    def handle_progress_osc(self, value):
        if value == -1:  # "Thread finished" Signal
            self.pbar_osc.setValue(0)
            self.label_save_osc.setText("Export completed. Resuming...")
        
        # Re-Start Animation safely
            if hasattr(self, 'ani2') and self.ani2 is not None:
                self.osc_widget.canvas.setVisible(True)
                self.ani2.event_source.start() 
                self.osc_widget.canvas.draw_idle()
            else:
                self.pbar_osc.setValue(value)

    def run_safe_export_osc(self, fname, Type, p):
        try:
            self.status_signal_osc.emit("Exporting (isolated)...")
        
            # create new figure without GUI connection
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_agg import FigureCanvasAgg
        
            # new, invisible figure object
            export_fig = Figure(figsize=(8, 6), dpi=150)
            canvas = FigureCanvasAgg(export_fig)
            ax1 = export_fig.add_subplot(121, projection='3d')
            ax2 = export_fig.add_subplot(122, projection='3d')

            # Initialize new animation using existing functions
            # (calculate_psi and add_iso_surface must be available in the module)
            export_ani = plot_osc_offline(export_fig, ax1, ax2 , p)
            
            def cb(curr, tot):
                self.progress_signal_osc.emit(int((curr/tot)*100))
            match Type:
                case '.mp4':
                    export_ani.save(fname, writer='ffmpeg', fps=25, progress_callback=cb)
                case '.gif':
                    export_ani.save(fname, writer='pillow', fps=25, progress_callback=cb)
                case _:
                    e='wrong video format'
                    self.status_signal_osc.emit(f"Error: {e}")
            self.status_signal_osc.emit("Export completed")
        except Exception as e:
            self.status_signal_osc.emit(f"Error: {e}")
        finally:
            self.progress_signal_osc.emit(-1)

    def save_osc_clicked(self):
        path, filter = QFileDialog.getSaveFileName(
                    None, 
                    "Export as mp4 or gif", 
                    f'video', 
                    "MP4 Video (*.mp4);; GIF File (*.gif)"
                    )
        if path:
            Type=os.path.splitext(os.path.basename(path))[1]
            if hasattr(self, 'ani2') and self.ani2 is not None:
                # 1. Pause Animation 
                self.ani2.event_source.stop()
                # 2. Collect data
                params = {
                    'N' : int(self.Edit_frames_osc.text()),
                    'T' : int(self.Edit_Time_osc.text()),
                    'n_points' : int(self.Edit_Points_osc.text()),
                    'color' : self.color_osc,
                    'n' : int(self.Edit_n_osc.text()),
                    'l' : int(self.Edit_l_osc.text()),
                    'm':  int(self.Edit_m_osc.text()),
                }

                # 3. Start Thread
                export_thread = threading.Thread(target=self.run_safe_export_osc, 
                                             args=(path, Type, params,))
                export_thread.daemon = True
                export_thread.start()

# Hybridization
    def plt_hyb_clicked(self):
        global hyb, N, psi_v_num, limit
        hyb=self.Select_Hyb.currentText()
        N=int(self.Edit_N.text())

        psi_v_num = get_psi_num(hyb,N) #from basis.py
        plot_hyb_orb(self.hyb_widget, self.hyb_widget.axes, hyb,N,psi_v_num[0],title=r'hybrid type: ' + hyb)
        
        fig=self.hyb_widget_2.figure
        fig.clf()
        for j in range(len(psi_v_num)):
            n=len(fig.axes)+1
            gs=GridSpec(1,n,figure=plt.figure)
            for i, ax in enumerate(fig.axes):
                ax.set_subplotspec(gs[i])
                ax.set_position(gs[i].get_position(fig))
            new_ax=fig.add_subplot(gs[n-1],projection='3d')
            plot_hyb_orb(self.hyb_widget_2, new_ax, hyb,N,psi_v_num[j],title=j)                
        fig.canvas.draw()
    
    def on_sub_hyb_click(self, event):
        global hyb, N, psi_v_num, limit
        fig=self.hyb_widget_2.figure
        # Check if a subplot was clicked at all
        if event.inaxes is not None:
            clicked_ax = event.inaxes        
        # Option B: Find index within a list of axes
        # (Useful for many automated subplots)
            try:
                index = list(fig.axes).index(clicked_ax)
                plot_hyb_orb(self.hyb_widget, self.hyb_widget.axes, hyb,N,psi_v_num[index],title=r'hybrid type: ' + hyb)
            except ValueError:
                pass
    
    def hyb_export_clicked(self):
        global psi_v_num
        hyb=self.Select_Hyb.currentText()
        # Full signature: getSaveFileName(parent, caption, directory, filter)
        path, filter = QFileDialog.getSaveFileName(
                    None, 
                    "Export Orbital as PovRay Include File", 
                    f'{hyb}_hybrid', 
                    "Include Files (*.inc);;All Files (*)"
                    )
        if path and len(psi_v_num>0):
            n_points=int(self.Edit_N.text())
            fname=os.path.splitext(os.path.basename(path))[0]
            export_to_pov_mesh2_hyb(path, fname, psi_v_num, hyb, n_points)

    def init_3d_orb_plt(self,widget,ax):
        ax.clear()
        ax_lim=10
        ax.plot([-ax_lim, ax_lim], [0,0], [0,0], c='0.5', lw=1, zorder=10)
        ax.plot([0,0], [-ax_lim, ax_lim], [0,0], c='0.5', lw=1, zorder=10)
        ax.plot([0,0], [0,0], [-ax_lim, ax_lim], c='0.5', lw=1, zorder=10)
        ax.set_xlim(-ax_lim, ax_lim)
        ax.set_ylim(-ax_lim, ax_lim)
        ax.set_zlim(-ax_lim, ax_lim)
        ax.text(ax_lim,0,0,'x',color='blue', fontsize=10)
        ax.text(0,ax_lim,0,'y',color='blue', fontsize=10)
        ax.text(0,0,ax_lim,'z',color='blue', fontsize=10)
        ax.axis('off')
        widget.canvas.draw()
    
# Orbitals
    def plt_orb_clicked(self):
        global n, l, m
        n=int(self.Edit_n.text())
        l=int(self.Edit_l.text())
        m=int(self.Edit_m.text())
        N=int(self.Edit_Points.text())
        global psi_orb, threshold
        wedge=self.checkBox_wedge.isChecked()
        psi_orb, threshold=plot_orbital(self.orbital_widget, self.orbital_widget.axes, n,l,m,N, wedge)
        plot_2d_grid(self.orbital_widget_2d,n,l,m)

    def export_orb_clicked(self):
        global psi_orb, threshold, n, l, m
        # Full signature: getSaveFileName(parent, caption, directory, filter)
        path, filter = QFileDialog.getSaveFileName(
                    None, 
                    "Export Orbital as PovRay Include File", 
                    f'Psi_{n}_{l}_{m}', 
                    "Include Files (*.inc);;All Files (*)"
                    )
        if path and len(psi_orb>0):
            limit=n**2 * 3
            n_points=int(self.Edit_Points.text())
            fname=os.path.splitext(os.path.basename(path))[0]
            export_to_pov_mesh2_orb(path, fname, psi_orb, threshold,limit, n_points)
 
# Spherical Harmonics
    def show_warning_messagebox(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        # setting message for Message Box
        msg.setText("Check Parameters: abs(m) <= l !!")
        # setting Message box window title
        msg.setWindowTitle("Warning")
        # declaring buttons on Message Box
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        # start the app
        retval = msg.exec_()

    def update_plot3(self):
        global color, l, m
        fig=self.plot_widget3.figure
        fig.clf()
        for j in range(-l,l+1,1):
            n=len(fig.axes)+1
            gs=GridSpec(1,n,figure=plt.figure)
            for i, ax in enumerate(fig.axes):
                ax.set_subplotspec(gs[i])
                ax.set_position(gs[i].get_position(fig))
            new_ax=fig.add_subplot(gs[n-1],projection='3d')                
            plot(self.plot_widget3,new_ax,l,j,color)
        fig.canvas.draw()

    def color_changed(self,value):
        global color, l, m
        m=int(self.Input_m.text())
        l=int(self.Input_l.text())
        color=value
        if (abs(m)<=l): #check for meaningful values
            plot(self.plot_widget,self.plot_widget.axes,l,m,color)
            plot2(self.plot_widget2,self.plot_widget2.axes, l,m,color)
            self.update_plot3()
        else:
            self.show_warning_messagebox()
    
    def m_changed(self,value):
        global l,m
        try:
            if (abs(int(value))>abs(int(self.Input_l.text()))):
                self.Input_m.setStyleSheet("color: red;")
            else:
                m=int(self.Input_m.text())
                self.Input_m.setStyleSheet("color: black;")
        except:
            self.Input_m.setStyleSheet("color: black;")
            return
        
    def l_changed(self,value):
        global l,m
        try:
            if (abs(int(self.Input_m.text()))>int(value)):
                self.Input_m.setStyleSheet("color: red;")
            else:
                self.Input_m.setStyleSheet("color: black;")          
        except:
            return

    def on_subplot_click(self, event):
        global color, l
        fig=self.plot_widget3.figure
        # Check if a subplot was clicked at all
        if event.inaxes is not None:
            clicked_ax = event.inaxes         
        # Option B: Find index within a list of axes
        # (Useful for many automated subplots)
            try:
                index = list(fig.axes).index(clicked_ax)
                m=index-l
                self.Input_m.setText(str(m))
                plot(self.plot_widget,self.plot_widget.axes,l,m,color)
                plot2(self.plot_widget2,self.plot_widget2.axes, l,m,color)
            except ValueError:
                pass

    def plot_clicked(self):
        global l, m, color
        #check if for changed input, do nothing if l and m unchanged
        if (l==int(self.Input_l.text()) and m==int(self.Input_m.text())):
            return
        
        m=int(self.Input_m.text())
        #update plot_widget3 only if l was changed 
        if (l!=int(self.Input_l.text()) ):
            l=int(self.Input_l.text())
            self.update_plot3()

        l=int(self.Input_l.text())

        if (abs(m)<=l):  # check for meaningful values
            plot(self.plot_widget,self.plot_widget.axes,l,m,color)
            plot2(self.plot_widget2,self.plot_widget2.axes, l,m,color)
        else:
            self.show_warning_messagebox()
        
# App-Start
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
