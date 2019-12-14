import arcpy

class Toolbox(object):
    def __init__(self):
        self.label = "Remodelar Lotes"
        self.alias = ""

        self.tools = [Manzanas_Tipo1, Manzanas_Tipo2, Manzanas_Tipo3_A, Manzanas_Tipo3_B]

def order_by_length(val):
    return val.length

def order_by_area(val):
    return val.area

class Manzanas_Tipo1(object):
    def __init__(self):
        self.label = "Manzanas tipo 1"
        self.description = "Tool que remodela los lotes dentro de una manzana de tipo 1"
        self.canRunInBackground = False

    def getParameterInfo(self):
        param_path = arcpy.Parameter(
            displayName="Path de la gdb sobre la que se ejecuta el algoritmo",
            name="path_name",
            datatype="DEType",
            parameterType="Required",
            direction="Input"
        )

        param_L1 = arcpy.Parameter(
            displayName="Numero de lotes en los que dividir la manzana en L1 (a lo largo)",
            name="L1_size",
            datatype="Long",
            parameterType="Required",
            direction="Input"
        )

        param_name_fc_blocks = arcpy.Parameter(
            displayName="Nombre de la capa de Manzanas a analizar",
            name="name_fc_blocks",
            datatype="String",
            parameterType="Required",
            direction="Input"
        )

        param_name_fc_plots = arcpy.Parameter(
            displayName="Nombre de la capa de Lotes a analizar",
            name="name_fc_plots",
            datatype="String",
            parameterType="Required",
            direction="Input"
        )

        params = [param_path, param_L1, param_name_fc_blocks, param_name_fc_plots]
        
        return params

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):

        # Se obtienen los parámetros
        param_L_size = parameters[1].valueAsText
        param_path = parameters[0].valueAsText
        param_name_fc_blocks = parameters[2].valueAsText
        param_name_fc_plots = parameters[3].valueAsText

        arcpy.env.workspace = param_path

        messages.AddMessage("Ruta de la gdb tratada: \t {0}".format(param_path))
        messages.AddMessage("Nombre de la feature class Manzanas analizada: \t {0}".format(param_name_fc_blocks))
        messages.AddMessage("Nombre de la feature class Lotes analizada: \t {0}".format(param_name_fc_plots))

        block_lyr = arcpy.Describe(param_name_fc_blocks)
        selected_block_list = block_lyr.FIDSet.split("; ")

        cont = 0
        blocks_list = ""
        for block in selected_block_list:
            if cont < (len(selected_block_list) - 1):
                blocks_list += "{0},".format(block)
            else:
                blocks_list += "{0}".format(block)
            cont += 1



        if selected_block_list[0] != u'':
            fc_blocks = param_path + "/" + param_name_fc_blocks
            fields = ["SHAPE@"]
            where_clause = """{0} IN ({1})""".format('"OBJECTID"', blocks_list)

            for block in arcpy.da.SearchCursor(fc_blocks, fields, where_clause):
                if block is not None and block[0] is not None and not block[0].isMultipart:
                    for part in block[0]:
                        if part is not None:
                            points_list = []
                            for point in part:
                                if point is not None:
                                    points_list.append(point)

                polylines_list = []
                polylines_list.append(arcpy.Polyline(arcpy.Array([points_list[0], points_list[1]])))
                polylines_list.append(arcpy.Polyline(arcpy.Array([points_list[1], points_list[2]])))
                polylines_list.append(arcpy.Polyline(arcpy.Array([points_list[2], points_list[3]])))
                polylines_list.append(arcpy.Polyline(arcpy.Array([points_list[3], points_list[0]])))

                polylines_list = sorted(polylines_list, key=order_by_length) # menor a mayor
                
                divide_length_C1 = polylines_list[0].length / int(2)
                divide_length_C2 = polylines_list[1].length / int(2)
                divide_length_L1 = polylines_list[2].length / int(param_L_size)
                divide_length_L2 = polylines_list[3].length / int(param_L_size)

                divide_geometries = []
                block_polygon = block[0]

                medium_line = arcpy.Polyline(arcpy.Array([polylines_list[0].positionAlongLine(divide_length_C1).firstPoint, polylines_list[1].positionAlongLine(divide_length_C2).firstPoint]), arcpy.Describe(param_path + "/" + param_name_fc_blocks).spatialReference)

                cursor = arcpy.da.InsertCursor(param_path + "/" + param_name_fc_plots, ["SHAPE@"])
                
                parts_two_divided = []
                
                for x in range(1, int(param_L_size)):
                    divide_polyline = arcpy.Polyline(arcpy.Array([polylines_list[2].positionAlongLine((divide_length_L1 * x)).firstPoint, polylines_list[3].positionAlongLine((polylines_list[3].length - (divide_length_L2 * x))).firstPoint]), arcpy.Describe(param_path + "/" + param_name_fc_blocks).spatialReference)
                    parts_divide = block_polygon.cut(divide_polyline)
                    parts_divide = sorted(parts_divide, key=order_by_area) # menor a mayor
                    block_polygon = parts_divide[1]

                    parts_two_divided = parts_divide[0].cut(medium_line)
                    cursor.insertRow([parts_two_divided[1]])
                    cursor.insertRow([parts_two_divided[0]])

                parts_two_divided = block_polygon.cut(medium_line)
                cursor.insertRow([parts_two_divided[1]])
                cursor.insertRow([parts_two_divided[0]])

                del cursor
        else:
            messages.addErrorMessage("[ERROR] No se ha seleccionado ninguna manzana")
        
        return


class Manzanas_Tipo2(object):
    def __init__(self):
        self.label = "Manzanas Tipo 2"
        self.description = "Tool que remodela los lotes dentro de una manzana de tipo 2"
        self.canRunInBackground = False

    def getParameterInfo(self):
        param_path = arcpy.Parameter(
            displayName="Path de la gdb sobre la que se ejecuta el algoritmo",
            name="path_name",
            datatype="DEType",
            parameterType="Required",
            direction="Input"
        )
        param_L1 = arcpy.Parameter(
            displayName="Numero de lotes en los que dividir la manzana en L1 (a lo largo)",
            name="L1_size",
            datatype="Long",
            parameterType="Required",
            direction="Input"
        )
        param_C1 = arcpy.Parameter(
            displayName="Numero de lotes en los que dividir la manzana en C1 (a lo ancho)",
            name="C1_size",
            datatype="Long",
            parameterType="Required",
            direction="Input"
        )
        param_C2 = arcpy.Parameter(
            displayName="Numero de lotes en los que dividir la manzana en C2 (a lo ancho)",
            name="C2_size",
            datatype="Long",
            parameterType="Required",
            direction="Input"
        )
        param_name_fc_blocks = arcpy.Parameter(
            displayName="Nombre de la capa de Manzanas a analizar",
            name="name_fc_blocks",
            datatype="String",
            parameterType="Required",
            direction="Input"
        )

        param_name_fc_plots = arcpy.Parameter(
            displayName="Nombre de la capa de Lotes a analizar",
            name="name_fc_plots",
            datatype="String",
            parameterType="Required",
            direction="Input"
        )

        params = [param_path, param_L1, param_C1, param_C2, param_name_fc_blocks, param_name_fc_plots]
        
        return params

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):

        if parameters[1].altered:
            if int(parameters[1].value) < 1:
                parameters[1].setErrorMessage("El valor debe ser superior a 0.")

        if parameters[2].altered:
            if int(parameters[2].value) < 1:
                parameters[2].setErrorMessage("El valor debe ser superior a 0.")

        if parameters[3].altered:
            if int(parameters[3].value) < 1:
                parameters[3].setErrorMessage("El valor debe ser superior a 0.")

        return

    def execute(self, parameters, messages):
        
        # Se obtienen los parámetros
        param_path = parameters[0].valueAsText
        param_L_size = parameters[1].valueAsText
        param_C1_size = parameters[2].valueAsText
        param_C2_size = parameters[3].valueAsText
        param_name_fc_blocks = parameters[4].valueAsText
        param_name_fc_plots = parameters[5].valueAsText

        arcpy.env.workspace = param_path

        block_lyr = arcpy.Describe(param_name_fc_blocks)
        selected_block_list = block_lyr.FIDSet.split("; ")

        cont = 0
        blocks_list = ""
        for block in selected_block_list:
            if cont < (len(selected_block_list) - 1):
                blocks_list += "{0},".format(block)
            else:
                blocks_list += "{0}".format(block)
            cont += 1

        if selected_block_list[0] != u'':
            fc_blocks = param_path + "/" + param_name_fc_blocks
            fields = ["SHAPE@"]
            where_clause = """{0} IN ({1})""".format('"OBJECTID"', blocks_list)

            for block in arcpy.da.SearchCursor(fc_blocks, fields, where_clause):
                if block is not None and block[0] is not None and not block[0].isMultipart:
                    for part in block[0]:
                        if part is not None:
                            points_list = []
                            for point in part:
                                if point is not None:
                                    points_list.append(point)

                # Se crea la feature class Líneas
                arcpy.CreateFeatureclass_management("in_memory", "Lineas", "POLYLINE", spatial_reference=arcpy.Describe(param_path + "/" + param_name_fc_blocks).spatialReference)

                cursorLines = arcpy.da.InsertCursor("in_memory" + "/Lineas", ["SHAPE@"])
                cursorLines.insertRow([block[0].boundary()])

                polylines_list = []
                polylines_list.append(arcpy.Polyline(arcpy.Array([points_list[0], points_list[1]])))
                polylines_list.append(arcpy.Polyline(arcpy.Array([points_list[1], points_list[2]])))
                polylines_list.append(arcpy.Polyline(arcpy.Array([points_list[2], points_list[3]])))
                polylines_list.append(arcpy.Polyline(arcpy.Array([points_list[3], points_list[0]])))

                polylines_list = sorted(polylines_list, key=order_by_length) # menor a mayor

                divide_length_C1 = polylines_list[0].length / int(2)
                part_length_C1 = polylines_list[0].length / int(param_C1_size)
                divide_length_C2 = polylines_list[1].length / int(2)
                part_length_C2 = polylines_list[1].length / int(param_C2_size)
                divide_length_L1 = (polylines_list[2].length - (divide_length_C1 + divide_length_C2)) / int(param_L_size)
                divide_length_L2 = (polylines_list[3].length - (divide_length_C1 + divide_length_C2)) / int(param_L_size)

                medium_line = arcpy.Polyline(arcpy.Array([polylines_list[0].positionAlongLine(divide_length_C1).firstPoint, polylines_list[1].positionAlongLine(divide_length_C2).firstPoint]), arcpy.Describe(param_path + "/" + param_name_fc_blocks).spatialReference)
                cut_line = medium_line.segmentAlongLine(
                        divide_length_C1,
                        medium_line.length - divide_length_C2
                )

                cursorLines.insertRow([cut_line])

                divide_polyline = arcpy.Polyline(arcpy.Array([polylines_list[2].positionAlongLine(divide_length_C1).firstPoint, polylines_list[3].positionAlongLine(polylines_list[3].length - divide_length_C1).firstPoint]), arcpy.Describe(param_path + "/" + param_name_fc_blocks).spatialReference)
                
                cursorLines.insertRow([divide_polyline])

                for x in range(1, int(param_C1_size)):
                    divide_polyline = arcpy.Polyline(arcpy.Array([polylines_list[0].positionAlongLine(polylines_list[0].length - (part_length_C1 * x)).firstPoint, polylines_list[1].positionAlongLine(part_length_C2 * x).firstPoint]), arcpy.Describe(param_path + "/" + param_name_fc_blocks).spatialReference, False)
                    cut_line = divide_polyline.segmentAlongLine(
                        0, 
                        divide_length_C1
                    )
                    
                    cursorLines.insertRow([cut_line])

                for x in range(1, int(param_L_size)+1):
                    divide_polyline = arcpy.Polyline(arcpy.Array([polylines_list[2].positionAlongLine(divide_length_C1 + (divide_length_L1 * x)).firstPoint, polylines_list[3].positionAlongLine((polylines_list[3].length - (divide_length_L2 * x)) - divide_length_C1).firstPoint]), arcpy.Describe(param_path + "/" + param_name_fc_blocks).spatialReference)
                    cursorLines.insertRow([divide_polyline])

                for x in range(1, int(param_C2_size)):
                    divide_polyline = arcpy.Polyline(arcpy.Array([polylines_list[1].positionAlongLine(part_length_C2 * x).firstPoint, polylines_list[0].positionAlongLine((polylines_list[0].length - (part_length_C1 * x))).firstPoint]), arcpy.Describe(param_path + "/" + param_name_fc_blocks).spatialReference)
                    cut_line = divide_polyline.segmentAlongLine(
                        0,
                        divide_length_C2
                    )
                    
                    cursorLines.insertRow([cut_line])

                del cursorLines

                arcpy.FeatureToPolygon_management("in_memory" + "/Lineas", "in_memory" + "/Lotess")

                arcpy.Append_management("in_memory" + "/Lotess", param_path + "/" + param_name_fc_plots, "NO_TEST")

                arcpy.Delete_management("in_memory" + "/Lineas")

                arcpy.Delete_management("in_memory" + "/Lotess")
              
        else:
            messages.addErrorMessage("[ERROR] No se ha seleccionado ninguna manzana")

        return


class Manzanas_Tipo3_A(object):
    def __init__(self):
        self.label = "Manzanas Tipo 3_A"
        self.description = "Tool que remodela los lotes dentro de una manzana de tipo 3_A"
        self.canRunInBackground = False

    def getParameterInfo(self):
        param_path = arcpy.Parameter(
            displayName="Path de la gdb sobre la que se ejecuta el algoritmo",
            name="path_name",
            datatype="DEType",
            parameterType="Required",
            direction="Input"
        )
        param_L1 = arcpy.Parameter(
            displayName="Numero de lotes en los que dividir la manzana en L1 (a lo largo)",
            name="L1_size",
            datatype="Long",
            parameterType="Required",
            direction="Input"
        )
        param_C1 = arcpy.Parameter(
            displayName="Numero de lotes en los que dividir la manzana en C1 (a lo ancho)",
            name="C1_size",
            datatype="Long",
            parameterType="Required",
            direction="Input"
        )
        param_name_fc_blocks = arcpy.Parameter(
            displayName="Nombre de la capa de Manzanas a analizar",
            name="name_fc_blocks",
            datatype="String",
            parameterType="Required",
            direction="Input"
        )
        param_name_fc_plots = arcpy.Parameter(
            displayName="Nombre de la capa de Lotes a analizar",
            name="name_fc_plots",
            datatype="String",
            parameterType="Required",
            direction="Input"
        )

        params = [param_path, param_L1, param_C1, param_name_fc_blocks, param_name_fc_plots]
        
        return params

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        if parameters[1].altered:
            if int(parameters[1].value) < 1:
                parameters[1].setErrorMessage("El valor debe ser superior a 0.")

        if parameters[2].altered:
            if int(parameters[2].value) < 1:
                parameters[2].setErrorMessage("El valor debe ser superior a 0.")

        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        
        # Se obtienen los parámetros
        param_path = parameters[0].valueAsText
        param_L_size = parameters[1].valueAsText
        param_C1_size = parameters[2].valueAsText
        param_name_fc_blocks = parameters[3].valueAsText
        param_name_fc_plots = parameters[4].valueAsText

        arcpy.env.workspace = param_path

        block_lyr = arcpy.Describe(param_name_fc_blocks)
        selected_block_list = block_lyr.FIDSet.split("; ")

        cont = 0
        blocks_list = ""
        for block in selected_block_list:
            if cont < (len(selected_block_list) - 1):
                blocks_list += "{0},".format(block)
            else:
                blocks_list += "{0}".format(block)
            cont += 1

        if selected_block_list[0] != u'':
            fc_blocks = param_path + "/" + param_name_fc_blocks
            fields = ["SHAPE@"]
            where_clause = """{0} IN ({1})""".format('"OBJECTID"', blocks_list)

            for block in arcpy.da.SearchCursor(fc_blocks, fields, where_clause):
                if block is not None and block[0] is not None and not block[0].isMultipart:
                    for part in block[0]:
                        if part is not None:
                            points_list = []
                            for point in part:
                                if point is not None:
                                    points_list.append(point)

                # Se crea la feature class Líneas
                arcpy.CreateFeatureclass_management("in_memory", "Lineas", "POLYLINE", spatial_reference=arcpy.Describe(param_path + "/" + param_name_fc_blocks).spatialReference)

                cursorLines = arcpy.da.InsertCursor("in_memory" + "/Lineas", ["SHAPE@"])
                cursorLines.insertRow([block[0].boundary()])

                polylines_list = []
                polylines_list.append(arcpy.Polyline(arcpy.Array([points_list[0], points_list[1]])))
                polylines_list.append(arcpy.Polyline(arcpy.Array([points_list[1], points_list[2]])))
                polylines_list.append(arcpy.Polyline(arcpy.Array([points_list[2], points_list[3]])))
                polylines_list.append(arcpy.Polyline(arcpy.Array([points_list[3], points_list[0]])))

                polylines_list = sorted(polylines_list, key=order_by_length) # menor a mayor

                part_length_C1 = polylines_list[0].length / int(param_C1_size)
                divide_length_C1 = polylines_list[0].length / int(2)
                divide_length_C2 = polylines_list[1].length / int(2)
                part_length_C2 = polylines_list[1].length / int(param_C1_size)
                divide_length_L1 = (polylines_list[2].length - (divide_length_C1)) / int(param_L_size)
                divide_length_L2 = (polylines_list[3].length - (divide_length_C1)) / int(param_L_size)

                medium_line = arcpy.Polyline(arcpy.Array([polylines_list[0].positionAlongLine(divide_length_C1).firstPoint, polylines_list[1].positionAlongLine(divide_length_C2).firstPoint]), arcpy.Describe(param_path + "/" + param_name_fc_blocks).spatialReference)
                cut_line = medium_line.segmentAlongLine(
                        divide_length_C1,
                        medium_line.length
                )

                cursorLines.insertRow([cut_line])

                for x in range(1, int(param_C1_size)):
                    divide_polyline = arcpy.Polyline(arcpy.Array([polylines_list[0].positionAlongLine(polylines_list[0].length - (part_length_C1 * x)).firstPoint, polylines_list[1].positionAlongLine(part_length_C2 * x).firstPoint]), arcpy.Describe(param_path + "/" + param_name_fc_blocks).spatialReference, False)
                    cut_line = divide_polyline.segmentAlongLine(
                        0, 
                        divide_length_C1
                    )
                    
                    cursorLines.insertRow([cut_line])

                for x in range(1, int(param_L_size)+1):
                    divide_polyline = arcpy.Polyline(arcpy.Array([polylines_list[2].positionAlongLine(divide_length_L2 * x).firstPoint, polylines_list[3].positionAlongLine(polylines_list[2].length - (divide_length_L1 * x)).firstPoint]), arcpy.Describe(param_path + "/" + param_name_fc_blocks).spatialReference)
                    cursorLines.insertRow([divide_polyline])

                del cursorLines

                arcpy.FeatureToPolygon_management("in_memory" + "/Lineas", "in_memory" + "/Lotess")

                arcpy.Append_management("in_memory" + "/Lotess", param_path + "/" + param_name_fc_plots, "NO_TEST")

                arcpy.Delete_management("in_memory" + "/Lineas")

                arcpy.Delete_management("in_memory" + "/Lotess")
              
        else:
            messages.addErrorMessage("[ERROR] No se ha seleccionado ninguna manzana")

        return


class Manzanas_Tipo3_B(object):
    def __init__(self):
        self.label = "Manzanas Tipo 3_B"
        self.description = "Tool que remodela los lotes dentro de una manzana de tipo 3_B"
        self.canRunInBackground = False

    def getParameterInfo(self):
        param_path = arcpy.Parameter(
            displayName="Path de la gdb sobre la que se ejecuta el algoritmo",
            name="path_name",
            datatype="DEType",
            parameterType="Required",
            direction="Input"
        )

        param_L1 = arcpy.Parameter(
            displayName="Numero de lotes en los que dividir la manzana en L1 (a lo largo)",
            name="L1_size",
            datatype="Long",
            parameterType="Required",
            direction="Input"
        )

        param_C2 = arcpy.Parameter(
            displayName="Numero de lotes en los que dividir la manzana en C2 (a lo ancho)",
            name="C2_size",
            datatype="Long",
            parameterType="Required",
            direction="Input"
        )
        param_name_fc_blocks = arcpy.Parameter(
            displayName="Nombre de la capa de Manzanas a analizar",
            name="name_fc_blocks",
            datatype="String",
            parameterType="Required",
            direction="Input"
        )
        param_name_fc_plots = arcpy.Parameter(
            displayName="Nombre de la capa de Lotes a analizar",
            name="name_fc_plots",
            datatype="String",
            parameterType="Required",
            direction="Input"
        )

        params = [param_path, param_L1, param_C2, param_name_fc_blocks, param_name_fc_plots]
        
        return params

    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):

        if parameters[1].altered:
            if int(parameters[1].value) < 1:
                parameters[1].setErrorMessage("El valor debe ser superior a 0.")

        if parameters[2].altered:
            if int(parameters[2].value) < 1:
                parameters[2].setErrorMessage("El valor debe ser superior a 0.")

        return

    def execute(self, parameters, messages):
        
        # Se obtienen los parámetros
        param_path = parameters[0].valueAsText
        param_L_size = parameters[1].valueAsText
        param_C1_size = parameters[2].valueAsText
        param_name_fc_blocks = parameters[3].valueAsText
        param_name_fc_plots = parameters[4].valueAsText

        arcpy.env.workspace = param_path

        block_lyr = arcpy.Describe(param_name_fc_blocks)
        selected_block_list = block_lyr.FIDSet.split("; ")

        cont = 0
        blocks_list = ""
        for block in selected_block_list:
            if cont < (len(selected_block_list) - 1):
                blocks_list += "{0},".format(block)
            else:
                blocks_list += "{0}".format(block)
            cont += 1

        if selected_block_list[0] != u'':
            fc_blocks = param_path + "/" + param_name_fc_blocks
            fields = ["SHAPE@"]
            where_clause = """{0} IN ({1})""".format('"OBJECTID"', blocks_list)

            for block in arcpy.da.SearchCursor(fc_blocks, fields, where_clause):
                if block is not None and block[0] is not None and not block[0].isMultipart:
                    for part in block[0]:
                        if part is not None:
                            points_list = []
                            for point in part:
                                if point is not None:
                                    points_list.append(point)

                # Se crea la feature class Líneas
                arcpy.CreateFeatureclass_management("in_memory", "Lineas", "POLYLINE", spatial_reference=arcpy.Describe(param_path + "/" + param_name_fc_blocks).spatialReference)

                cursorLines = arcpy.da.InsertCursor("in_memory" + "/Lineas", ["SHAPE@"])
                cursorLines.insertRow([block[0].boundary()])

                polylines_list = []
                polylines_list.append(arcpy.Polyline(arcpy.Array([points_list[0], points_list[1]])))
                polylines_list.append(arcpy.Polyline(arcpy.Array([points_list[1], points_list[2]])))
                polylines_list.append(arcpy.Polyline(arcpy.Array([points_list[2], points_list[3]])))
                polylines_list.append(arcpy.Polyline(arcpy.Array([points_list[3], points_list[0]])))

                polylines_list = sorted(polylines_list, key=order_by_length) # menor a mayor

                part_length_C1 = polylines_list[0].length / int(param_C2_size)
                divide_length_C1 = polylines_list[0].length / int(2)
                divide_length_C2 = polylines_list[1].length / int(2)
                part_length_C2 = polylines_list[1].length / int(param_C2_size)
                divide_length_L1 = (polylines_list[2].length - (divide_length_C2)) / int(param_L_size)
                divide_length_L2 = (polylines_list[3].length - (divide_length_C2)) / int(param_L_size)

                medium_line = arcpy.Polyline(arcpy.Array([polylines_list[0].positionAlongLine(divide_length_C1).firstPoint, polylines_list[1].positionAlongLine(divide_length_C2).firstPoint]), arcpy.Describe(param_path + "/" + param_name_fc_blocks).spatialReference)
                cut_line = medium_line.segmentAlongLine(
                        0,
                        medium_line.length - divide_length_C2
                )

                cursorLines.insertRow([cut_line])

                for x in range(1, int(param_L_size)+1):
                    divide_polyline = arcpy.Polyline(arcpy.Array([polylines_list[2].positionAlongLine((divide_length_L1 * x)).firstPoint, polylines_list[3].positionAlongLine(polylines_list[3].length - (divide_length_L1 * x)).firstPoint]), arcpy.Describe(param_path + "/" + param_name_fc_blocks).spatialReference)
                    cursorLines.insertRow([divide_polyline])

                for x in range(1, int(param_C2_size)):
                    divide_polyline = arcpy.Polyline(arcpy.Array([polylines_list[1].positionAlongLine(part_length_C2 * x).firstPoint, polylines_list[0].positionAlongLine((polylines_list[0].length - (part_length_C1 * x))).firstPoint]), arcpy.Describe(param_path + "/" + param_name_fc_blocks).spatialReference)
                    cut_line = divide_polyline.segmentAlongLine(
                        0,
                        divide_length_C2
                    )
                    
                    cursorLines.insertRow([cut_line])

                del cursorLines

                arcpy.FeatureToPolygon_management("in_memory" + "/Lineas", "in_memory" + "/Lotess")

                arcpy.Append_management("in_memory" + "/Lotess", param_path + "/" + param_name_fc_plots, "NO_TEST")

                arcpy.Delete_management("in_memory" + "/Lineas")

                arcpy.Delete_management("in_memory" + "/Lotess")
              
        else:
            messages.addErrorMessage("[ERROR] No se ha seleccionado ninguna manzana")

        return


