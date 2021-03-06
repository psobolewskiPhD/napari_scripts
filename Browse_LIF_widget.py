# %%
from aicsimageio import AICSImage
from qtpy.QtWidgets import QListWidget
from qtpy.QtCore import Qt, QFileInfo
import napari

# %%
# Make a custom QListWidget that can accept drag and drop
class SceneList(QListWidget):
    # be able to pass the Napari viewer name (viewer)
    def __init__(self, viewer, parent=None):
        super().__init__(parent)
        self.viewer = viewer
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.currentItemChanged.connect(self.open_scene)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            # Check that it's a LIF file
            for url in event.mimeData().urls():
                img_file = str(url.toLocalFile())
                info = QFileInfo(img_file)
                if info.completeSuffix() == "lif":
                    # Load data from LIF using AICSImage
                    img = AICSImage(img_file, reconstruct_mosaic=False)
                    # Make a list of the scenes
                    for scene in img.scenes:
                        self.addItem(scene)
                    self.img = img
                else:
                    print("Not a LIF")
                    event.ignore()
        else:
            event.ignore()

    def open_scene(self):
        item = self.currentItem()
        scene = item.text()
        self.img.set_scene(scene)
        if len(self.img.shape) == 6:
            M = "M"
            if self.img.shape[1] == 1:
                C = ""
            else:
                C = "C"
            if self.img.shape[2] == 1:
                T = ""
            else:
                T = "T"
            if self.img.shape[3] == 1:
                Z = ""
            else:
                Z = "Z"
        else:
            M = ""
            if self.img.shape[0] == 1:
                C = ""
            else:
                C = "C"
            if self.img.shape[1] == 1:
                T = ""
            else:
                T = "T"
            if self.img.shape[2] == 1:
                Z = ""
            else:
                Z = "Z"
        channels = M + C + T + Z + "YX"
        if self.img.physical_pixel_sizes.Z is None:
            scale = [
                self.img.physical_pixel_sizes.Y,
                self.img.physical_pixel_sizes.X,
            ]
        else:
            scale = [
                self.img.physical_pixel_sizes.Z,
                self.img.physical_pixel_sizes.Y,
                self.img.physical_pixel_sizes.X,
            ]
        if self.viewer.theme == "light":
            colormap = "gray_r"
        else:
            colormap = "gray"
        self.viewer.add_image(
            self.img.get_image_dask_data(channels),
            name=scene,
            scale=scale,
            colormap=colormap,
        )
        self.viewer.scale_bar.visible = True


# %%
def lif_widget():
    viewer = napari.Viewer()
    list_widget = SceneList(viewer)
    viewer.window.add_dock_widget(list_widget, area="right", name="LIF Scene Browser")
    return viewer


# %%
