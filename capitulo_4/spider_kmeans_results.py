import os
import csv
import arcpy

RESULTS_CSV_PATH = "#CONFIDENCIAL\\k-means.csv"
FC_PATH = "#CONFIDENCIAL\\Fase1PrecampoCartoBase.gdb"
FC_BLOCKS = os.path.join(
    os.sep,
    FC_PATH,
    "Manzanas"
)


def main():
    with open(RESULTS_CSV_PATH) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                with arcpy.da.UpdateCursor(
                        FC_BLOCKS,
                        ["OBJECTID", "Assignment"],
                        """OBJECTID = {0}""".format(row[4])
                ) as cursor:
                    for row_csor in cursor:
                        row_csor[1] = row[5]
                        cursor.updateRow(row_csor)
                del cursor, row_csor

            line_count += 1
        print("Bloques procesados {0}".format(line_count))


if __name__ == '__main__':
    main()
