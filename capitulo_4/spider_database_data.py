#!/usr/bin/python
# coding=utf-8

import arcpy
import os
import psycopg2
import datetime

FC_PATH = "#CONFIDENCIAL\\Fase1PrecampoCartoBase.gdb"
FC_BLOCKS = os.path.join(
    os.sep,
    FC_PATH,
    "Manzanas"
)
FC_PLOTS = os.path.join(
    os.sep,
    FC_PATH,
    "Lotes"
)


def order_by_length(line):
    """ Key encargada de ordenar la lista de líneas de acuerdo a su longitud. """
    return line.length


def search_C1_line(param_order_line_list):
    """ Se encarga de buscar la línea C1 en la lista a través de la comparación de sus coordenadas. """
    cand_x = float("inf")
    cand_y = float("-inf")
    cand = None

    for line in param_order_line_list:
        for pnt in line.boundary():
            if pnt.X < cand_x:
                cand_x = pnt.X
                cand = line
            elif pnt.X == cand_x:
                if pnt.Y > cand_y:
                    cand_y = pnt.Y
                    cand = line
    return cand


def check_square_form(param_line_list, ratio):
    """ Función que compreba si una manzana es cuadrada. """
    if ((param_line_list[2].length - ratio) < param_line_list[0].length < (param_line_list[2].length + ratio)) and ((param_line_list[3].length - ratio) < param_line_list[1].length < (param_line_list[3].length + ratio)):
        return True
    return False


def main():
    """ El proceso se encarga de obtener la base de conocimiento que usaremos en el algoritmo de clasificación. """
    data = []

    # Connection zone
    dbname = "TFG"
    dbuser = "postgres"
    host = "localhost"
    password = "#CONFIDENCIAL"
    count = 0

    try:
        conn = psycopg2.connect(
            "dbname='{0}' user='{1}' host='{2}' password='{3}'".format(
                dbname,
                dbuser,
                host,
                password
            )
        )
    except:
        print("I am unable to connect to the database.")
    # ---

    block_fields = [
        'OID@',
        'SHAPE@',
        'SHAPE@X',
        'SHAPE@Y',
        'SHAPE@XY',
        'SHAPE@TRUECENTROID',
        'CODSECTOR',
        'CODSUBSECTOR',
        'CODMANZANA'
    ]

    total_blocks = str(arcpy.GetCount_management(FC_BLOCKS))

    for block in arcpy.da.SearchCursor(FC_BLOCKS, block_fields, """{0} = {1}""".format("OBJECTID", 10717)):

        print("{0} \t MANZANA Nº {1} \t\t {2}/{3} \t\t ".format(
            datetime.datetime.now(),
            block[0],
            count,
            total_blocks
        ))

        C1_plots_number = 0
        C2_plots_number = 0
        L1_plots_number = 0
        C1_length = None
        C2_length = None
        L1_length = None
        L2_length = None
        square_form = None
        rectangular_form = None
        point_list = []
        line_list = []
        notcontinue = True
        already_done_dict = []
        already_done_pnts = []

        if not block[1].isMultipart:
            for part in block[1]:
                for pnt in part:
                    current_point = {'x': pnt.X, 'y': pnt.Y}
                    if current_point not in already_done_pnts:
                        already_done_pnts.append(current_point)
                        point_list.append(pnt)

            if len(point_list) == 4:
                line_list.append(arcpy.Polyline(arcpy.Array([point_list[0], point_list[1]])))
                line_list.append(arcpy.Polyline(arcpy.Array([point_list[1], point_list[2]])))
                line_list.append(arcpy.Polyline(arcpy.Array([point_list[2], point_list[3]])))
                line_list.append(arcpy.Polyline(arcpy.Array([point_list[3], point_list[0]])))

                order_line_list = sorted(line_list, key=order_by_length)

                C1 = search_C1_line(order_line_list[0:2])

                new_line_list = []

                new_line_list.append(line_list[line_list.index(C1)])
                new_line_list.append(line_list[(line_list.index(C1) + 1) % 4])
                new_line_list.append(line_list[(line_list.index(C1) + 2) % 4])
                new_line_list.append(line_list[(line_list.index(C1) + 3) % 4])

                for line in new_line_list:
                    if line.length == 0:
                        notcontinue = False

                if notcontinue:
                    C1_length = new_line_list[0].length
                    C2_length = new_line_list[1].length
                    L1_length = new_line_list[2].length
                    L2_length = new_line_list[3].length
                    square_form = check_square_form(new_line_list, 0.2)
                    rectangular_form = True if not square_form else False

                    plot_fields = [
                        'SHAPE@'
                    ]
                    plot_where_clause = "{0} = '{1}'".format("CODMANZANA", block[8])

                    pnts_already_done = []
                    for plot in arcpy.da.SearchCursor(FC_PLOTS, plot_fields, plot_where_clause):
                        for part in plot[0]:
                            for pnt in part:
                                actual_point = {'x': pnt.X, 'y': pnt.Y}
                                if actual_point not in pnts_already_done:
                                    if new_line_list[0].buffer(2).contains(pnt, "BOUNDARY"):
                                        C1_plots_number += 1
                                    elif new_line_list[1].buffer(2).contains(pnt, "BOUNDARY"):
                                        L1_plots_number += 1
                                    elif new_line_list[2].buffer(2).contains(pnt, "BOUNDARY"):
                                        C2_plots_number += 1
                                    pnts_already_done.append(actual_point)
        C1_plots_number -= 1

        if C1_plots_number == 2 and C2_plots_number == 2:
            pass
        elif C1_plots_number == 2 or C2_plots_number == 2:
            L1_plots_number -= 1
        else:
            L1_plots_number -= 2

        row_data = [{
            'C1_plots_number': C1_plots_number,
            'C2_plots_number': C2_plots_number,
            'L1_plots_number': L1_plots_number,
            'L2_plots_number': L1_plots_number,
            'x_block_coordinate': block[2],
            'y_block_coordinate': block[3],
            'OBJECTID': block[0],
            'CODSECTOR': block[6],
            'CODSUBSECTOR': block[7],
            'CODMANZANA': block[8],
            'x_centroid_coordinate': block[4][0],
            'y_centroid_coordinate': block[4][1],
            'x_true_centroid_coordinate': block[5][0],
            'y_true_centroid_coordinate': block[5][1],
            'block_area': block[1].area,
            'block_length': block[1].length,
            'C1_length': C1_length,
            'C2_length': C2_length,
            'L1_length': L1_length,
            'L2_length': L2_length,
            'block_apexes_number': block[1].pointCount - 1,
            'rectangular_form': rectangular_form,
            'square_form': square_form,
            'is_multipart': block[1].isMultipart
        }]

        print("{0} \t MANZANA Nº {1} \t\t {2}/{3} \t\t MULTIPART: {4} \t\t LADOS: ({5}/{6}/{7}/{8})".format(
            datetime.datetime.now(),
            block[0],
            count,
            total_blocks,
            str(block[1].isMultipart),
            C1_plots_number,
            L1_plots_number,
            C2_plots_number,
            L1_plots_number
        ))

        cursor = conn.cursor()
        cursor.executemany("""INSERT INTO blocks_details(
            C1_plots_number, 
            C2_plots_number,
            L1_plots_number,
            L2_plots_number,
            x_block_coordinate,
            y_block_coordinate,
            OBJECTID,
            CODSECTOR,
            CODSUBSECTOR,
            CODMANZANA,
            x_centroid_coordinate,
            y_centroid_coordinate,
            x_true_centroid_coordinate,
            y_true_centroid_coordinate,
            block_area,
            block_length,
            C1_length,
            C2_length,
            L1_length,
            L2_length,
            block_apexes_number,
            rectangular_form,
            square_form,
            is_multipart
        ) VALUES (
            %(C1_plots_number)s, 
            %(C2_plots_number)s,
            %(L1_plots_number)s,
            %(L2_plots_number)s,
            %(x_block_coordinate)s,
            %(y_block_coordinate)s,
            %(OBJECTID)s,
            %(CODSECTOR)s,
            %(CODSUBSECTOR)s,
            %(CODMANZANA)s,
            %(x_centroid_coordinate)s,
            %(y_centroid_coordinate)s,
            %(x_true_centroid_coordinate)s,
            %(y_true_centroid_coordinate)s,
            %(block_area)s,
            %(block_length)s,
            %(C1_length)s,
            %(C2_length)s,
            %(L1_length)s,
            %(L2_length)s,
            %(block_apexes_number)s,
            %(rectangular_form)s,
            %(square_form)s,
            %(is_multipart)s
        )""", row_data)

        cursor.close()
        conn.commit()

        # Actualizo contador de manzanas
        count += 1

    conn.close()


if __name__ == '__main__':
    main()
