# LazysApp
Una aplicación básica creada mediante el framework Tkinter, la cual tiene como funcionabilidad la extracción de información y producción de variables básicas de ficheros LAS/LAZ. Toda la informacion generada se registrará en una base de datos del tipo SQLite3.

Las variables que se extraen de estos ficheros LAZ/LAS son:
- __Nombre del fichero__ al que pertenecen las variables
- Nº de Retornos totales
- Puntos clasificados como _Suelo_:
  -  Ptos. Suelo de 1º Retorno
  -  Ptos. Suelo de 2º Retorno
  -  Ptos. Suelo de 3º Retorno
- Altitud Máxima
- Altitud Mínima

#### La aplicación ha sido diseñada en base a los ficheros LiDAR del IGN (_Instituto Geográfico Nacional_) y la clasificación de puntos es según ASPRS (_American Society for Photogrammetry and Remote Sensing_).
