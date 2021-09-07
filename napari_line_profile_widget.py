import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from skimage import measure
import numpy as np
import napari


def profile_line(viewer):
    # get top-most, visible image layer
    def get_image_layer():
        for layer in viewer.layers:
            if isinstance(layer, napari.layers.Image) and layer.visible != 0:
                img_layer = layer
        return img_layer

    img_layer = get_image_layer()

    # get img dimensions
    x = img_layer.data.shape[-1]
    y = img_layer.data.shape[-2]
    # get scale information
    px_size = img_layer.scale[-2:]
    global units
    if viewer.scale_bar.unit is None:
        units = "px"
    elif viewer.scale_bar.unit == "um":
        units = "µm"
    else:
        units = viewer.scale_bar.unit

    # draw line in the center 20% of y, x
    line = np.array([[4 * y // 10, 4 * x // 10], [6 * y // 10, 6 * x // 10]])
    line_prof_layer = viewer.add_shapes(
        line,
        shape_type="line",
        edge_color="red",
        edge_width=4,
        scale=px_size,
        name="Line Profile",
    )
    line_prof_layer.mode = "select"

    # get line profile using skimage.measure.profile_line
    def line_profile(line_prof_layer):
        # get the top most image layer
        top_image = get_image_layer()
        # get scale info
        px_size = top_image.scale[-2:]
        if top_image.data.ndim > 2:
            slice_nr = viewer.dims.current_step[0]
            slice = top_image.data[slice_nr]
        else:
            slice = top_image.data
        if line_prof_layer.data:
            if line_prof_layer.shape_type[-1] == "line":
                linescan = measure.profile_line(
                    slice,
                    line_prof_layer.data[-1][0],
                    line_prof_layer.data[-1][1],
                    mode="reflect",
                )
                return linescan, px_size
            else:
                print("no line")
        else:
            print("No data")

    # set params and create mpl figure with subplots
    plt.rcParams.update(
        {
            "figure.autolayout": True,
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

    linescan, px_size = line_profile(line_prof_layer)
    # define the length of the line using px scale (round to try to avoid length mismatch)
    line_len = np.arange(
        0, round(len(linescan) * round(px_size[-1], 3), 3), round(px_size[-1], 3)
    )
    (line,) = ax.plot(line_len, linescan)
    axes = plt.gca()
    axes.set_xlim(np.min(line_len), np.max(line_len))
    axes.set_ylim(0, np.max(linescan) * (1.15))
    ax.set_xlabel(f"Line length ({units})", color="grey")
    ax.set_ylabel("Intensity (AU)", color="grey")
    plt.tight_layout()
    line.figure.canvas.draw()

    def update_profile(line_prof_layer):
        linescan, px_size = line_profile(line_prof_layer)
        line_len = np.arange(
            0, round(len(linescan) * round(px_size[-1], 3), 3), round(px_size[-1], 3)
        )
        line.set_data(line_len, linescan)
        axes.set_xlim(np.min(line_len), np.max(line_len))
        axes.set_ylim(0, np.max(linescan) * (1.15))
        line.figure.canvas.draw_idle()

    # connect a callback that updates the line plot via mouse drag
    @line_prof_layer.mouse_drag_callbacks.append
    def profile_lines_drag(line_prof_layer, event):
        yield
        while event.type == "mouse_move":
            try:
                update_profile(line_prof_layer)
                yield
            except IndexError:
                pass
            except KeyError:
                pass

    # connect to dimension slider to update on scroll
    @viewer.dims.events.current_step.connect
    def profile_lines_slice(event):
        update_profile(line_prof_layer)

    # refresh on layer move
    @viewer.layers.events.reordered.connect
    def update_layers(event):
        img_layer = get_image_layer()
        img_layer.events.visible.connect(check_vis)
        update_profile(line_prof_layer)

    # refresh on image layer visibility change
    @img_layer.events.visible.connect
    def check_vis(event):
        update_profile(line_prof_layer)

    return line


def get_figure(line, viewer, name=None, screenshot=True):
    if screenshot is True:
        screeny = viewer.screenshot()
        dpi = 300
        width = screeny.shape[1] / dpi
        height = screeny.shape[0] / dpi
        ratio = width / height
        with plt.style.context("default"):
            plt.rcParams.update(
                {
                    "font.family": "sans-serif",
                    "font.sans-serif": "Fira Sans",
                    "font.size": 9,
                }
            )
            fig, ax = plt.subplots(
                2,
                1,
                figsize=(width * 1.12, height * 1.14 * (3.55 + ratio - 0.1) / (3.55)),
                dpi=dpi,
                constrained_layout=True,
                gridspec_kw={"height_ratios": [3.55, ratio - 0.1]},
            )
            ax[0].imshow(screeny)
            ax[0].axis("off")
            ax[0].text(
                -0.15,
                1.02,
                "A",
                transform=ax[0].transAxes,
                fontsize=16,
                fontweight="bold",
                va="top",
            )
            x_data = line.get_xdata()
            y_data = line.get_ydata()
            ax[1].plot(x_data, y_data)
            ax[1].set_xlabel(f"Line length ({units})", loc="right")
            ax[1].set_ylabel("Intensity (AU)")
            ax[1].text(
                -0.15,
                1.075,
                "B",
                transform=ax[1].transAxes,
                fontsize=16,
                fontweight="bold",
                va="top",
            )
            if name is not None:
                fig.savefig(name, dpi=fig.dpi)
            plt.show()
    else:
        with plt.style.context("default"):
            plt.rcParams.update(
                {
                    "figure.autolayout": True,
                    "font.family": "sans-serif",
                    "font.sans-serif": "Fira Sans",
                    "font.size": 10,
                }
            )
            fig = plt.figure(figsize=(6, 3), dpi=300)
            ax = fig.add_subplot(1, 1, 1)
            x_data = line.get_xdata()
            y_data = line.get_ydata()
            ax.plot(x_data, y_data)
            ax.set_xlabel(f"Line length ({units})", loc="right")
            ax.set_ylabel("Intensity (AU)", loc="top")
            if name is not None:
                fig.savefig(name, dpi=fig.dpi)
            plt.show()
