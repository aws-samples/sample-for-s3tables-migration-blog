# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from pyspark.sql import SparkSession
import sys

PQT_DATABASE_NAME = "blogdb"
S3_BUCKET = sys.argv[1] 
S3_BUCKET_PARQUET_PATH = f"s3://{S3_BUCKET}/data/{PQT_DATABASE_NAME}/"

spark = SparkSession.builder \
    .appName("S3TablesMigrationDataSetup") \
    .enableHiveSupport() \
    .getOrCreate()

# Read the TPC-DS store_sales fact table
path = "s3://blogpost-sparkoneks-us-east-1/blog/BLOG_TPCDS-TEST-3T-partitioned/store_sales/"
source_df = spark.read.parquet(path)
source_df.cache()

spark.sql(f"CREATE DATABASE IF NOT EXISTS {PQT_DATABASE_NAME} LOCATION '{S3_BUCKET_PARQUET_PATH}'")

# Table 1 — the small-file problem: 150,000 tiny snappy files
source_df.repartition(150000) \
    .write.format("parquet") \
    .option("path", f"{S3_BUCKET_PARQUET_PATH}store_sales_snappy_smallfiles") \
    .saveAsTable(f"spark_catalog.{PQT_DATABASE_NAME}.store_sales_snappy_smallfiles")

# Table 2 — well-sized snappy layout: 1,500 files
source_df.repartition(1500) \
    .write.format("parquet") \
    .option("path", f"{S3_BUCKET_PARQUET_PATH}store_sales_snappy_optimized") \
    .saveAsTable(f"spark_catalog.{PQT_DATABASE_NAME}.store_sales_snappy_optimized")

print("Parquet data set preparation complete.")
