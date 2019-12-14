#!/usr/bin/python
# coding=utf-8

import arcpy
import constants
import utilities


def main(args):
    utilities.start_time()

    # Se crean los campos (CODSECTOR, CODSUBSECTOR) en BBDD
    utilities.add_field(constants.FC_BLOCKS, "CODSECTOR", "TEXT", 2, "Sector")
    utilities.add_field(constants.FC_BLOCKS, "CODSUBSECTOR", "TEXT", 3, "SubSector")

    where_clause = utilities.get_arguments_filter(args.s, args.sb, None)

    arcpy.MakeFeatureLayer_management(constants.FC_SUBSECTORS, "subsectors_count", where_clause)

    count_subsectors = int(arcpy.GetCount_management("subsectors_count").getOutput(0))
    count_total_blocks = int(arcpy.GetCount_management(constants.FC_BLOCKS).getOutput(0))
    count_subsec = 0
    count_blocks = 0
    arcpy.MakeFeatureLayer_management(constants.FC_BLOCKS, "manzanas_lyr")

    for subsector in arcpy.da.SearchCursor(constants.FC_SUBSECTORS, ['OID@', 'CODSECTOR', 'CODSUBSECTOR', 'SHAPE@'], where_clause):
        utilities.update_progress_bar(count_subsec, count_subsectors, param_prefix=constants.PB_PREFIX.format(str(2)))
        arcpy.SelectLayerByLocation_management("manzanas_lyr", "COMPLETELY_WITHIN", subsector[3], "", "NEW_SELECTION")

        oids = arcpy.Describe("manzanas_lyr").FIDSet
        for oidmanzana in oids.split(";"):
            oid = int(oidmanzana.strip())
            utilities.update_block(oid, subsector[1], subsector[2])
            count_blocks += 1
        count_subsec += 1

    utilities.update_progress_bar(count_subsec, count_subsectors, param_prefix=constants.PB_PREFIX.format(str(2)))
    utilities.stop_time('blocks', count_total_blocks, count_blocks)
    print("\t error_blocks: {0}".format(count_total_blocks - count_blocks))


if __name__ == '__main__':
    parser = utilities.init_arguments()
    main(parser.parse_args())
