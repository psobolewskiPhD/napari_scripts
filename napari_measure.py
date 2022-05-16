import napari
import math


def measure_shape(keybind="m"):
    viewer = napari.current_viewer()
    # get top-most, visible image layer

    def get_image_layer():
        for layer in viewer.layers:
            if isinstance(layer, napari.layers.Image) and layer.visible != 0:
                img_layer = layer
        return img_layer

    img_layer = get_image_layer()

    # get img dimensions
    px_size = img_layer.scale[-2:]
    global units
    if viewer.scale_bar.unit is None:
        units = "px"
    elif viewer.scale_bar.unit == "um":
        units = "µm"
    else:
        units = viewer.scale_bar.unit

    measure_layer = viewer.add_shapes(
        None,
        edge_color="red",
        edge_width=2,
        scale=px_size,
        name="Measure",
    )
    measure_layer.mode = "add_line"

    @viewer.bind_key(keybind)
    def measure_length(viewer):
        layer = viewer.layers["Measure"]
        if layer.data:
            if layer.shape_type[-1] == "line":
                length = math.dist(*layer.data[-1]) * px_size[-1]
                print(f"Length: {round(length, 1)} {units}")
            elif layer.shape_type[-1] == "rectangle":
                area = (
                    math.dist(layer.data[-1][0], layer.data[-1][1])
                    * math.dist(layer.data[-1][0], layer.data[-1][3])
                    * px_size[-1] ** 2
                )
                print(f"Area: {round(area)} {units}\u00b2")
            elif layer.shape_type[-1] == "ellipse":
                area = (
                    math.pi
                    * 0.5
                    * math.dist(layer.data[-1][0], layer.data[-1][1])
                    * 0.5
                    * math.dist(layer.data[-1][0], layer.data[-1][3])
                ) * px_size[-1] ** 2
                print(f"Area: {round(area)} {units}\u00b2")
            else:
                print("not a line, rectangle, or ellipse")
        else:
            print("no shapes")
