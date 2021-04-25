SET NOCOUNT ON;
GO


-- create [inrix] schema ---------------------------------------------------
-- note [inrix] schema permissions are defined at end of file
IF NOT EXISTS (
    SELECT TOP 1
        [schema_name]
    FROM
        [information_schema].[schemata]
    WHERE
        [schema_name] = 'inrix'
)
EXEC ('CREATE SCHEMA [inrix]')
GO


-- create xd segment metadata table ------------------------------------------
CREATE TABLE [inrix].[xdseg_metadata] (
	[segment_id] [bigint] IDENTITY(1, 1) NOT NULL,
	[vintage] [nvarchar](20) NOT NULL,
	[xdsegid] [bigint] NOT NULL,
	[frc] [smallint] NOT NULL,
	[road_number] [smallint] NULL,
	[road_name] [nvarchar](150) NULL,
	[county] [nvarchar](10) NOT NULL,
	[district] [nvarchar](25) NULL,
	[miles] [float] NOT NULL,
	[lanes] [float] NOT NULL,
	[slip_road] [bit] NOT NULL,
	[special_road] [nvarchar](5) NULL,
	[road_list] [nvarchar](100) NULL,
	[bearing] [nvarchar](5) NOT NULL,
	[xdgroup] [int] NOT NULL,
	[shape] [geometry] NOT NULL,
    CONSTRAINT [pk_inrix_xdseg_metadata] PRIMARY KEY ([segment_id]),
    CONSTRAINT [ixuq_inrix_xdseg_metadata] UNIQUE ([vintage], [xdsegid])
    )
WITH (DATA_COMPRESSION = PAGE)
GO


-- create INRIX speed dataset 15 min data ------------------------------------
CREATE TABLE [inrix].[speed_15min](
    [speed_15min_id] [bigint] IDENTITY(1, 1) NOT NULL,
    [segment_id] [bigint] NOT NULL,
	[date_time] [datetimeoffset](0) NOT NULL,
	[speed] [float] NULL,
	[hist_av_speed] [float] NULL,
	[ref_speed] [float] NOT NULL,
	[travel_time] [float] NULL,
	[c_value] [float] NULL,
	[pct_score30] [float] NULL,
	[pct_score20] [float] NULL,
	[pct_score10] [float] NULL,
	[road_closure] [nvarchar](5) NULL,
	INDEX [ccsi_inrixspeed_15min] CLUSTERED COLUMNSTORE
)
GO