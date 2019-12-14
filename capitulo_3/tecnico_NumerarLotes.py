#!/usr/bin/python
# coding=utf-8

import arcpy
import constants
import utilities
import sys


arcpy.env.workspace = constants.FC_PATH_BASE_CARTOGRAPHY

utilities.add_field(constants.FC_PLOTS, "CODLOTE", "TEXT", 4, "Lote")


def index_exists(tablename, indexname):
    if not arcpy.Exists(tablename):
        return False

    table_description = arcpy.Describe(tablename)

    for iIndex in table_description.indexes:
        if iIndex.Name == indexname:
            return True

    return False


if not index_exists("Lotes", "index_CODMANZANA_Lotes"):
    arcpy.AddIndex_management("Lotes", "CODMANZANA", "index_CODMANZANA_Lotes", "NON_UNIQUE", "ASCENDING")


def search_north_point(pointsInOrder):

    xmin = sys.float_info.max
    ymax = sys.float_info.min

    index_point = 0
    cont = 0

    for point in pointsInOrder:
        if point['pnt'].Y > ymax:
            ymax = point['pnt'].Y
            xmin = point['pnt'].X
            index_point = cont
        elif point['pnt'].Y == ymax:
            if point['pnt'].X < xmin:
                ymax = point['pnt'].Y
                xmin = point['pnt'].X
                index_point = cont
        cont += 1
    return index_point


def main(args):
    utilities.start_time()

    where_clause = utilities.get_arguments_filter(args.s, args.sb, args.b)

    arcpy.MakeFeatureLayer_management(constants.FC_BLOCKS, "blocks_count", where_clause)

    count_blocks = int(arcpy.GetCount_management("blocks_count").getOutput(0))
    count = 0
    count_done = 0

    for block in arcpy.da.SearchCursor(constants.FC_BLOCKS, ['OID@', 'SHAPE@', 'CODSECTOR', 'CODSUBSECTOR', 'CODMANZANA', 'Texto_10'], where_clause):
        if not utilities.check_already_done(block[5]):
            utilities.update_progress_bar(count, count_blocks, param_prefix=constants.PB_PREFIX.format(str(6)))
            if block is not None and block[0] is not None and block[1] is not None and block[2] is not None and block[3] is not None and block[4] is not None:
                plot_points_list = []
                plot_list = []
                plot_shape_list = []
                first = True
                t_union = None

                for lote in arcpy.da.SearchCursor(constants.FC_PLOTS, ['SHAPE@'], """{0} = '{1}'""".format("CODMANZANA", str(block[4]))):
                    if lote is not None and lote[0] is not None:
                        if first:
                            t_union = lote[0]
                            first = False
                        else:
                            t_union = t_union.union(lote[0])
                if t_union is not None:
                    boundary = t_union.boundary()

                for lote in arcpy.da.SearchCursor(constants.FC_PLOTS, ['OID@', 'SHAPE@', 'CODSECTOR', 'CODSUBSECTOR', 'CODMANZANA', 'CODLOTE', 'SHAPE@XY'],
                                                  """{0} = '{1}'""".format("CODMANZANA", str(block[4]))):
                    if lote is not None and lote[0] is not None and lote[1] is not None and lote[2] is not None and lote[3] is not None and lote[4] is not None:
                        plot_shape_list.append(lote[1])
                        for part in lote[1]:
                            if part is not None:
                                for pnt in part:
                                    if pnt is not None and boundary.buffer(2).contains(pnt, 'BOUNDARY'):
                                        plot_points_list.append({'pnt': pnt, 'idPlot': lote[0], 'shape': lote[1], 'distance': boundary.measureOnLine(pnt, False)})
                                        plot_list.append({'shape': lote[1], 'idPlot': lote[0]})

                plot_points_list.sort(key=utilities.order_by_distance)

                if plot_points_list:

                    indexNorte = search_north_point(plot_points_list)

                    done = []
                    count_plot_id = 10

                    for index in range(len(plot_points_list)):
                        current = plot_points_list[(indexNorte + index) % len(plot_points_list)]

                        if current['idPlot'] not in done:
                            utilities.update_plot(current['idPlot'], block[2], block[3], block[4], block[4] + str(count_plot_id).zfill(4))
                            count_done += 1
                            done.append(current['idPlot'])
                            count_plot_id += 10

        count += 1

    utilities.update_progress_bar(count, count_blocks, param_prefix=constants.PB_PREFIX.format(str(6)))
    utilities.stop_time('blocks', count_blocks, count_done)


if __name__ == '__main__':
    parser = utilities.init_arguments()
    main(parser.parse_args())
