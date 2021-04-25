import geopandas as gpd
import os
import pandas as pd
import pyodbc
import shutil
from zipfile import ZipFile


# set SQL instance and database containing INRIX objects
server = ""  # TODO: set SQL instance
db = ""  # TODO: set SQL database

# set path to INRIX datasets
inrixPath = ""  # TODO: set path to INRIX datasets

# create SQL connection string to database
connStr = "DRIVER={ODBC Driver 17 for SQL Server};" + \
          "SERVER=" + server + ";" + \
          "DATABASE=" + db + ";" + \
          "Trusted_Connection=yes;"

conn = pyodbc.connect(connStr)


# load the geography zip file in the data folder -----------------------------
xd_geo = gpd.read_file("zip://../data/USA_California.zip")

# restrict to San Diego and surrounding counties
xd_geo = xd_geo[xd_geo["County"].isin(
    ["San Diego",
     "Imperial",
     "Riverside",
     "Orange"]
)]

xd_geo = xd_geo.to_crs("EPSG:2230")  # set to SANDAG crs
xd_geo["shape"] = [geo.wkt for geo in xd_geo.geometry]  # append WKT geometry
xd_geo["vintage"] = "2019 Datasets"  # hardcoded dataset vintage

xd_df = xd_geo[[
    "vintage",
    "XDSegID",
    "FRC",
    "RoadNumber",
    "RoadName",
    "County",
    "District",
    "Miles",
    "Lanes",
    "SlipRoad",
    "SpecialRoa",
    "RoadList",
    "Bearing",
    "XDGroup",
    "shape"
]]


# load geography to SQL server -----------------------------------------------
# write xd segment metadata to temporary csv file
# note this csv file must be in a location visible to SQL server
metadataPath = "../data/xdseg_metadata.csv"
xd_df.to_csv(metadataPath, index=False, sep="|")

# bulk insert xd segment metadata to SQL Server temporary table
# then insert to final SQL table transforming WKT to geometry
with conn.cursor() as cursor:
    sqlTT = "DROP TABLE IF EXISTS [inrix].[temp_xdseg_metadata];" \
            "CREATE TABLE [inrix].[temp_xdseg_metadata] (" \
            "[vintage] nvarchar(20) NOT NULL," \
            "[xdsegid] [int] NOT NULL," \
            "[frc] [smallint] NOT NULL," \
            "[road_number] [smallint] NULL," \
            "[road_name] [nvarchar](150) NULL," \
            "[county] [nvarchar](10) NOT NULL," \
            "[district] [nvarchar](25) NULL," \
            "[miles] [float] NOT NULL," \
            "[lanes] [float] NOT NULL," \
            "[slip_road] [bit] NOT NULL," \
            "[special_road] [nvarchar](5) NULL," \
            "[road_list] [nvarchar](100) NULL," \
            "[bearing] [nvarchar](5) NOT NULL," \
            "[xdgroup] [int] NOT NULL," \
            "[shape] [nvarchar](max) NOT NULL," \
            "CONSTRAINT [pk_inrix_temp_xdseg_metadata] PRIMARY KEY ([vintage], [xdsegid]))"

    cursor.execute(sqlTT)
    cursor.commit()

    sqlBI = "BULK INSERT [inrix].[temp_xdseg_metadata] FROM '" + \
            os.path.realpath(metadataPath) + "' " + \
            "WITH (FIRSTROW = 2, TABLOCK, CODEPAGE = 'ACP', " + \
            "FIELDTERMINATOR='|', ROWTERMINATOR='0x0a', MAXERRORS=0);"

    cursor.execute(sqlBI)
    cursor.commit()

    sqlInsert = "INSERT INTO [inrix].[xdseg_metadata] (" \
                "[vintage], [xdsegid], [frc], [road_number]," \
                "[road_name], [county], [district]," \
                "[miles], [lanes], [slip_road], [special_road], [road_list]," \
                "[bearing], [xdgroup], [shape]) " \
                "SELECT [vintage], [xdsegid], [frc], [road_number]," \
                "[road_name], [county], [district]," \
                "[miles], [lanes], [slip_road], [special_road], [road_list]," \
                "[bearing], [xdgroup]," \
                "geometry::STGeomFromText([shape], 2230).MakeValid()" \
                "FROM [inrix].[temp_xdseg_metadata]; " \
                "DROP TABLE [inrix].[temp_xdseg_metadata]"
    cursor.execute(sqlInsert)
    cursor.commit()

os.remove(metadataPath)


# load INRIX speed data ------------------------------------------------------
# store xd segment metadata surrogate key lookup
xdQry = "SELECT [segment_id], [xdsegid] " \
        "FROM [inrix].[xdseg_metadata]" \
        "WHERE [vintage] = '2019 Datasets'"
xdLookup = pd.read_sql_query(xdQry, conn)

for root, dirs, files in os.walk(inrixPath):
    # for each file in the data folder
    for file in files:
        path = os.path.join(root, file)

        # for each file in the data folder
        if not file.endswith(".zip"):
            pass  # ignore non-zip files
        else:
            with ZipFile(path) as zipData:  # within the zip archive
                print("Loading: " + file)

                # extract data csv file from archive
                speedPath = file.rstrip(".zip") + "/data.csv"
                zipData.extract(member=speedPath, path=root)

            # create SQL temporary table and bulk insert data csv file
            with conn.cursor() as cursor:
                sqlTT = "CREATE TABLE [inrix].[temp_speed_15min] (" \
                        "[Date Time] datetimeoffset(0) NOT NULL," \
                        "[Segment ID] bigint NOT NULL," \
                        "[UTC Date Time] datetimeoffset(0) NOT NULL," \
                        "[Speed(km/hour)] float NULL," \
                        "[Hist Av Speed(km/hour)] float NULL," \
                        "[Ref Speed(km/hour)] float NOT NULL," \
                        "[Travel Time(Minutes)] float NULL," \
                        "[CValue] float NULL," \
                        "[Pct Score30] float NULL," \
                        "[Pct Score20] float NULL," \
                        "[Pct Score10] float NULL," \
                        "[Road Closure] nvarchar(5) NULL," \
                        "[Corridor/Region Name] nvarchar(40) NOT NULL," \
                        "CONSTRAINT pk_inrix_temp_speed_15min PRIMARY KEY ([Date Time], [Segment ID]))"
                cursor.execute(sqlTT)
                cursor.commit()

                sqlBI = "BULK INSERT [inrix].[temp_speed_15min] FROM '" + \
                        os.path.realpath(os.path.join(root, speedPath)) + "' " + \
                        "WITH (FIRSTROW = 2, TABLOCK, CODEPAGE = 'ACP', " + \
                        "FIELDTERMINATOR=',', ROWTERMINATOR='0x0a', MAXERRORS=0);"
                cursor.execute(sqlBI)
                cursor.commit()

                # insert temporary table data into final SQL table
                # applying transformations as necessary
                # convert kmph to mph and append xd segment surrogate key
                # note the dataset version is hardcoded in this query
                # then drop the temporary table
                sqlInsert = "INSERT INTO [inrix].[speed_15min] (" + \
                            "[segment_id], [date_time], [speed]," + \
                            "[hist_av_speed], [ref_speed], [travel_time]," + \
                            "[c_value], [pct_score30], [pct_score20]," + \
                            "[pct_score10], [road_closure]) " + \
                            "SELECT [xdseg_metadata].[segment_id], [Date Time]," + \
                            "[Speed(km/hour)] * 0.621371," + \
                            "[Hist Av Speed(km/hour)] * 0.621371," + \
                            "[Ref Speed(km/hour)] * 0.621371," + \
                            "[Travel Time(Minutes)], [CValue], [Pct Score30]," + \
                            "[Pct Score20], [Pct Score10], [Road Closure] " + \
                            "FROM [inrix].[temp_speed_15min] " + \
                            "INNER JOIN [inrix].[xdseg_metadata] " + \
                            "ON [xdseg_metadata].[vintage] = '2019 Datasets' " + \
                            "AND [temp_speed_15min].[Segment ID] = [xdseg_metadata].[xdsegid];" + \
                            "DROP TABLE [inrix].[temp_speed_15min]"
                cursor.execute(sqlInsert)
                cursor.commit()

            # remove extracted data csv file
            shutil.rmtree(os.path.join(root, file.rstrip(".zip")))
