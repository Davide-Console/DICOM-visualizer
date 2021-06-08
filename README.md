# DICOM visualizer

## INFORMAZIONI GENERALI
Interfaccia grafica per la visualizzazione di immagini DICOM in vista sagittale, coronale e assiale.
Consente lo zoom e il pan delle immagini tramite gli slider e i button presenti sotto le immagini, così come la segmentazione manuale tramite la selezione con il mouse dei pixel sulle immagini.

## REQUISITI
Le librerie necessarie sono le seguenti:

* os
* tk == 8.6
* numpy == 1.20.2
* pydicom == 2.1.2
* Pillow == 8.2.0
* scipy == 1.6.2
* opencv-python==4.5.1.48

Per installare le librerie elencate, eseguire il comando:

```
pip install -r requirements.txt
```

## VISUALIZZAZIONE
La dimensione dello schermo del pc potrebbe essere troppo piccola per visualizzare la GUI nella sua interezza.
In tal caso eliminare o commentare la linea 21 di DICOMvisualizer.py
