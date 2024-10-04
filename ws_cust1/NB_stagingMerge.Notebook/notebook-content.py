# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "ea46ad2b-7bfb-4cf9-aed9-b33c80c1157e",
# META       "default_lakehouse_name": "LH_Cust1",
# META       "default_lakehouse_workspace_id": "6fb7801b-bf2b-492a-91bc-38a51f57732c"
# META     }
# META   }
# META }

# CELL ********************

folder_path = "abfss://WS_Customer1@onelake.dfs.fabric.microsoft.com/LH_Cust1.Lakehouse/Files/raw"
primary_keys="ProductKey"
src_foldername="Product"
tgt_table_name="DimProduct"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

join_columns = " and ".join(["t." + i + "= s." + i for i in primary_keys.split(",")])
print(join_columns)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

full_path = f"{folder_path}/{src_foldername}"
print(full_path)
shortcuts = notebookutils.fs.ls(full_path)
shortcut_paths = [shortcut.path for shortcut in shortcuts]
print(shortcut_paths)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql import DataFrame

def read_parquet(parquet_path: str) -> DataFrame:
    df = spark.read.parquet(parquet_path)
    return df

def union_parquet_files(parquet_paths: list) -> DataFrame:
    df_union = None

    for path in parquet_paths:
        try:
            # Read the Parquet file or folder
            df_parquet = read_parquet(path)

            # Append the data to the main DataFrame
            if df_union is None:
                df_union = df_parquet
            else:
                df_union = df_union.union(df_parquet)
        
        except Exception as e:
            print(f"Error loading Parquet file from path {path}: {e}")
            continue  # Skip this path and move to the next one

    return df_union



# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df_union = union_parquet_files(shortcut_paths)
if df_union is not None:
    df_union.createOrReplaceTempView("df_union_view")
  

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql   
# MAGIC select * from df_union_view

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from delta.tables import DeltaTable
from pyspark.sql.utils import AnalysisException

# Function to check if the table exists
def table_exists(spark, table_name):
    try:
        spark.table(table_name)
        return True
    except AnalysisException:
        return False

# Check if the target table exists
if not table_exists(spark, tgt_table_name):
    # Create the table (you can define the schema and other options here)
    df_schema = spark.table("df_union_view").schema  # Assuming you want the schema from df_union_view
    empty_df = spark.createDataFrame([], df_schema)
    empty_df.write.format("delta").saveAsTable(tgt_table_name)

# Perform the merge operation
DeltaTable.forName(spark, tgt_table_name).alias("t")\
    .merge(spark.table("df_union_view").alias("s"), join_columns)\
    .whenMatchedUpdateAll()\
    .whenNotMatchedInsertAll()\
    .execute()


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
