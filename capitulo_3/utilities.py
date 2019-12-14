#!/usr/bin/python
# coding=utf-8

import json
import urllib, urllib2, time, os
import ConfigParser
import arcpy
import arcpy.cartography as arcpyCA
import constants
import datetime
import time
import argparse


def sendRequest(request):
    response = urllib2.urlopen(request)
    readResponse = response.read()
    jsonResponse = json.loads(readResponse)
    return jsonResponse


def getTokenAGOL():
    # Recuperamos usuario y clave del "config.txt"
    configParser = ConfigParser.RawConfigParser()
    configFilePath = r'config.txt'
    configParser.read(configFilePath)

    usr = configParser.get('AGOL', 'usuario')
    pwd = configParser.get('AGOL', 'clave')

    # Pedimos el token a arcgis.com
    url = "https://arcgis.com/sharing/rest/generateToken"
    data = {'username': usr,
            'password': pwd,
            'referer': "https://www.arcgis.com",
            'f': 'json'}
    request = urllib2.Request(url, urllib.urlencode(data))
    jsonResponse = sendRequest(request)
    return jsonResponse['token']


def getUsername():
    configParser = ConfigParser.RawConfigParser()
    configFilePath = r'config.txt'
    configParser.read(configFilePath)

    usr = configParser.get('AGOL', 'usuario')
    return usr


def getPassword():
    configParser = ConfigParser.RawConfigParser()
    configFilePath = r'config.txt'
    configParser.read(configFilePath)

    pwd = configParser.get('AGOL', 'clave')
    return pwd


# TECHNICAL FUNCTIONS
def update_progress_bar(param_iteration, param_total, param_prefix='', param_suffix='Complete', param_length=50, param_fill='=', param_oids=''):
    percent = 100
    filled_length = 100
    if param_total > 0:
        percent = "{0:.1f}".format(100 * (param_iteration / float(param_total)))
        filled_length = int(param_length * param_iteration // param_total)
    progress_bar = param_fill * filled_length + '-' * (param_length - filled_length)
    print('\r%s |%s| %s%% %s \r' % (param_prefix, progress_bar, percent, param_suffix if percent == str(100.0) else param_oids))
# ---


def simplify_blocks_fc_polygons():
    if arcpy.Exists(constants.FC_GENERALIZED_BLOCKS):
        arcpy.Delete_management(constants.FC_GENERALIZED_BLOCKS)
    if arcpy.Exists(constants.FC_GENERALIZED_BLOCKS_PNT):
        arcpy.Delete_management(constants.FC_GENERALIZED_BLOCKS_PNT)

    arcpyCA.SimplifyPolygon(constants.FC_BLOCKS, constants.FC_GENERALIZED_BLOCKS, "POINT_REMOVE", 2)


def order_by_north(val):
    return val.Y


def order_by_distance_to_east(val, pntTo):
    return val.distanceTo(pntTo)


def is_even(arg_num):
    return True if (arg_num % 2 == 0) else False


def order_by_distance(val):
    return val['distance']


# UPDATE UTILITIES
def update_subsector(arg_oido, arg_codsector, arg_codsubsector):
    where_clause = """{0} = {1}""".format("ObjectID", str(arg_oido))
    with arcpy.da.UpdateCursor(constants.FC_SUBSECTORS, ['OID@', 'CODSECTOR', 'CODSUBSECTOR'], where_clause) as cursor:
        for row in cursor:
            if row[0] == arg_oido:
                row[1] = str(arg_codsector).zfill(2)
                row[2] = row[1] + str(arg_codsubsector).zfill(1)
                cursor.updateRow(row)
    del row
    del cursor


def update_block(arg_oido, arg_sector, arg_subsector):
    where_clause = """{0} = {1}""".format("ObjectID", str(arg_oido))
    with arcpy.da.UpdateCursor(constants.FC_BLOCKS, ['OID@', 'CODSECTOR', 'CODSUBSECTOR'], where_clause) as cursor:
        for row in cursor:
            if row[0] == arg_oido:
                row[1] = str(arg_sector).zfill(2)
                row[2] = str(arg_subsector).zfill(3)
                cursor.updateRow(row)
    del row
    del cursor


def update_plot(arg_oido, arg_sector, arg_subsector, arg_block, arg_plot):
    where_clause = """{0} = {1}""".format("ObjectID", str(arg_oido))
    with arcpy.da.UpdateCursor(constants.FC_PLOTS, ['OID@', 'CODSECTOR', 'CODSUBSECTOR', 'CODMANZANA',
                                                    'CODLOTE', 'NUMLOTE'], where_clause) as cursor:
        for row in cursor:
            row[1] = arg_sector
            row[2] = arg_subsector
            row[3] = arg_block
            row[4] = arg_plot
            if len(arg_plot) > 3:
                row[5] = arg_plot[-4:]
            cursor.updateRow(row)
        del row
        del cursor


def update_corner(arg_oido, arg_shape):
    edit = arcpy.da.Editor(constants.FC_PATH_TECHNICAL_CARD)
    edit.startEditing(False, True)
    edit.startOperation()

    where_clause = """{0} = {1}""".format("ObjectID", str(arg_oido))
    with arcpy.da.UpdateCursor(constants.FC_TECHNICAL_CARD, ['OID@', 'SHAPE@'], where_clause) as cursor:
        for row in cursor:
            if row[0] == arg_oido:
                row[1] = arg_shape
                cursor.updateRow(row)
    del row
    del cursor
    edit.stopOperation()
    edit.stopEditing(True)


# INSERT UTILITIES
def insert_ereference(shape, manzana, esquina, tipo):

    cursor = arcpy.da.InsertCursor(constants.FC_EREFERENCE, ['SHAPE@', 'MANZANA', 'TIPO', 'ESQUINA'])

    cursor.insertRow((shape, manzana, tipo, esquina))

    del cursor


# ARGUMENTS UTILITY
def init_arguments(param_bool_sector=True, param_bool_subsector=True, param_bool_block=True, param_description=None):
    parser = argparse.ArgumentParser(param_description)
    if param_bool_sector:
        parser.add_argument(
            "-s",
            required=False,
            help="Sector o lista de sectores sobre el que se ejecuta el script. Ej: --s '10', '2'",
            type=str,
            action='store'
            )
    if param_bool_subsector:
        parser.add_argument(
            "-sb",
            required=False,
            help="Subsector o lista de subsectores sobre el que se ejecuta el script. Ej: --sb '1', '2'",
            type=str,
            action='store'
        )
    if param_bool_block:
        parser.add_argument(
            "-b",
            required=False,
            help="Manzana o lista de manzanas sobre la que se ejecuta el script. Ej: --b '101', '102', '103'",
            type=str,
            action='store'
            )
    return parser


def get_arguments_filter(param_sector=None, param_subsector=None, param_block=None, param_sector_name="CODSECTOR", param_subsector_name="CODSUBSECTOR", param_block_name="CODMANZANA"):
    if param_sector is not None:
        where_clause = """{0} IN ({1})""".format(param_sector_name, str(param_sector))
        if param_subsector is not None:
            where_clause += """ and {0} IN ({1})""".format(param_subsector_name, str(param_subsector))
            if param_block is not None:
                where_clause += """ and {0} IN ({1})""".format(param_block_name, str(param_block))
        elif param_block is not None:
            where_clause += """ and {0} IN ({1})""".format(param_block_name, str(param_block))

    elif param_subsector is not None:
        where_clause = """{0} IN ({1})""".format(param_subsector_name, str(param_subsector))
        if param_block is not None:
            where_clause += """ and {0} IN ({1})""".format(param_block_name, str(param_block))

    elif param_block is not None:
        where_clause = """{0} IN ({1})""".format(param_block_name, str(param_block))

    else:
        where_clause = None
    return where_clause
# ---


def add_field(param_feature_class, param_name, param_type, param_precision, param_description):
    if not (len(arcpy.ListFields(param_feature_class, param_name)) > 0):
        arcpy.AddField_management(param_feature_class, param_name, param_type, param_precision, "", "", param_description, "NULLABLE")
    else:
        log("Ya existe el campo {0}, no se crea.".format(param_name))


def create_feature_class(arg_feature_class, arg_name, arg_figure_type, arg_spatial_reference, arg_args):
    if arcpy.Exists(arg_feature_class):
        if arg_args.s is not None:
            where_clause = """{0} IN ({1})""".format("CODSECTOR", str(arg_args.s))
            with arcpy.da.UpdateCursor(constants.FC_CORNERS, ['CODSECTOR'], where_clause) as cursor:
                for row in cursor:
                    cursor.deleteRow()
            del cursor
        elif arg_args.sb is not None:
            where_clause = """{0} IN ({1})""".format("CODSUBSECTOR", str(arg_args.sb))
            with arcpy.da.UpdateCursor(constants.FC_CORNERS, ['CODSUBSECTOR'], where_clause) as cursor:
                for row in cursor:
                    cursor.deleteRow()
            del cursor
        elif arg_args.b is not None:
            where_clause = """{0} IN ({1})""".format("CODMANZANA", str(arg_args.b))
            with arcpy.da.UpdateCursor(constants.FC_CORNERS, ['CODMANZANA'], where_clause) as cursor:
                for row in cursor:
                    cursor.deleteRow()
            del cursor
        else:
            with arcpy.da.UpdateCursor(constants.FC_CORNERS, ['CODMANZANA']) as cursor:
                for row in cursor:
                    cursor.deleteRow()
            del cursor
    else:
        arcpy.Delete_management(arg_feature_class)

        arcpy.CreateFeatureclass_management(constants.FC_PATH_BASE_CARTOGRAPHY, arg_name, arg_figure_type, spatial_reference=arg_spatial_reference)

        add_field(constants.FC_CORNERS, "CODSECTOR", "TEXT", 2, "Sector")
        add_field(constants.FC_CORNERS, "CODSUBSECTOR", "TEXT", 3, "SubSector")
        add_field(constants.FC_CORNERS, "CODMANZANA", "TEXT", 6, "Manzana")
        add_field(constants.FC_CORNERS, "CODESQUINA", "TEXT", 8, "Esquina")
        add_field(constants.FC_CORNERS, "EAVESB1", "DOUBLE", 8, "Alero en B1 (m)")
        add_field(constants.FC_CORNERS, "EAVESB2", "DOUBLE", "", "Alero en B2 (m)")
        add_field(constants.FC_CORNERS, "C1", "DOUBLE", "", "Distancia C1 (m)")
        add_field(constants.FC_CORNERS, "C2", "DOUBLE", "", "Distancia C2 (m)")


def init_base_cartography():
    config_parser = ConfigParser.RawConfigParser()
    config_file_path = r'config.txt'
    config_parser.read(config_file_path)

    return config_parser.get('LOCAL', 'gdb_cartobase'), \
        config_parser.get('LOCAL', 'gdb_fichatecnica'), \
        config_parser.get('LOCAL', 'gdb_ereferencia')


# TIME UTILITIES
def start_time():
    global init_time
    init_time = time()


def stop_time(elements, total_elements, worked_elements):
    final_time = time()
    exet_time = final_time - init_time
    log(
        "execution_time: {0}".format(
            datetime.timedelta(seconds=exet_time)
        )
    )
    log(
        "\t total_{0}: {1}".format(
            elements,
            str(total_elements)
        )
    )
    log(
        "\t worked_{0}: {1}".format(
            elements,
            str(worked_elements)
        )
    )
# ---


# LOG UTILITIES
def log(param_text):
    print "{0} \t {1}".format(
        datetime.datetime.now(),
        param_text
    )
# ---


def check_already_done(arg_observations):
    if arg_observations is not None:
        for key in arg_observations.split(";"):
            if key == constants.ALREADY_DONE_KEY:
                return True
    return False


def if_null(var, val):
    if var is None:
        return val
    return var