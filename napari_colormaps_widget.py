# %%
import napari
import numpy as np
from pathlib import Path
from qtpy.QtWidgets import (QFileDialog, QVBoxLayout, QWidget, QTabWidget, QCheckBox, QSpinBox, QLabel, QPushButton, QLineEdit)
from qtpy.QtCore import Qt
from napari._qt.layer_controls.qt_colormap_combobox import QtColormapComboBox
from vispy.color import Colormap
from napari.utils.colormaps import Colormap as NpColormap
from napari.utils.colormaps.colormap_utils import convert_vispy_colormap, ensure_colormap
from magicgui.widgets import create_widget
from skimage import data

# %%
# These are vispy implementations of the inverted LUTs by @cleterrier from:
# https://github.com/cleterrier/ChrisLUTs
ColormapDict = {
    "I_Forest": Colormap([[1, 1, 1], [0, 0.6, 0]]),
    "I_Blue": Colormap([[1, 1, 1], [0, 0, 1]]),
    "I_Bordeaux": Colormap([[1, 1, 1], [0.8, 0, 0.2]]),
    "I_Cyan": Colormap([[1, 1, 1], [0, 1, 1]]),
    "I_Green": Colormap([[1, 1, 1], [0, 1, 0]]),
    "I_Magenta": Colormap([[1, 1, 1], [1, 0, 1]]),
    "I_Purple": Colormap([[1, 1, 1], [0.8, 0, 0.8]]),
    "I_Red": Colormap([[1, 1, 1], [1, 0, 0]]),
    "I_Yellow": Colormap([[1, 1, 1], [1, 1, 0]]),
}
NapariColormaps = {
    name: ensure_colormap(convert_vispy_colormap(colormap, name=name))
    for name, colormap in ColormapDict.items()
}
# %%
viewer = napari.Viewer()
viewer.add_image(data.cells3d()[:,1,:])
# %%
class CustomWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.viewer = napari.current_viewer()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout) 
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Make a tab to apply ChrisLUTs
        self.apply_colormap = QWidget()
        self._apply_colormap_layout = QVBoxLayout()
        self.apply_colormap.setLayout(self._apply_colormap_layout)
        self.tabs.addTab(self.apply_colormap, 'Apply cleterrier inverted LUTs')
        
        colormap_choices = QtColormapComboBox(self)
        colormap_choices.setObjectName("colormapComboBox")
        colormap_choices._allitems = set(NapariColormaps)
        for name, colormap in NapariColormaps.items():
           colormap_choices.addItem(name, colormap)

        def set_lut():
            self.viewer.layers.selection.active.colormap = colormap_choices.currentData()

        self.colormapComboBox = colormap_choices
        colormap_choices.currentTextChanged.connect(set_lut)
        self._apply_colormap_layout.addWidget(self.colormapComboBox)
        self._apply_colormap_layout.setAlignment(Qt.AlignTop)

        
        # make a tab for generating a colormap
        self.make_colormaps = QWidget()
        self._make_colormaps_layout = QVBoxLayout()
        self.make_colormaps.setLayout(self._make_colormaps_layout)
        self.tabs.addTab(self.make_colormaps, 'Add Custom Colormap')
        self._make_colormaps_layout.addWidget(QLabel("Name of colormap:"))
        self.colormap_name = QLineEdit("test")
        self._make_colormaps_layout.addWidget(self.colormap_name)
        self.inverted_colormap = QCheckBox("Inverted")
        self._make_colormaps_layout.addWidget(self.inverted_colormap)
        self._make_colormaps_layout.addWidget(QLabel("R value"))
        self.R_value = QSpinBox()
        self.R_value.setRange(0, 255)
        self._make_colormaps_layout.addWidget(self.R_value)
        self._make_colormaps_layout.setAlignment(Qt.AlignTop)
        self._make_colormaps_layout.addWidget(QLabel("G value"))
        self.G_value = QSpinBox()
        self.G_value.setRange(0, 255)
        self._make_colormaps_layout.addWidget(self.G_value)
        self._make_colormaps_layout.addWidget(QLabel("B value"))
        self.B_value = QSpinBox()
        self.B_value.setRange(0, 255)
        self._make_colormaps_layout.addWidget(self.B_value)
        
        self.apply_colormap_button = QPushButton("Apply Colormap")
        self._make_colormaps_layout.addWidget(self.apply_colormap_button)
        self.apply_colormap_button.clicked.connect(self._apply_own_colormap)


        # make a tab to import and apply an imageJ LUT
        # both ascii and binary .lut files are supported
        self.import_LUT = QWidget()
        self._import_LUT_layout = QVBoxLayout()
        self.import_LUT.setLayout(self._import_LUT_layout)
        self.tabs.addTab(self.import_LUT, 'Import ImageJ LUT')
        self.import_LUT_button = QPushButton("Select LUT to import and apply")
        self._import_LUT_layout.addWidget(self.import_LUT_button)
        self.import_LUT_button.clicked.connect(self._on_click_import_LUT)

    def _apply_own_colormap(self):
            if self.inverted_colormap.isChecked():
                start = [1, 1, 1]
            else:
                start = [0, 0, 0]
            own_colormap = Colormap([start, [self.R_value.value()/255, self.G_value.value()/255, self.B_value.value()/255]])
            self.viewer.layers.selection.active.colormap = self.colormap_name.text(), own_colormap
            
    def _on_click_import_LUT(self):
        self.LUT_file_path = Path(QFileDialog.getOpenFileName(self, "Select ImageJ LUT file")[0])
        # try reading .lut as ascii
        try:
            lut = np.loadtxt(self.LUT_file_path, delimiter="\t", skiprows=1)
            self.viewer.layers.selection.active.colormap = self.LUT_file_path.stem, NpColormap(lut[:,1:4]/255, name=self.LUT_file_path.stem, display_name=self.LUT_file_path.stem)
            return
        except Exception as e:
            pass
        # try reading .lut as binary
        try:
            dtype = np.dtype('B')
            with open(self.LUT_file_path, "rb") as f:
                numpy_data = np.fromfile(f,dtype)
            self.viewer.layers.selection.active.colormap = self.LUT_file_path.stem, NpColormap(numpy_data.reshape(3, 256).T/255, name=self.LUT_file_path.stem, display_name=self.LUT_file_path.stem)
        except IOError:
            print('Error While Opening the file!')   

# %%
colormap_widget = CustomWidget()
viewer.window.add_dock_widget(colormap_widget, area='right', name='Colormap Manager')


# %%
napari.run()