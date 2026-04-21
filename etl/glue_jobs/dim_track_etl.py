"""
DimTrack ETL — AWS Glue Visual Job (exportado y corregido)
Fuente : RDS PostgreSQL tablas:
            public.track, public.album, public.artist,
            public.genre, public.media_type
Destino: s3://chinook-datalake-academy/dim_track/
Modo   : Overwrite (siempre el estado actual)
Bookmark: ACTIVADO — solo procesa tracks nuevos en cada ejecución
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# ── 1. SOURCES — Leer las 5 tablas desde RDS ───────────────────────────────

track_source = glueContext.create_dynamic_frame.from_options(
    connection_type="postgresql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "public.track",
        "connectionName": "chinook-rds",
    },
    transformation_ctx="track_source"
)

album_source = glueContext.create_dynamic_frame.from_options(
    connection_type="postgresql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "public.album",
        "connectionName": "chinook-rds",
    },
    transformation_ctx="album_source"
)

artist_source = glueContext.create_dynamic_frame.from_options(
    connection_type="postgresql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "public.artist",
        "connectionName": "chinook-rds",
    },
    transformation_ctx="artist_source"
)

genre_source = glueContext.create_dynamic_frame.from_options(
    connection_type="postgresql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "public.genre",
        "connectionName": "chinook-rds",
    },
    transformation_ctx="genre_source"
)

media_type_source = glueContext.create_dynamic_frame.from_options(
    connection_type="postgresql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "public.media_type",
        "connectionName": "chinook-rds",
    },
    transformation_ctx="media_type_source"
)

# ── 2. Convertir a DataFrames y renombrar columnas ANTES de los JOINs ──────
# Esto evita el problema de columnas duplicadas llamadas "name" y "artist_id"

track_df = track_source.toDF()

album_df = album_source.toDF().select(
    col("album_id").alias("album_album_id"),
    col("title").alias("Album"),
    col("artist_id").alias("album_artist_id")
)

artist_df = artist_source.toDF().select(
    col("artist_id").alias("artist_artist_id"),
    col("name").alias("Artist")
)

genre_df = genre_source.toDF().select(
    col("genre_id").alias("genre_genre_id"),
    col("name").alias("Genre")
)

media_type_df = media_type_source.toDF().select(
    col("media_type_id").alias("media_type_media_type_id"),
    col("name").alias("MediaType")
)

# ── 3. JOINs encadenados ────────────────────────────────────────────────────

# Join 1: track ⟕ album
joined_df = track_df.join(
    album_df,
    track_df["album_id"] == album_df["album_album_id"],
    "left"
)

# Join 2: resultado ⟕ artist
joined_df = joined_df.join(
    artist_df,
    joined_df["album_artist_id"] == artist_df["artist_artist_id"],
    "left"
)

# Join 3: resultado ⟕ genre
joined_df = joined_df.join(
    genre_df,
    joined_df["genre_id"] == genre_df["genre_genre_id"],
    "left"
)

# Join 4: resultado ⟕ media_type
joined_df = joined_df.join(
    media_type_df,
    joined_df["media_type_id"] == media_type_df["media_type_media_type_id"],
    "left"
)

# ── 4. Seleccionar solo las columnas finales del modelo ─────────────────────
dim_track_df = joined_df.select(
    col("track_id").alias("TrackKey"),
    col("name").alias("Name"),
    col("Album"),
    col("Artist"),
    col("Genre"),
    col("MediaType"),
    col("composer").alias("Composer"),
    col("milliseconds").alias("Milliseconds")
)

# ── 5. Convertir de vuelta a DynamicFrame ──────────────────────────────────
result_node = DynamicFrame.fromDF(dim_track_df, glueContext, "result_node")

# ── 6. TARGET — Escribir en S3 como Parquet (Snappy) ───────────────────────
glueContext.write_dynamic_frame.from_options(
    frame=result_node,
    connection_type="s3",
    format="glueparquet",
    connection_options={
        "path": "s3://chinook-datalake-academy/dim_track/",
        "partitionKeys": [],
    },
    format_options={
        "compression": "snappy",
        "useGlueParquetWriter": True,
    },
    transformation_ctx="target_node"
)

# ── Commit del Job Bookmark ─────────────────────────────────────────────────
job.commit()