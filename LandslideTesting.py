#import system modules + define environmental variables
import arcpy, os
from arcpy import env
env.overwriteOutput = True
env.addOutputsToMap = 0 #Note that env.addOutputsToMap is boolean. 0 = False, 1 = True
env.workspace = r'C:\Users\mpalkovic\Documents\ArcGIS\Default.gdb'
env.scratchWorkspace = r'C:\Users\mpalkovic\Documents\ArcGIS\scratch.gdb'

#define local variables
outPolys = os.path.join (env.workspace, 'BreckLandslidePolys')
inGeo = r'N:\LIBRARY\Archive\PUBLISHED\OF-OPEN-FILE_SERIES\2000s\OF-02-07 Breckenridge\OF-02-07 FINAL FILES\GIS_Data\geol_poly.shp'
inDEM = os.path.join(env.workspace, 'BreckDEM')
lyr = arcpy.MakeFeatureLayer_management(inGeo, outPolys)
fmt = 'DESCRIPTIO'
opTemp = os.path.join (env.workspace, 'Breckintpolys')
county = 'Summit'
ht = 'Landslide Hazard'

#Create a list of potential units that can exhibit landslide hazards here. We'll then make county specific rules below
def geo_units(table, field):
    with arcpy.da.SearchCursor (table, field) as cursor:
        return sorted ({row[0] for row in cursor})
    
geoUnits = geo_units(inGeo, fmt)
#print (geoUnits)
rockList = []
for g in geoUnits:
    if 'Qls' in g: #Quaternary Landslide Deposits
        if 'Qls' not in rockList:
            rockList.append(g)
    if 'Qlsp' in g: #Quaternary Preglacial Landslide Deposits
        if 'Qlsp' not in rockList:
            rockList.append(g)
    if 'Qlso' in g: #Quaternary Old Landslide Deposits
        if 'Qlso' not in rockList:
            rockList.append(g) 
    if 'Qlsr' in g: #Quaternary Recent Landslide Deposits
        if 'Qlsr' not in rockList:
            rockList.append(g)  
    if 'Qlsy' in g: #Quaternary Young Landslide Deposits
        if 'Qlsy' not in rockList:
            rockList.append(g) 
    if 'Qt' in g: #Quaternary Talus Deposits
        if 'Qt' not in rockList:
            rockList.append(g)
    if 'Qta' in g: #Quaternary Talus Deposits
        if 'Qta' not in rockList:
            rockList.append(g)
    if 'PPm' in g: #Pennsylvanian and Permian Maroon Formation
        if 'PPm' not in rockList:
            rockList.append(g)
    if 'Pm' in g: #Pennsylvanian Minturn Formation
        if 'Pm' not in rockList:
            rockList.append(g)
#print (rockList)

sl = arcpy.Slope_3d (inDEM, os.path.join(env.scratchWorkspace, os.path.basename(inDEM)[:-4] + '_sl'), 'DEGREE') 

if county == 'Summit':
    try:
        if 'PPm' in rockList: #Maroon Formation. This is the codeblock we'll need to modify for each geologic unit, but this is in essence a template of what we need to do for landslide and rockfall hazards.
            index = rockList.index('PPm')
            index_v2 = rockList[index]
            where_clause = "{} = '{}'".format(arcpy.AddFieldDelimiters(lyr, fmt), index_v2)
            queryValue1 = 2 #All values > x degrees after we reclassify the raster
            queryValue2 = 1000 #Most of the erroneous polygons have a small shape area. This filters out the junk
            
            #create a slope map
            #sl = arcpy.Slope_3d (inDEM, os.path.join(env.scratchWorkspace, os.path.basename(inDEM)[:-4] + '_sl'), 'DEGREE')     
            
            #select all of the Maroon Formation Polygons
            slba = arcpy.SelectLayerByAttribute_management (lyr, 'ADD_TO_SELECTION', where_clause)
            
            #clip the raster based on the geology polygons we just selected
            clip = arcpy.Clip_management(sl, '#', opTemp, slba, '#', 'ClippingGeometry')
            
            #convert that raster to integer type
            sl_int = arcpy.Int_3d(clip, os.path.join(env.scratchWorkspace, os.path.basename(inDEM)[:-4] + '_int'))
            
            #reclassify the raster (example: 0-25 degrees, >25 degree slope)
            sl_rc = arcpy.Reclassify_3d(sl_int, 'VALUE', '0 25 1; 25.01 90 2', os.path.join(env.scratchWorkspace, os.path.basename(inDEM)[:-4] + '_rc'))
            ls = arcpy.RasterToPolygon_conversion(sl_rc, os.path.join(env.scratchWorkspace, os.path.basename(inDEM)[:-4] + '_rtp'), 'SIMPLIFY', 'Value')
            
            #export the final polygons
            where_clause2 = "{} = {}".format('gridcode', queryValue1) + ' AND ' + "{} > {}".format('Shape_Area', queryValue2)
            env.addOutputsToMap = 1
            target = arcpy.Select_analysis(ls, os.path.join(env.workspace, os.path.basename(inDEM)[:-4] + '_LandslideHazards'), where_clause2)
            
            arcpy.AddField_management (target, 'fmt', 'TEXT')
            arcpy.AddField_management (target, 'Hazard_Type', 'TEXT')
            fields = ['fmt', 'Hazard_Type']
            with arcpy.da.UpdateCursor (target, fields) as cursor:
                for row in cursor:
                    row[0] = index_v2
                    row[1] = ht
                    cursor.updateRow(row)
            del cursor, row
    except:
        pass

env.addOutputsToMap = 0 
    try:
        if 'Pm' in rockList:
            index = rockList.index('Pm') #Minturn Formation
            index_v2 = rockList[index]
            where_clause = "{} = '{}'".format(arcpy.AddFieldDelimiters(lyr, fmt), index_v2)
            queryValue1 = 2 #All values > x degrees after we reclassify the raster
            queryValue2 = 1000 #Most of the erroneous polygons have a small shape area. This filters out the junk
            
            slba = arcpy.SelectLayerByAttribute_management (lyr, 'ADD_TO_SELECTION', where_clause)
            clip = arcpy.Clip_management(sl, '#', opTemp, slba, '#', 'ClippingGeometry')
            sl_int = arcpy.Int_3d(clip, os.path.join(env.scratchWorkspace, os.path.basename(inDEM)[:-4] + '_int'))
            sl_rc = arcpy.Reclassify_3d(sl_int, 'VALUE', '0 27.5 1; 27.51 90 2', os.path.join(env.scratchWorkspace, os.path.basename(inDEM)[:-4] + '_rc'))
            ls = arcpy.RasterToPolygon_conversion(sl_rc, os.path.join(env.scratchWorkspace, os.path.basename(inDEM)[:-4] + '_rtp'), 'SIMPLIFY', 'Value')
            
            #export the final polygons
            where_clause2 = "{} = {}".format('gridcode', queryValue1) + ' AND ' + "{} > {}".format('Shape_Area', queryValue2)
            append = arcpy.Select_analysis(ls, os.path.join(env.workspace, os.path.basename(inDEM)[:-4] + index_v2 + '_LandslideHazards'), where_clause2)
            arcpy.Append_management(append, target, 'NO_TEST')
            
            fields = ['fmt', 'Hazard_Type']
            with arcpy.da.UpdateCursor(target, fields) as cursor:
                for row in cursor:
                    if (row[0] == None):
                        row[0] = index_v2
                        row[1] = ht
                    cursor.updateRow(row)
            del cursor, row
            
    except:
        pass