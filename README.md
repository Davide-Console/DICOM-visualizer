# DICOM visualizer

## GENERAL INFORMATION
Graphic User Interface for DICOM images' visualization on sagittal, coronal and axial plane.
The images can be zoomed and moved using slider and buttons. The manual segmentation can be done selecting the pixels directly on the image with the left button of the mouse.

## REQUIREMENTS
The needed libraries are the following:

* os
* tk == 8.6
* numpy == 1.20.2
* pydicom == 2.1.2
* Pillow == 8.3.2
* scipy == 1.6.2
* opencv-python==4.5.1.48

To install these libraries, execute the command:

```
pip install -r requirements.txt
```

## VISUALIZATION
The dimension of the screen could be too small to completely visualize the GUI.
In this case, delete or comment line 21 of DICOMvisualizer.py
