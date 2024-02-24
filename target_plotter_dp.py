#!/usr/bin/python

#Author: Brandon Klett
#Description:python script to target target data CSV + designation and
# reformat into KML file for ingestion into ATAK
#Date Created: 02/23/2024
#Date Last Modified: 02/24/204

import csv, mgrs, pyproj, datetime, string, secrets, os
from zipfile import ZipFile

#open and read CSV file containing grid, designator, and title
def read_csv():
    grid = []
    desig = []
    title = []
    with open('./read_dir/tgt.csv', newline='') as csvfile:
        csvparse = csv.reader(csvfile, delimiter=',', quotechar='|')
        unlabled_tgt_ctr = 0
        
        for i in csvparse:
            if i[0]:
                grid.append(i[0])
                if not i[1]:
                    desig.append("u")
                else:
                    desig.append(i[1])

                if not i[2]:
                    title.append("tgt " + str(unlabled_tgt_ctr))
                    unlabled_tgt_ctr += 1
                else:
                    title.append(i[2])
            else:
                print("grid column empty moving to next...")

    return grid, desig, title

#converts LAT/LONG to MGRS
def convert_to_mgrs(grid):
    lat_long_tgt = []
    for i in grid:
        mgrs_object = mgrs.MGRS()
        geod = pyproj.Geod(ellps='WGS84')

        lat_min, lon_min = mgrs_object.toLatLon(i.replace(" ",""))

        x_var = geod.line_length([lon_min, lon_min], [lat_min, lat_min + 1])
        y_var = geod.line_length([lon_min, lon_min + 1], [lat_min, lat_min])

        lat_max = lat_min + 100 / x_var
        lon_max = lon_min + 100 / y_var 

        lat_long_tgt.append(""" lat="{0}" lon="{1}" """.format(str(lat_max),str(lon_min)))
    return lat_long_tgt

def gen_uid():
    uid1 = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
              for i in range(8))
    uid2 = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
              for i in range(4))
    uid3 = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
              for i in range(4))
    uid4 = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
              for i in range(4))
    uid5 = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
              for i in range(12))
    uid_gen = str(uid1) + "-" + str(uid2) + "-" + str(uid3) + "-" + str(uid4) + "-" + str(uid5)
    return uid_gen.lower()

#generates MKL file contents
def gen_mkl(lat_long_tgt, desig, title):
    dte_raw = datetime.datetime.now()
    dte = dte_raw.strftime("%Y%m%d%H%M%S")

    dt_zulu = dte_raw.strftime('%Y-%m-%dT%H:%M%S GMT-00:00')
    
    uid_store = []
    
    for tgt, designate, tlt in zip(lat_long_tgt, desig, title):
        uid_gen = gen_uid()
        uid_store.append(uid_gen)

        cot_block = """
                    <event version="2.0" uid="{uid_plc}" type="a-{1}-G" time="{tme}" 
                    start="{tme}" stale="{tme}" how="h-g-i-g-o">
                    <point {0} hae="9999999" ce="9999999" le="9999999" /><detail>
                    <contact callsign="{2}" /><link type="a-f-G-U-C-I" uid="S-1-5-21-3465841570-2924230073-3338536973-1001"
                    parent_callsign="bk_script" relation="p-p" production_time="{tme}" /><archive />
                    <usericon iconsetpath="COT_MAPPING_2525C/a-{1}/a-{1}-G" />
                    </detail></event>\n""".format(tgt, designate, tlt, uid_plc=uid_gen,  tme=dt_zulu)
        
        dp_dir = "./dp_dump/" + uid_gen + "/" + uid_gen + ".cot"
        os.makedirs(os.path.dirname(dp_dir), exist_ok=True)
        dp_file = open(dp_dir, "w")
        dp_file.write(cot_block)
        dp_file.close()
        print("file_written")

    return uid_store
 
def write_manifest(uid_store):
    dte_raw = datetime.datetime.now()
    dte = dte_raw.strftime("%Y%m%d%H%M%S")

    uid_gen = gen_uid()

    contents_full = ''
    manifest_header = """
                <MissionPackageManifest version="2">
                    <Configuration>
                        <Parameter name="name" value="bk_tgt_script_{dt}" />
                        <Parameter name="uid" value="{0}" />
                    </Configuration>
                    <Contents>
                    """.format(uid_gen, dt=dte)
    
    for id in uid_store:
        manifest_contents = """
                        <Content zipEntry="{0}/{0}.cot" ignore="false">
                            <Parameter name="uid" value="{0}" />
                        </Content>
                        """.format(id)
        contents_full = contents_full + manifest_contents

    manifest_footer = """
                    </Contents>
                </MissionPackageManifest>
                    """
    manifest_file = manifest_header + contents_full + manifest_footer

    dp_dir = "./dp_dump/MANIFEST/manifest.xml"
    os.makedirs(os.path.dirname(dp_dir), exist_ok=True)
    dp_file = open(dp_dir, "w")
    dp_file.write(manifest_file)
    dp_file.close()
    print("file_written")

    dp_title = "bk_tgt_script_" + dte

    return dp_title 

def compress(dp_title):
    file_paths = [] 

    with ZipFile("./dp_dump/" + dp_title + ".zip", 'w') as zip:
        os.chdir("./dp_dump/")
        for root, directories, files in os.walk("./"):
            for filename in files:
                filepath = os.path.join(root, filename) 
                file_paths.append(filepath)
        for file in file_paths:
            if dp_title not in file:  
                zip.write(file)
                os.remove(file)
    for current_dir, subdirs, files in os.walk("./", topdown=False):
        try:
            os.rmdir(current_dir)
        except:
            print("unable to delete file " + current_dir)
    print("compression complete...")

print("--------------------------- SCRIPT START ---------------------------")
grid, desig, title = read_csv()
lat_long_tgt = convert_to_mgrs(grid)
uid_store = gen_mkl(lat_long_tgt, desig, title)
dp_title = write_manifest(uid_store)
compress(dp_title)
