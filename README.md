## Napari scripts
# A collection of [napari](https://napari.org) related tools in various state of disrepair/functionality.

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
The widget will display a plot of the pixel instensities along the red line.
You can also get a nice figure (6"x3", 300 dpi) of the current line profile:
```
line_figure = linepro.get_figure(line_plot)
```
Then to save:
```
line_figure.savefig("test_profile.png")
```
