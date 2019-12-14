#!/usr/bin/python
# coding=utf-8

import arcpy
import constants
import utilities


def main(args):
    utilities.start_time()

    count = 0
    count_steps = 10

    # Borramos algunos campos... si están en la capa el join nunca coge estos campos de la capa de manzanas
    arcpy.DeleteField_management(constants.FC_PLOTS, ['CODSECTOR', 'CODSUBSECTOR', 'CODMANZANA'])

    count += 1
    utilities.update_progress_bar(count, count_steps, param_prefix=constants.PB_PREFIX.format(str(5)))

    arcpy.SpatialJoin_analysis(constants.FC_PLOTS, constants.FC_BLOCKS, constants.FC_JOIN_PLOTS, "JOIN_ONE_TO_ONE", "KEEP_ALL", "RefName \"RefName\" true true false 255 Text 0 0 ,First,#," + constants.FC_PLOTS + ",RefName,-1,-1;"
                                                                                                    "Text \"Text\" true true false 255 Text 0 0 ,First,#," + constants.FC_PLOTS + ",Text,-1,-1;"
                                                                                                    "TxtAngle \"TxtAngle\" true true false 8 Double 0 0 ,First,#," + constants.FC_PLOTS + ",TxtAngle,-1,-1;"
                                                                                                    "TxtMemo \"TxtMemo\" true true false 2048 Text 0 0 ,First,#," + constants.FC_PLOTS + ",TxtMemo,-1,-1;"
                                                                                                    "Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + constants.FC_PLOTS + ",Shape_Length,-1,-1;"
                                                                                                    "Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#," + constants.FC_PLOTS + ",Shape_Area,-1,-1;"
                                                                                                    "CODLOTE \"Lote\" true true false 10 Text 0 0 ,First,#," + constants.FC_PLOTS + ",CODLOTE,-1,-1;"
                                                                                                    "NUMLOTE \"Numero Lote\" true true false 4 Text 0 0 ,First,#," + constants.FC_PLOTS + ",NUMLOTE,-1,-1;"
                                                                                                    "CODSECTOR \"Sector\" true true false 2 Text 0 0 ,First,#," + constants.FC_BLOCKS + ",CODSECTOR,-1,-1;"
                                                                                                    "CODSUBSECTOR \"Subsector\" true true false 3 Text 0 0 ,First,#," + constants.FC_BLOCKS + ",CODSUBSECTOR,-1,-1;"
                                                                                                    "CODMANZANA \"Manzana\" true true false 7 Text 0 0 ,First,#," + constants.FC_BLOCKS + ",CODMANZANA,-1,-1", "HAVE_THEIR_CENTER_IN", "", "")
    count += 1
    utilities.update_progress_bar(count, count_steps, param_prefix=constants.PB_PREFIX.format(str(5)))

    arcpy.DeleteFeatures_management(constants.FC_PLOTS)

    count += 1
    utilities.update_progress_bar(count, count_steps, param_prefix=constants.PB_PREFIX.format(str(5)))

    utilities.add_field(constants.FC_PLOTS, "CODSECTOR", "TEXT", 2, "Sector")
    count += 1
    utilities.add_field(constants.FC_PLOTS, "CODSUBSECTOR", "TEXT", 3, "SubSector")
    count += 1
    utilities.add_field(constants.FC_PLOTS, "CODMANZANA", "TEXT", 6, "Manzana")
    count += 1
    utilities.add_field(constants.FC_PLOTS, "CODLOTE", "TEXT", 10, "Lote")
    count += 1
    utilities.add_field(constants.FC_PLOTS, "NUMLOTE", "TEXT", 4, "Numero Lote")

    count += 1
    utilities.update_progress_bar(count, count_steps, param_prefix=constants.PB_PREFIX.format(str(5)))

    arcpy.Append_management(constants.FC_JOIN_PLOTS, constants.FC_PLOTS, "NO_TEST", "RefName \"RefName\" true true false 255 Text 0 0 ,First,#,"+ constants.FC_JOIN_PLOTS +",RefName,-1,-1;"
                                            "Text \"Text\" true true false 255 Text 0 0 ,First,#," + constants.FC_JOIN_PLOTS + ",Text,-1,-1;"
                                            "TxtAngle \"TxtAngle\" true true false 8 Double 0 0 ,First,#," + constants.FC_JOIN_PLOTS + ",TxtAngle,-1,-1;"
                                            "TxtMemo \"TxtMemo\" true true false 2048 Text 0 0 ,First,#," + constants.FC_JOIN_PLOTS + ",TxtMemo,-1,-1;"
                                            "Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#," + constants.FC_JOIN_PLOTS + ",Shape_Length,-1,-1;"
                                            "Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#," + constants.FC_JOIN_PLOTS + ",Shape_Area,-1,-1;"
                                            "CODLOTE \"CODLOTE\" true true false 10 Text 0 0 ,First,#," + constants.FC_JOIN_PLOTS + ",CODLOTE,-1,-1;"
                                            "NUMLOTE \"NUMLOTE\" true true false 4 Text 0 0 ,First,#," + constants.FC_JOIN_PLOTS + ",NUMLOTE,-1,-1;"
                                            "CODSECTOR \"CODSECTOR\" true true false 0 Text 0 0 ,First,#," + constants.FC_JOIN_PLOTS + ",CODSECTOR,-1,-1;"
                                            "CODSUBSECTOR \"CODSUBSECTOR\" true true false 0 Text 0 0 ,First,#," + constants.FC_JOIN_PLOTS + ",CODSUBSECTOR,-1,-1;"
                                            "CODMANZANA \"CODMANZANA\" true true false 0 Text 0 0 ,First,#," + constants.FC_JOIN_PLOTS + ",CODMANZANA,-1,-1;")
    count += 1
    utilities.update_progress_bar(count, count_steps, param_prefix=constants.PB_PREFIX.format(str(5)))

    arcpy.Delete_management(constants.FC_JOIN_PLOTS, "")
    count += 1

    utilities.update_progress_bar(count, count_steps, param_prefix=constants.PB_PREFIX.format(str(5)))
    utilities.stop_time('steps', count_steps, count)


if __name__ == '__main__':
    parser = utilities.init_arguments()
    main(parser.parse_args())
