import os
import pandas as pd
import settings  # import user created settings file
from zipfile import ZipFile
import csv
import time
from datetime import timedelta


start_time = time.time()

# get INRIX xd segment id and SANDAG generated vintage id
# from the geometry table that was previously created from the INRIX shapefile
# this will be used to create a cross-reference between the speed data and the geometry table

sql = ("SELECT [vintage_id], [xdsegid] "
       "FROM [speed_inrix].[speed_segments_sandiego_ogr2ogr]")
# read segment id and vintage id to a DataFrame
segments = pd.read_sql_query(sql,settings.conn)
# index & sort by the segment id for faster matching to speed data
segments = segments.set_index('xdsegid')
segments = segments.sort_index()


# load all zip files in the data folder ----
# into the INRIX SQL object
for root, dirs, files in os.walk(settings.folder):
    # for each file in the data folder
    for file in files:
        # print("Loading: " + file)
        path = os.path.join(root, file)
        # for each file in the data folder
        if not file.endswith(".zip"):
            pass  # ignore non-zip files
        else:
            with ZipFile(path) as zipfile:  # within the zip archive
                # extract speed data to data folder
                speedCsv = file.rstrip(".zip") + "/data.csv"
                speedPath = os.path.join(root, speedCsv)
                zipfile.extract(member=speedCsv, path=root)
                # write speed data with vintage id added
                writeCsv = file.rstrip(".zip") + "/data_plus_vintage.csv"
                writePath = os.path.join(root, writeCsv)
                with open(writePath, 'w', newline='') as csv_outfile:
                    file_writer = csv.writer(csv_outfile)
                    with open(speedPath, 'r', newline='') as csv_infile:
                        file_reader = csv.reader(csv_infile)
                        first_row = True
                        for row in file_reader:
                            if not first_row:
                                # match vintage id in data row to geometry table (segments)
                                vintage_id = segments.loc[int(row[1]), 'vintage_id']
                                row.append(vintage_id) # add vintage id
                                file_writer.writerow(row)
                            else:
                                # add column name "vintage_id" to first row
                                header_row = row
                                header_row.append("vintage_id")
                                file_writer.writerow(header_row)
                                first_row = False
                # bulk insert speed data to SQL Server
                with settings.conn.cursor() as cursor:
                    sql = "BULK INSERT [speed_inrix].[speed_data_15min] FROM '" + \
                          os.path.realpath(writePath) + "' " + \
                          "WITH (FIRSTROW = 2, TABLOCK, CODEPAGE = 'ACP', " + \
                          "FIELDTERMINATOR=',', ROWTERMINATOR='0x0a');"
                    cursor.execute(sql)
                    cursor.commit()

                # remove extracted speed data
                print("Loaded: Speed data-set ",writePath)
                os.remove(speedPath)
                os.remove(writePath)

elapsed_time_secs = time.time() - start_time
msg = "Read/write and load took: %s secs (Wall clock time)" % timedelta(seconds=round(elapsed_time_secs))
print(msg)