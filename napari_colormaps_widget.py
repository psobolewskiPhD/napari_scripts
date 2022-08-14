# %%
import napari
from qtpy.QtWidgets import QVBoxLayout, QWidget, QTabWidget, QCheckBox, QSpinBox, QLabel, QPushButton, QLineEdit
from napari._qt.layer_controls.qt_colormap_combobox import QtColormapComboBox
from vispy.color import Colormap
from napari.utils.colormaps import SIMPLE_COLORMAPS
from napari.utils.colormaps.colormap_utils import convert_vispy_colormap, ensure_colormap
from magicgui.widgets import create_widget
from skimage import data
from qtpy.QtCore import Qt



# %%
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
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout) 
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # apply_colormaps tab
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
            self._layer_combo.value.colormap = colormap_choices.currentData()

        self.colormapComboBox = colormap_choices

        colormap_choices.currentTextChanged.connect(set_lut)

        # change annotation to napari.layers.Image (e.g) to restrict to just Images
        self._layer_combo = create_widget(annotation=napari.layers.Image)
        # magicgui widgets hold the Qt widget at `widget.native`
        self._apply_colormap_layout.addWidget(self._layer_combo.native)
        self._apply_colormap_layout.addWidget(self.colormapComboBox)
        self._apply_colormap_layout.setAlignment(Qt.AlignTop)

        
        # make colormaps tab
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

        def apply_own_colormap():
            if self.inverted_colormap.isChecked():
                start = [1, 1, 1]
            else:
                start = [0, 0, 0]
            own_colormap = Colormap([start, [self.R_value.value()/255, self.G_value.value()/255, self.B_value.value()/255]])
            self._layer_combo.value.colormap = self.colormap_name.text(), own_colormap
            colormap_choices.addItem(self.colormap_name.text(), own_colormap)

        self.apply_colormap_button.clicked.connect(apply_own_colormap)

# %%
#viewer = napari.Viewer()
# %%
my_widget = CustomWidget()
viewer.window.add_dock_widget(my_widget)

my_widget._layer_combo.reset_choices()
viewer.layers.events.inserted.connect(my_widget._layer_combo.reset_choices)
viewer.layers.events.removed.connect(my_widget._layer_combo.reset_choices)

# %%
napari.run()