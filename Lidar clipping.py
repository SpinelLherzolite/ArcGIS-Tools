#Clipping script for Weld County, Colorado. This script takes an Area
#of Interest (AOI) and clips a DEM (in this case, lidar) for that area by 
#quadrangle, and then creates a hillshade for that. This logic can be applied
#to work in other Areas of Interest (AOI)
#--------------------- 


#import system modules
#---------------------
import arcpy, os
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension('Spatial')
arcpy.CheckOutExtension('3D')
env.workspace = r'C:\Users\mpalkovic\Documents\ArcGIS\Projects\WeldCoMaps\WeldCoMaps.gdb'
env.overwriteOutput = False
env.addOutputsToMap = False

#definition query
#---------------
aprx = arcpy.mp.ArcGISProject('CURRENT')
m = aprx.listMaps('WeldCo')[0]
for l in m.listLayers():
    if l.name == 'COUNTIES_DOLA_2016':
        l.definitionQuery = """"COUNTY" = 'WELD'"""

#define variables
#----------------
inLidar = r'N:\LIBRARY\Data\GIS data library\LiDAR\Lincoln, Elbert, Arapahoe, Adams, Denver, Morgan, Weld counties composite\Blocks_1_4\total_mosaic.img'
inQuads = 'Quads24k_USDA_python' #SelectLayerByLocation wont accept a file path for an input, must be local to the mxd/aprx project
inCounty = 'COUNTIES_DOLA_2016'
fields = ['quad_name', 'SHAPE@']
arcpy.SelectLayerByLocation_management (inQuads, 'WITHIN', inCounty)

#iterate through each row in a feature class using a search cursor
#-----------------------------------------------------------------
with arcpy.da.SearchCursor (inQuads, fields) as cursor:
    for row in cursor:
        try:
            #outFC = os.path.join(env.workspace, (row[0][:13]))
            outBuff = arcpy.Buffer_analysis(row[1], (row[0][:10]) + '_bf', '1 mile')
            outClip = arcpy.Clip_management(inLidar, '#', (row[0][:9]) + '_dem', outBuff, '#', 'ClippingGeometry', 'NO_MAINTAIN_EXTENT')
            arcpy.HillShade_3d(outClip, (row[0][:10]) + '_hs')
            arcpy.Slope_3d(outClip, (row[0][:10]) + '_sl')
            arcpy.Aspect_3d(outClip, (row[0][:10]) + '_as')
            arcpy.Contour_3d(outClip, (row[0][:10]) + '_ct', 100)
        except:
            print (arcpy.GetMessages())
            pass

#delete the buffered polygons
#----------------------------
dList = [fc for fc in arcpy.ListFeatureClasses() if fc.endswith('bf')]
#print (dList)
for fc in dList:
    arcpy.Delete_management(fc)

#Build pyramids for the rasters
#-------------------------------
pList = arcpy.ListRasters()
print (pList)

for raster in pList:
    try:
        arcpy.BuildPyramids_management(raster)
    except:
        print (arcpy.GetMessages())
        pass   
