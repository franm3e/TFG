#!/usr/bin/python
# coding=utf-8

import ConfigParser


config_parser = ConfigParser.RawConfigParser()
config_file_path = r'config.txt'
config_parser.read(config_file_path)

# Import GDB's from config.txt
FC_PATH_BASE_CARTOGRAPHY = config_parser.get('LOCAL', 'gdb_cartobase')
FC_PATH_TECHNICAL_CARD = config_parser.get('LOCAL', 'gdb_fichatecnica')
FC_PATH_EREFERENCE = config_parser.get('LOCAL', 'gdb_ereferencia')
FC_PATH_DRINKING_WATER_PILOT = config_parser.get('LOCAL', 'gdb_aguapotable')
FC_PATH_COMERCIAL_CARD = config_parser.get('LOCAL', 'gdb_fichaagua')


# FEATURE CLASSES
FC_SECTORS = FC_PATH_BASE_CARTOGRAPHY + '\Sectores'
FC_SUBSECTORS = FC_PATH_BASE_CARTOGRAPHY + '\Subsectores'
FC_BLOCKS = FC_PATH_BASE_CARTOGRAPHY + '\Manzanas'
FC_GENERALIZED_BLOCKS = FC_PATH_BASE_CARTOGRAPHY + '\ManzanasGeneralizadas'
FC_CORNERS = FC_PATH_BASE_CARTOGRAPHY + '\Esquinas'
FC_GENERALIZED_BLOCKS_PNT = FC_PATH_BASE_CARTOGRAPHY + '\ManzanasGeneralizadas_Pnt'
FC_PLOTS = FC_PATH_BASE_CARTOGRAPHY + '\Lotes'
FC_JOIN_PLOTS = FC_PATH_BASE_CARTOGRAPHY + '\LotesJoin'
FC_TECHNICAL_CARD = FC_PATH_TECHNICAL_CARD + '\FichaTecnica'
FC_EREFERENCE = FC_PATH_EREFERENCE + '\eReferencia'
FC_TECHNICAL_CARD_PROJECT = FC_PATH_TECHNICAL_CARD + '\FichaTecnicaProject'


# OTHER CONSTANTS
SCRIPTS_COUNT = 8
PB_PREFIX = "({0}/" + str(SCRIPTS_COUNT) + ") Progress:"
ALREADY_DONE_KEY = "DONE"
