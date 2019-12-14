#!/usr/bin/python
# coding=utf-8

import arcpy
import constants
import math
import utilities


def distanceTo(pnt, pointTo):
    return math.sqrt(((pointTo['x'] - pnt.X) ** 2) + ((pointTo['y'] - pnt.Y) ** 2))


def orderByDistanceToN(val):
    return val['shape'].X


def orderByDistanceToNO(val):
    return val['distance']


def orderByPosFinal(val):
    return val['idFinal']


def numerarEsquinas(dict, iter):
    for x in range(len(dict)):
        dict[(iter['idOrig'] % len(dict))]['idFinal'] = x + 1
        iter['idOrig'] += 1
    return dict


def main(args):

    utilities.simplify_blocks_fc_polygons()

    where_clause = utilities.get_arguments_filter(args.s, args.sb, args.b)

    if where_clause is None:
        utilities.create_feature_class(constants.FC_PATH_BASE_CARTOGRAPHY, "Esquinas", "POINT",
                                       spatial_reference=arcpy.Describe(constants.FC_BLOCKS).spatialReference)
    else:
        # Si no existe creamos la capa de Esquinas
        if not(arcpy.Exists(constants.FC_CORNERS)):
            arcpy.CreateFeatureclass_management(constants.FC_PATH_BASE_CARTOGRAPHY, "Esquinas", "POINT",
                                                spatial_reference=arcpy.Describe(constants.FC_BLOCKS).spatialReference)
        else:
            # La capa ya existía, y tenemos un filtro... borramos lo que cumpla el criterio del filtro
            with arcpy.da.UpdateCursor(constants.FC_CORNERS, ['OID@'], where_clause) as cursor:
                for row in cursor:
                    cursor.deleteRow()

    utilities.start_time()


    arcpy.MakeFeatureLayer_management(constants.FC_BLOCKS, "blocks_count", where_clause)

    count_blocks = int(arcpy.GetCount_management("blocks_count").getOutput(0))
    errors = []
    count = 0
    contesquinas = 0

    for block in arcpy.da.SearchCursor(constants.FC_GENERALIZED_BLOCKS, ['OID@', 'SHAPE@', 'CODSECTOR', 'CODSUBSECTOR', 'CODMANZANA', 'Texto_10'], where_clause):
        if not utilities.check_already_done(block[5]):
            utilities.update_progress_bar(count, count_blocks, param_prefix=constants.PB_PREFIX.format(str(4)))
            if block is not None and block[0] is not None and block[1] is not None and block[2] is not None and block[3] is not None and block[4] is not None:
                envelop = block[1].extent
                noreste = {
                            'x': envelop.XMax,
                            'y': envelop.YMax
                            }
                noroeste = {
                            'x': envelop.XMin,
                            'y': envelop.YMax
                            }
                if block[1].isMultipart:
                    errors.append(block)

                for part in block[1]:
                    cursor = arcpy.da.InsertCursor(constants.FC_CORNERS, ['SHAPE@', 'CODSECTOR', 'CODSUBSECTOR', 'CODMANZANA', 'CODESQUINA'])
                    corner_list = []
                    index = 0
                    for pnt in part:
                        dont = False
                        for x in corner_list:
                            if x['shape'].equals(pnt):
                                dont = True
                                break

                        if not dont:
                            corner_list.append({
                                'shape': pnt,
                                'distanceNE': distanceTo(pnt, noreste),
                                'distanceNO': distanceTo(pnt, noroeste),
                                'idOrig': index
                                }
                            )
                            index += 1
                    if args.o == 'N' or args.o is None:
                        order = sorted(corner_list, key=lambda i: (i['shape'].Y, i['distanceNE']), reverse=True)

                    elif args.o == 'NE':
                        order = sorted(corner_list, key=orderByDistanceToNO)

                    elif args.o == 'NO':
                        order = sorted(corner_list, key=orderByDistanceToNO)

                    corner_list = numerarEsquinas(corner_list, order[0])

                    corner_list = sorted(corner_list, key=orderByPosFinal)

                    for x in range(len(corner_list)):
                        cursor.insertRow((arcpy.Point(corner_list[x]["shape"].X, corner_list[x]["shape"].Y),
                                          block[2],
                                          block[3],
                                          block[4],
                                          str(block[4]).zfill(6) + str(x+1).zfill(2),
                                          ))
                        contesquinas += 1
                    del cursor
        count += 1

    utilities.update_progress_bar(count, count_blocks, param_prefix=constants.PB_PREFIX.format(str(4)))
    utilities.stop_time('blocks', count_blocks, count)


if __name__ == '__main__':
    parser = utilities.init_arguments()
    parser.add_argument(
        "--o",
        required=False,
        help="Orden de numeración de las esquinas. \n"
             "(N) Primero la más al norte \n"
             "(NE) Primero la más al noreste \n"
             "(NO) Primero la más al noroeste",
        )
    main(parser.parse_args())
