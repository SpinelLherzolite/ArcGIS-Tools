"""
Source Name:   Geologic Hazards Derivative Tools.pyt
Version:       ArcGIS Desktop 10.6
Author:        Martin Palkovic, Colorado Geological Survey
Date:          May 2020
Description:   A python toolbox for generating polygons of various
geologic hazards in Colorado (rockfall, swelling soil, landslides, debris flows, etc.)
"""
#-----------------------------------------------------------------------------

import arcpy, os
from arcpy import env
arcpy.CheckOutExtension('3D')

class Toolbox (object):
    def __init__(self):
        self.label = 'Geohazard Derivative Tools'
        self.alias = 'GDT'

        # List of tool classes associated with this toolbox
        self.tools = [Rockfall, Problematic_Soils, Landslide]  #update this every time I add a new tool


class Rockfall(object):
    """
    Rockfall Hazards Polygon Tool 
    METHOD:
        __init__(): Define tool name and class info
        getParameterInfo(): Define parameter definitions in tool
        isLicensed(): Set whether tool is licensed to execute
        updateParameters():Modify the values and properties of parameters
                           before internal validation is performed
        updateMessages(): Modify the messages created by internal validation
                          for each tool parameter.
        execute(): Runtime script for the tool
    """
    def __init__(self):
        self.label = 'Rockfall Hazards Polygon Tool'
        self.description = 'Creates polygons of rockfall hazards from a high resolution digital elevation model (i.e Lidar)'
        self.canRunInBackground = False

    def getParameterInfo(self):
        #Define parameter definitions
        
        #First Parameter
        param0 = arcpy.Parameter(
            displayName = 'Scratch Workspace',
            name = 'scratch_workspace',
            datatype = 'DEWorkspace',
            parameterType = 'Required',
            direction = 'Input')
        
        #Second Parameter 
        param1 = arcpy.Parameter(
            displayName = 'input DEM',
            name = 'inDEM',
            datatype = 'DERasterDataset',
            parameterType = 'Required',
            direction = 'Input')
        
        
        #Third Parameter
        param2 = arcpy.Parameter(
            displayName = 'Output Rockfall Polygons',
            name = 'rockfall',
            datatype = 'DEFeatureClass',
            parameterType = 'Required',
            direction = 'Output')
        
        
        params = [param0, param1, param2]
        return params

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        
        env.overwriteOutput = True
        env.addOutputsToMap = 0
        #### User defined variables ####
        sW = parameters[0].valueAsText
        inDEM = parameters[1].valueAsText
        outPolys = parameters[2].valueAsText
        queryValue1 = 2 #All values > 30 degrees slope
        queryValue2 = 1000 #Most of the erroneous polygons have a small shape area. This filters out the junk
        
        
        sl = arcpy.Slope_3d (inDEM, sW + '\\' + os.path.basename(inDEM)[:-4] + '_sl', 'DEGREE')
        #ct = arcpy.Contour_3d(inDEM, sW + '\\' + os.path.basename(inDEM)[:-4] + '_ct', 20)
        sl_int = arcpy.Int_3d(sl, sW + '\\' + os.path.basename(inDEM)[:-4] + '_int') 
        sl_int2 = arcpy.Reclassify_3d(sl_int, 'VALUE', '0 30 1; 30.01 90 2', sW + '\\' + os.path.basename(inDEM)[:-4] + '_rc')
        rockfall = arcpy.RasterToPolygon_conversion(sl_int2, outPolys + '_rf', 'SIMPLIFY', 'Value')
        
        where_clause = "{} = {}".format('gridcode', queryValue1) + ' AND ' + "{} > {}".format('Shape_Area', queryValue2)
        env.addOutputsToMap = 1
        arcpy.Select_analysis(rockfall, outPolys + '_final', where_clause)
        
        return

class Problematic_Soils(object):
    def __init__(self):
        self.label = 'Problematic Soils Polygon Tool'
        self.description = 'Creates polygons of Problematic soils from mapped geology in the area of interest'
        self.canRunInBackground = False

    def getParameterInfo(self):
        
        #First Parameter
        param0 = arcpy.Parameter(
            displayName = 'Scratch Workspace',
            name = 'scratch_workspace',
            datatype = 'DEWorkspace',
            parameterType = 'Required',
            direction = 'Input')
        
        #Second Parameter 
        param1 = arcpy.Parameter(
            displayName = 'input Geology',
            name = 'inDEM',
            datatype = 'DEFeatureClass',
            parameterType = 'Required',
            direction = 'Input')
        
        
        #Third Parameter
        param2 = arcpy.Parameter(
            displayName = 'Output Problematic Rock Polygons',
            name = 'problematic_rock',
            datatype = 'DEFeatureClass',
            parameterType = 'Required',
            direction = 'Output')
        
        #Third Parameter
        param3 = arcpy.Parameter(
            displayName = 'Output Problematic Soil Polygons',
            name = 'problematic_soil',
            datatype = 'DEFeatureClass',
            parameterType = 'Required',
            direction = 'Output')
        
        
        params = [param0, param1, param2, param3]
        return params

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        
        env.overwriteOutput = True
        #### User defined variables ####
        sW = parameters[0].valueAsText
        inGeo = parameters[1].valueAsText
        outRock = parameters[2].valueAsText
        outSoil = parameters[3].valueAsText
        fmt = 'FMT'
        outGeo = os.path.join(sW, os.path.basename(inGeo))
        lyr = arcpy.MakeFeatureLayer_management(inGeo, outGeo)
        
        def geo_units(table, field):
            with arcpy.da.SearchCursor (table, field) as cursor:
                return sorted ({row[0] for row in cursor})
        geoUnits = geo_units(inGeo, fmt)
        #print (geoUnits)
        rockList = []
        for g in geoUnits:
            if 'Ta'.lower() in g.lower(): #Paleocene and Upper Cretaceous Animas Formation
                if 'Ta' not in rockList:
                    rockList.append(g)
            if 'Tkda1' in g: #Paleocene and Upper Cretaceous Dawson Formation, Facies Unit 1
                if 'TKda1' not in rockList:
                    rockList.append(g)
            if 'Tkda2' in g: #Paleocene and Upper Cretaceous Dawson Formation, Facies Unit 2
                if 'TKda2' not in rockList:
                    rockList.append(g)
            if 'Tkda3' in g: #Paleocene and Upper Cretaceous Dawson Formation, Facies Unit 3
                if 'TKda3' not in rockList:
                    rockList.append(g)
            if 'Ka' in g: #Paleocene and Upper Cretaceous Animas Formation
                if 'Ka' not in rockList:
                    rockList.append(g)
            if 'Kb' in g: #Cretaceous Benton Group (Synonymous with Kcgg)
                if 'Kb' not in rockList:
                    rockList.append(g)
            if 'Kcgg' in g: #Cretaceous Carlile Shale, Greenhorn Limestone and Graneros Shale
                if 'Kcgg' not in rockList:
                    rockList.append(g)
            if 'Kch' in g: #Cretaceous Cliff House Sandstone
                if 'Kch' not in rockList:
                    rockList.append(g)
            if 'Kk' in g: #Cretaceous Kirtland Formation
                if 'Kk' not in rockList:
                    rockList.append(g)
            if 'Kl' in g: #Cretaceous Mancos Shale
                if 'Kl' not in rockList:
                    rockList.append(g)
            if 'Km' in g: #Cretaceous Mancos Shale
                if 'Km' not in rockList:
                    rockList.append(g)
            if 'Kp' in g: #Cretaceous Pierre Shale
                if 'Kp' not in rockList:
                    rockList.append(g)
            if 'Jm' in g: #Jurassic Morrison Formation
                if 'Km' not in rockList:
                    rockList.append(g)
        for g in rockList:
            where_clause = "{} = '{}'".format(arcpy.AddFieldDelimiters(lyr, fmt), g)
            arcpy.SelectLayerByAttribute_management(lyr, 'ADD_TO_SELECTION', where_clause)
            arcpy.Select_analysis(lyr, outRock)
        arcpy.SelectLayerByAttribute_management(lyr, 'CLEAR_SELECTION')
           
        #print (rockList)
        
        #Add this in when I figure out how...
        # if len(rockList) == 0:
        #     arcpy.AddMessage("{} has no problematic rock".format(inGeo))

        # if len(rockList) >= 1:
        #     for g in rockList:
        #         where_clause = "{} = '{}'".format(arcpy.AddFieldDelimiters(lyr, fmt), g)
        #         arcpy.SelectLayerByAttribute_management(lyr, 'ADD_TO_SELECTION', where_clause) 
        #         arcpy.Select_analysis(lyr, outRock)
        #     arcpy.SelectLayerByAttribute_management(lyr, 'CLEAR_SELECTION')
        
        geoUnits = geo_units(inGeo, fmt)
        #print (geoUnits)
        soilList = []
        for g in geoUnits:
            if 'af' in g: #Artificial fill
                if 'af' not in soilList:
                    soilList.append(g)
            if 'dg' in g: #Disturbed Ground
                if 'dg' not in soilList:
                    soilList.append(g)
            if 'Qacc1' in g: #Alluvium one of Coal Creek
                if 'Qacc1' not in soilList:
                    soilList.append(g)
            if 'Qacc2' in g: #Alluvium two of Coal Creek
                if 'Qacc2' not in soilList:
                    soilList.append(g)
            if 'Qad1' in g: #Alluvium one of Dry Creek
                if 'Qad1' not in soilList:
                    soilList.append(g)
            if 'Qad2' in g: #Alluvium two of Dry Creek
                if 'Qad2' not in soilList:
                    soilList.append(g)
            if 'Qaeo' in g: #Old alluvium of East Creek
                if 'Qaeo' not in soilList:
                    soilList.append(g)
            if 'Qag2' in g: #Alluvium two of the Gunnison River
                if 'Qag2' not in soilList:
                    soilList.append(g)
            if 'Qag3' in g: #Alluvium three of the Gunnison River
                if 'Qag3' not in soilList:
                    soilList.append(g)
            if 'Qamf' in g: #Alluvial mud flow and mud fan deposits 
                if 'Qamf' not in soilList:
                    soilList.append(g)
            if 'Qamfo' in g: #Old alluvial mud flow and mud fan deposits
                if 'Qamfo' not in soilList:
                    soilList.append(g)
            if 'Qau' in g: #Undifferentiated alluvium of the Uncompaghre River
                if 'Qau' not in soilList:
                    soilList.append(g)
            if 'Qau2' in g: #Alluvium two of the Uncompaghre River
                if 'Qau2' not in soilList:
                    soilList.append(g)
            if 'Qau3' in g: #Alluvium three of the Uncompaghre River
                if 'Qau3' not in soilList:
                    soilList.append(g)
            if 'Qau4' in g: #Alluvium four of the Uncompaghre River
                if 'Qau4' not in soilList:
                    soilList.append(g)
            if 'Qau5' in g: #Alluvium five of the Uncompaghre River
                if 'Qau5' not in soilList:
                    soilList.append(g)
            if 'Qc' in g: #Colluvial deposits
                if 'Qc' not in soilList:
                    soilList.append(g)
            if 'Qco' in g: #Old Colluvial deposits
                if 'Qco' not in soilList:
                    soilList.append(g)
            if 'Qf' in g: #Fan deposits
                if 'Qf' not in soilList:
                    soilList.append(g)
            if 'Qfy' in g: #Young Fan deposits
                if 'Qfy' not in soilList:
                    soilList.append(g)
            if 'Qsw' in g: #Young Fan deposits
                if 'Qsw' not in soilList:
                    soilList.append(g)
        for g in soilList:
            where_clause = "{} = '{}'".format(arcpy.AddFieldDelimiters(lyr, fmt), g)
            arcpy.SelectLayerByAttribute_management(lyr, 'ADD_TO_SELECTION', where_clause) 
            arcpy.Select_analysis(lyr, outSoil)
        arcpy.SelectLayerByAttribute_management(lyr, 'CLEAR_SELECTION')
        
        #Add this in when I figure out how...
        # if len(soilList) == 0:
        #     arcpy.AddMessage("{} has no problematic soil".format(inGeo))

        # if len(soilList) >= 1:
        #     for g in soilList:
        #         where_clause = "{} = '{}'".format(arcpy.AddFieldDelimiters(lyr, fmt), g)
        #         arcpy.SelectLayerByAttribute_management(lyr, 'ADD_TO_SELECTION', where_clause) 
        #         arcpy.Select_analysis(lyr, outSoil)
        # arcpy.SelectLayerByAttribute_management(lyr, 'CLEAR_SELECTION')

class Landslide(object):
    def __init__(self):
        self.label = 'Landslide Hazards Polygon Tool'
        self.description = 'Creates polygons of Landslide hazards from mapped geology in the area of interest'
        self.canRunInBackground = False

    def getParameterInfo(self):
        
        #First Parameter
        param0 = arcpy.Parameter(
            displayName = 'Scratch Workspace',
            name = 'scratch_workspace',
            datatype = 'DEWorkspace',
            parameterType = 'Required',
            direction = 'Input')
        
        #Second Parameter 
        param1 = arcpy.Parameter(
            displayName = 'input Geology',
            name = 'inDEM',
            datatype = 'DEFeatureClass',
            parameterType = 'Required',
            direction = 'Input')
        
        
        #Third Parameter
        param2 = arcpy.Parameter(
            displayName = 'Output Landslide Polygons',
            name = 'landslide',
            datatype = 'DEFeatureClass',
            parameterType = 'Required',
            direction = 'Output')
        
        
        params = [param0, param1, param2]
        return params

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        
        #### User defined variables ####
        sW = parameters[0].valueAsText
        inGeo = parameters[1].valueAsText
        outPolys = parameters[2].valueAsText
        fmt = 'FMT'
        outGeo = os.path.join(sW, os.path.basename(inGeo))
        lyr = arcpy.MakeFeatureLayer_management(inGeo, outGeo)
        
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
            #if 'Qc' in g:
                #if 'Qc' not in rockList:
                    #if slope raster > x degrees:
                        #rockList.append(g)
           
        
        for g in rockList:
            where_clause = "{} = '{}'".format(arcpy.AddFieldDelimiters(lyr, fmt), g)
            arcpy.SelectLayerByAttribute_management(lyr, 'ADD_TO_SELECTION', where_clause)   
            
        arcpy.Select_analysis(lyr, outPolys)
        return