"""
DimTrack ETL — AWS Glue Visual Job (exportado)
Fuente : RDS PostgreSQL tablas:
            public.track
            public.album
            public.artist
            public.genre
            public.media_type
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
from pyspark.sql.functions import col

# ── Inicialización ──────────────────────────────────────────────────────────
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc   = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job   = Job(glueContext)
job.init(args["JOB_NAME"], args)

# ── Función helper para leer tablas desde RDS ───────────────────────────────
def read_table(table_name, ctx=None):
    options = {
        "useConnectionProperties": "true",
        "dbtable": f"public.{table_name}",
        "connectionName": "chinook-rds",
    }
    if ctx:
        return glueContext.create_dynamic_frame.from_options(
            connection_type="postgresql",
            connection_options=options,
            transformation_ctx=ctx,
        )
    return glueContext.create_dynamic_frame.from_options(
        connection_type="postgresql",
        connection_options=options,
    )

# ── 1. SOURCE — Leer las 5 tablas desde RDS ────────────────────────────────
# track usa transformation_ctx para el Job Bookmark
track_node      = read_table("track",      ctx="track_node")
album_node      = read_table("album")
artist_node     = read_table("artist")
genre_node      = read_table("genre")
media_type_node = read_table("media_type")

# Convertir a DataFrames Spark para hacer los JOINs fácilmente
track_df      = track_node.toDF()
album_df      = album_node.toDF()
artist_df     = artist_node.toDF()
genre_df      = genre_node.toDF()
media_type_df = media_type_node.toDF()

# ── 2. JOINs — Enriquecer track con las tablas de referencia ───────────────

# Join 1: track ⟕ album  (para obtener el título del álbum)
joined_df = track_df.join(
    album_df.select(
        col("album_id"),
        col("title").alias("album_title"),
        col("artist_id"),
    ),
    on="album_id",
    how="left",
)

# Join 2: resultado ⟕ artist  (para obtener el nombre del artista)
joined_df = joined_df.join(
    artist_df.select(
        col("artist_id"),
        col("name").alias("artist_name"),
    ),
    on="artist_id",
    how="left",
)

# Join 3: resultado ⟕ genre  (para obtener el nombre del género)
joined_df = joined_df.join(
    genre_df.select(
        col("genre_id"),
        col("name").alias("genre_name"),
    ),
    on="genre_id",
    how="left",
)

# Join 4: resultado ⟕ media_type  (para obtener el tipo de medio)
joined_df = joined_df.join(
    media_type_df.select(
        col("media_type_id"),
        col("name").alias("media_type_name"),
    ),
    on="media_type_id",
    how="left",
)

# ── 3. SELECCIONAR y renombrar solo las columnas del modelo ─────────────────
dim_track_df = joined_df.select(
    col("track_id").alias("TrackKey"),
    col("name").alias("Name"),               # nombre de la canción (de track)
    col("album_title").alias("Album"),
    col("artist_name").alias("Artist"),
    col("genre_name").alias("Genre"),
    col("media_type_name").alias("MediaType"),
    col("composer").alias("Composer"),
    col("milliseconds").alias("Milliseconds"),
)

# ── 4. Convertir de vuelta a DynamicFrame ──────────────────────────────────
from awsglue.dynamicframe import DynamicFrame
result_node = DynamicFrame.fromDF(dim_track_df, glueContext, "result_node")

# ── 5. TARGET — Escribir en S3 como Parquet (Snappy) ───────────────────────
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
    transformation_ctx="target_node",
)

# ── Commit del Job Bookmark ─────────────────────────────────────────────────
job.commit()