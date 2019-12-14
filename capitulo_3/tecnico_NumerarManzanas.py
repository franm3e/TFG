#!/usr/bin/python
# coding=utf-8

import arcpy
import constants
import sys
from math import *
import utilities


def get_band_heigth(north_block):
    yMax = sys.float_info.min
    yMin = sys.float_info.max

    for part in north_block['shape']:
        for pnt in part:
            if pnt.Y > yMax:
                yMax = pnt.Y
            if pnt.Y < yMin:
                yMin = pnt.Y
    return (yMax, yMin)


def search_north_block(blockList):
    north_block = {'x': sys.float_info.min, 'y': sys.float_info.min}
    for block in blockList:
        for part in block[1]:
            for pnt in part:
                if pnt.Y > north_block['y']:
                    north_block['y'] = pnt.Y
                    north_block['x'] = pnt.X
                    north_block['shape'] = block[1]
                    north_block['id'] = block[0]
                elif pnt.Y == north_block['y']:
                    if pnt.X > north_block['x']:
                        north_block['y'] = pnt.Y
                        north_block['x'] = pnt.X
                        north_block['shape'] = block[1]
                        north_block['id'] = block[0]
    return north_block


def get_blocks_inside_band(bandHeigth, noroeste, blockList):
    blocks = []

    for manzana in blockList:
        newBlock = {}
        minDistNO = sys.float_info.max

        if bandHeigth[1] < manzana[2][1] < bandHeigth[0]:
            newBlock['id'] = manzana[0]
            # Obtener distancia al noroeste
            for part in manzana[1]:
                for pnt in part:
                    distancia = sqrt(((noroeste[0] - pnt.X) ** 2) + ((noroeste[1] - pnt.Y) ** 2))
                    if minDistNO > distancia:
                        minDistNO = distancia

            newBlock['distance'] = minDistNO
            blocks.append(newBlock)
    return blocks


def order_by_distance(val):
    return val['distancia']


def get_blocks_list(arg_subsector):
    blocks_list = []

    where_clause = """{0} = '{1}' AND {2} <> {3}""".format("CODSUBSECTOR", str(arg_subsector).zfill(3), "Shape_Area", 0)
    for block in arcpy.da.SearchCursor(constants.FC_BLOCKS, ['OID@', 'SHAPE@', 'SHAPE@XY', "Texto_10"], where_clause):
        if not utilities.check_already_done(block[3]):
            if block is not None and block[1] is not None and block[2] is not None:
                blocks_list.append(block)

    return blocks_list


def get_blocks_list_done(arg_subsector):
    blocks_list_done = []

    where_clause = """{0} = '{1}' AND {2} <> {3}""".format("CODSUBSECTOR", str(arg_subsector).zfill(3), "Shape_Area", 0)
    for block in arcpy.da.SearchCursor(constants.FC_BLOCKS, ['CODMANZANA', 'Texto_10'], where_clause):
        if utilities.check_already_done(block[1]):
            if block is not None and block[0] is not None:
                blocks_list_done.append(block[0])

    return blocks_list_done


def get_nice_oido(arg_oido, arg_select_blocks_done):
    count = arg_oido
    while True:
        if arg_oido not in arg_select_blocks_done:
            return count
        else:
            count += 1


def main(args):
    utilities.start_time()

    # Create field (CODMANZANA)
    utilities.add_field(constants.FC_BLOCKS, "CODMANZANA", "TEXT", 6, "Manzana")

    where_clause = utilities.get_arguments_filter(args.s, args.sb, None)

    arcpy.MakeFeatureLayer_management(constants.FC_BLOCKS, "blocks_count", where_clause)

    count_blocks = int(arcpy.GetCount_management("blocks_count").getOutput(0))
    count = 0
    num = 0

    for subsector in arcpy.da.SearchCursor(constants.FC_SUBSECTORS, ['OID@', 'CODSUBSECTOR', 'SHAPE@'], where_clause):
        utilities.update_progress_bar(num, count_blocks, param_prefix=constants.PB_PREFIX.format(str(3)))

        envelop = subsector[2].extent
        band_num = 1
        block_list = get_blocks_list(subsector[1])
        select_blocks_done = get_blocks_list_done(subsector[1])
        blocks_done = []
        orden = []

        while len(block_list) > 0:

            north_block = search_north_block(block_list)
            band_heigth = get_band_heigth(north_block)
            blocks_inside_band = get_blocks_inside_band(band_heigth, (
                envelop.XMin if not utilities.is_even(band_num) else envelop.XMax, envelop.YMax), block_list)
            blocks_inside_band.sort(key=utilities.order_by_distance)

            for x in blocks_inside_band:
                orden.append(x['id'])
                blocks_done.append(x['id'])
                num += 1

            band_num += 1
            block_list = [x for x in block_list if x[0] not in blocks_done]

        where_clause = """{0} = '{1}' AND {2} <> {3}""".format("CODSUBSECTOR", str(subsector[1]).zfill(3), "Shape_Area", 0)
        with arcpy.da.UpdateCursor(constants.FC_BLOCKS, ['OID@', 'CODSECTOR', 'CODSUBSECTOR', 'CODMANZANA', 'Texto_10'], where_clause) as cursor:
            for row in cursor:
                if not utilities.check_already_done(row[4]):
                    block_oido = str(get_nice_oido((str(row[2]) + str(orden.index(row[0]) + 1).zfill(3)), select_blocks_done))
                    code = block_oido
                    select_blocks_done.append(block_oido)
                    row[3] = code
                    cursor.updateRow(row)
                    count += 1

    utilities.update_progress_bar(num, count_blocks, param_prefix=constants.PB_PREFIX.format(str(3)))
    utilities.stop_time('blocks', count_blocks, count)


if __name__ == '__main__':
    parser = utilities.init_arguments()
    main(parser.parse_args())
