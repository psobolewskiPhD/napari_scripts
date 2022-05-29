## Napari scripts
# A collection of [napari](https://napari.org) related tools in various state of disrepair/functionality.

# Browse_LIF_widget.py
## *This functionality is now part of the [napari-aicsimageio plugin](https://github.com/AllenCellModeling/napari-aicsimageio), which supports other file types, as well. Please test it! Note: empty/singleton dimensions may be handled differently, so leave feedback.*

This module can be imported, for example:
```
import napari_scripts.Browse_LIF_widget as BL
```
it then can be used to open Napari with a LIF browser widget:
```
viewer = BL.lif_widget()
```
This Napari viewer will have a empty widget on the right, where you can drag-and-drop a LIF. **Make sure you drop it on the side panel, not the main/middle Napari canvas** Using `aicsimageio`, the widget will import the LIF and prepare a list of scenes. Clicking on a scene should load the chosen scene as an image layer. Note: the Image will have all `MTCZYX` channels, to permit browsing all types of scenes. The returned `viewer` can be used for other manipulations, such listing the selected scenes: `viewer.layers`


# napari_line_profile_widget.py
This is a module that can be imported, for example:
```
import napari_line_profile_widget as linepro
```
and then permits:
```
line_plot = linepro.profile_line(<insert name of napari viewer>) 
```
This will add a shape layer with a red line and widget at the bottom of the Napari window. 
The widget will display a plot of the pixel instensities along the red line, as you move the red line or change z- or t-stack slice.
The top most image layer will be used for the intensity data and the x-axis of the plot should be consistent with any scale data provided to napari. If you close and open a new image, move the line/change slice to update.
You can also get a nice figure (6"x3", 300 dpi) of the current viewer status and the line profile:
```
linepro.get_figure(line_plot, <insert name of napari viewer>)
```
If you don't want the viewer status and just want the plot, pass `screenshot=False`
The figure can be saved, for example as PDF:
```
linepro.get_figure(line_plot, <insert name of napari viewer>, name="test_profile.pdf")
```

# napari_measure_widget.py
This is a module that can be imported, for example:
```
import napari_measure_widget as nmw
```
and then permits:
```
nmw.measure_shape(<insert name of napari viewer>)
```
This will add a shape layer to the napari window and create a widget to display a table of results. By default, the key `m` will be bound to measuring:
- length of lines drawn with `line` or `path` tools
- angle between `path` segments, for the case of a `path` of two segments (3 points)
- area of shapes drawn with `rectangle`, `polygon`, or `ellipse` tools
The last drawn shape will be measured, unless a shape is selected.
The keybind can be changed, by passing a different keybind as a string. For example, to set the keybind to `z`:
```
nm.measure_shape(<insert name of napari viewer>, keybind="z")
```
By default, existing keybinds will *not* be overwritten. To overwrite an existing keybind (for example, if re-opening the widget), you must pass `overwrite=True`.
The measurements will be displayed in a table in the widget. 
Make sure there is an open, visible image layer, so that the measurements can take into account any scale and unit information.
