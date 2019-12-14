#!/usr/bin/python
# coding=utf-8

import arcpy
import constants
import utilities


def main():
    utilities.start_time()

    # Se crean los campos (CODSECTOR, CODSUBSECTOR) en BBDD
    utilities.add_field(constants.FC_SUBSECTORS, "CODSECTOR", "TEXT", 2, "Sector")
    utilities.add_field(constants.FC_SUBSECTORS, "CODSUBSECTOR", "TEXT", 1, "SubSector")

    count_subsectors = int(arcpy.GetCount_management(constants.FC_SUBSECTORS).getOutput(0))
    count = 0

    for subsector in arcpy.da.SearchCursor(constants.FC_SUBSECTORS, ['OID@', 'SubSector']):
        utilities.update_progress_bar(count, count_subsectors, param_prefix=constants.PB_PREFIX.format(str(1)))
        split = subsector[1].split('-', len(subsector[1]))
        utilities.update_subsector(subsector[0], split[0], split[1])
        count += 1

    utilities.update_progress_bar(count, count_subsectors, param_prefix=constants.PB_PREFIX.format(str(1)))
    utilities.stop_time('subsectors', count_subsectors, count)


if __name__ == '__main__':
    # No necesita parámetros
    main()
