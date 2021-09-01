import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from skimage import measure
import numpy as np
import napari


def profile_line(viewer):
    def get_image_layer():
        for layer in viewer.layers.selection:
            if isinstance(layer, napari.layers.Image):
                img_layer = layer
        return img_layer

    img_layer = get_image_layer()

    # get img dimensions
    (z, x, y) = img_layer.data.shape

    # draw line in the center 20% of x, y
    line = np.array([[4 * x // 10, 4 * y // 10], [6 * x // 10, 6 * y // 10]])
    line_prof_layer = viewer.add_shapes(
        line, shape_type="line", edge_color="red", name="Line Profile"
    )
    line_prof_layer.mode = "select"

    # get line profile using skimage.measure.profile_line
    def line_profile(img_layer, line_prof_layer):
        slice_nr = viewer.dims.current_step[0]
        slice = img_layer.data[slice_nr]
        if line_prof_layer.data:
            if line_prof_layer.shape_type[-1] == "line":
                linescan = measure.profile_line(
                    slice,
                    line_prof_layer.data[-1][0],
                    line_prof_layer.data[-1][1],
                    mode="reflect",
                )
                return linescan
            else:
                print("no line")
        else:
            print("No data")

    # set params and create mpl figure with subplots
    plt.rcParams.update(
        {
            "font.size": 12,
            "xtick.color": "grey",
            "ytick.color": "grey",
            "axes.edgecolor": "grey",
        }
    )
    mpl_fig = plt.figure()
    ax = mpl_fig.add_subplot(1, 1, 1)

    # add the figure to the viewer as a FigureCanvas widget
    viewer.window.add_dock_widget(FigureCanvas(mpl_fig), area="bottom")

    linescan = line_profile(img_layer, line_prof_layer)
    line_len = np.arange(len(linescan))
    (line,) = ax.plot(linescan)
    axes = plt.gca()
    axes.set_xlim(np.min(line_len), np.max(line_len))
    axes.set_ylim(0, np.max(linescan) * (1.15))
    line.figure.canvas.draw()

    # connect a callback that updates the line plot via mouse drag
    @line_prof_layer.mouse_drag_callbacks.append
    def profile_lines_drag(shapes_layer, event):
        yield
        while event.type == "mouse_move":
            try:
                linescan = line_profile(img_layer, shapes_layer)
                line_len = np.arange(len(linescan))
                line.set_data(line_len, linescan)
                axes.set_xlim(np.min(line_len), np.max(line_len))
                axes.set_ylim(0, np.max(linescan) * (1.15))
                line.figure.canvas.draw_idle()
                yield
            except IndexError:
                pass
            except KeyError:
                pass

    # connect to dimension slider to update on scroll
    @viewer.dims.events.current_step.connect
    def profile_lines_slice(event):
        linescan = line_profile(img_layer, line_prof_layer)
        line_len = np.arange(len(linescan))
        line.set_data(line_len, linescan)
        axes.set_xlim(np.min(line_len), np.max(line_len))
        axes.set_ylim(0, np.max(linescan) * (1.15))
        line.figure.canvas.draw_idle()
