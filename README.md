## Migrating Hive Parquet tables to Amazon S3 Tables with the Migration API

In this post, we will cover a few practical scenarios of migrating Hive-style Parquet tables to S3 Tables and observe the results. We have written every step so you can reproduce the whole thing yourself: generate the exact same source data, run the migration, and compare the before and after. By the end you'll have two managed Iceberg tables, two migration reports, and a concrete feel for what the API does to your storage footprint.
 
For this post, we will be creating two copies of Snappy Parquet tables that have the same data but are laid out very differently on S3, so we can cover different practical storage scenarios to observe the behavior after migrating them to S3 Tables.

Both tables hold the same TPC-DS (3 TB) store_sales fact data. The first is a textbook small-file problem: 150,000 tiny objects, each under 5 MB, the kind of layout that quietly taxes every query you run against it. The second is already well-sized to ~365 MB per file. We will migrate both the tables to S3 Tables using the Migration API, that is, without having to write a single line of Spark or any code modules to do the rewrite.

 <add link here>

[Prerequisites](PREREQUISITES.md)

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

