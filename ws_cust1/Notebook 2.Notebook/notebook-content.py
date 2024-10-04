# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

control_table_server_name = "oldbtabular.database.windows.net"
control_table_port_number = 1433
control_table_database_name = "Sales_DW"

# Construct JDBC URL for Managed Identity authentication
control_table_jdbc_url = f"jdbc:sqlserver://{control_table_server_name}:{control_table_port_number};database={control_table_database_name};encrypt=true;trustServerCertificate=false;hostNameInCertificate=*.database.windows.net;loginTimeout=30;authentication=ActiveDirectoryMSI;"

# Properties for Managed Identity authentication
control_table_properties = {
    "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver"
}

# Fetch control table data
control_table_query = f"SELECT * FROM [dbo].[artist]"
control_df = spark.read.jdbc(url=control_table_jdbc_url, table=f"({control_table_query}) AS tbl", properties=control_table_properties)

# Display the DataFrame
display(control_df)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
