"""Execució implícita quan s'inicialitza la consola Python de QGIS"""
from qgis.core import *
import qgis.utils


# En el supòsit que no es treballi a la consola Python de QGIS
import os
from qgis.core import QgsVectorLayer
