#%%
from aicsimageio import AICSImage
from vispy.color import Colormap
from qtpy.QtWidgets import QListWidget, QAbstractItemView, QListWidgetItem
from qtpy.QtCore import Qt, QUrl, QFileInfo
import napari


#%%
class SceneList(QListWidget):
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

            for url in event.mimeData().urls():
                img_file = str(url.toLocalFile())
                info = QFileInfo(img_file)
                if info.completeSuffix() == "lif":
                    # Load data from LIF into a dask stack
                    img = AICSImage(img_file, reconstruct_mosaic=False)
                    for scene in img.scenes:
                        self.addItem(scene)
                    self.img = img
                else:
                    event.ignore()
        else:
            event.ignore()

    def open_scene(self):
        item = self.currentItem()
        scene = item.text()
        self.img.set_scene(scene)
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
        self.viewer.add_image(
            self.img.get_image_dask_data("MTCZYX"), name=scene, scale=scale
        )
        self.viewer.scale_bar.visible = True


#%%
def lif_widget():
    viewer = napari.Viewer()
    list_widget = SceneList(viewer)
    viewer.window.add_dock_widget([list_widget], area="right")
    return viewer


#%%
