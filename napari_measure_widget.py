from __future__ import annotations

import math
from typing import TYPE_CHECKING

import napari
import numpy as np
from magicgui import magicgui

if TYPE_CHECKING:
    import napari.layers
    import napari.types


def measure_shape(
    viewer: napari.Viewer, keybind: str = "m", overwrite: bool = False
) -> None:
    # get top-most, visible image layer
    img_layer = None
    for layer in viewer.layers:
        if isinstance(layer, napari.layers.Image) and layer.visible != 0:
            img_layer = layer
    if img_layer is None:
        raise Exception("No image layer found; is needed for scale information")

    # get img dimensions
    px_size = img_layer.scale[-2:]

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

    # prep results table for the table widget
    result_table = {
        "Shape": [],
        f"Length ({units})": [],
        "Angle (°)": [],
        f"Area ({units}\u00b2)": [],
    }

    @viewer.bind_key(keybind, overwrite=overwrite)
    @magicgui(call_button=f"Measure ({keybind})", result_widget=True)
    def measure_prop(viewer: napari.Viewer) -> magicgui.widgets.Table:
        layer = measure_layer
        if layer.data:
            # Check if a shape is selected, if so use that shape
            if layer.selected_data:
                m_shape_vertices = layer.data[[*layer.selected_data][0]]
                m_shape_type = layer.shape_type[[*layer.selected_data][0]]
            else:  # otherwise use the last shape
                m_shape_vertices = layer.data[-1]
                m_shape_type = layer.shape_type[-1]

            if m_shape_type == "line":
                length = math.dist(*m_shape_vertices) * px_size[-1]
                result_table["Shape"].append("Line")
                result_table[f"Length ({units})"].append(round(length))
                result_table["Angle (°)"].append("N/A")
                result_table[f"Area ({units}\u00b2)"].append("N/A")
            elif m_shape_type == "rectangle":
                area = (
                    math.dist(m_shape_vertices[0], m_shape_vertices[1])
                    * math.dist(m_shape_vertices[0], m_shape_vertices[3])
                    * px_size[-1] ** 2
                )
                result_table["Shape"].append("Rectangle")
                result_table[f"Length ({units})"].append("N/A")
                result_table["Angle (°)"].append("N/A")
                result_table[f"Area ({units}\u00b2)"].append(round(area))
            elif m_shape_type == "ellipse":
                area = (
                    math.pi
                    * 0.5
                    * math.dist(m_shape_vertices[0], m_shape_vertices[1])
                    * 0.5
                    * math.dist(m_shape_vertices[0], m_shape_vertices[3])
                ) * px_size[-1] ** 2
                result_table["Shape"].append("Ellipse")
                result_table[f"Area ({units}\u00b2)"].append(round(area))
                result_table[f"Length ({units})"].append("N/A")
                result_table["Angle (°)"].append("N/A")
            elif m_shape_type == "polygon":
                i = np.arange(len(m_shape_vertices))
                area = (
                    0.5
                    * np.abs(
                        np.sum(np.cross(m_shape_vertices[i - 1], m_shape_vertices[i]))
                    )
                    * px_size[-1] ** 2
                )
                result_table["Shape"].append("Polygon")
                result_table[f"Area ({units}\u00b2)"].append(round(area))
                result_table[f"Length ({units})"].append("N/A")
                result_table["Angle (°)"].append("N/A")
            elif m_shape_type == "path":
                length = 0
                for i in range(len(m_shape_vertices) - 1):
                    length += (
                        math.dist(m_shape_vertices[i], m_shape_vertices[i + 1])
                        * px_size[-1]
                    )
                if m_shape_vertices.shape[0] == 3:
                    angle_rad = np.arccos(
                        np.inner(
                            m_shape_vertices[0] - m_shape_vertices[1],
                            m_shape_vertices[2] - m_shape_vertices[1],
                        )
                        / (
                            np.linalg.norm(m_shape_vertices[1] - m_shape_vertices[0])
                            * np.linalg.norm(m_shape_vertices[2] - m_shape_vertices[1])
                        )
                    )
                    angle_deg = np.rad2deg(angle_rad)
                    result_table["Angle (°)"].append(round(angle_deg))
                else:
                    result_table["Angle (°)"].append("N/A")

                result_table["Shape"].append("Path")
                result_table[f"Length ({units})"].append(round(length))
                result_table[f"Area ({units}\u00b2)"].append("N/A")

        return result_table

    widget = measure_prop.show()
    viewer.window.add_dock_widget(widget, name="Measure Shapes", area="bottom")
