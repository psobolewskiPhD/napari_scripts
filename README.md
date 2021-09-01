## Napari scripts
# A collection of [napari](https://napari.org) related tools in various state of disrepair/functionality.

# napari_line_profile_widget.py
This is a module that can be imported, for example:
```
import napari_line_profile_widget as linep
```
and then permits:
```
linep.profile_line(<insert name of napari viewer>) 
```
This will add a shape layer with a red line and widget at the bottom of the Napari window. 
The widget will display a plot of the pixel instensities along the red line.
