from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, regexp_replace, initcap, when

spark = SparkSession.builder.appName("1111SaleCleaning").getOrCreate()

print("--- STARTING DATA CLEANING ---")

# Load CSV
df = spark.read.option("header", "true").option("inferSchema", "true").csv("orders.csv")
initial_count = df.count()
print(f"Initial row count: {initial_count}")

# 1. Remove duplicate orders
df = df.dropDuplicates(["order_id"])
after_dup = df.count()
print(f"Row count after removing duplicates: {after_dup} (Dropped: {initial_count - after_dup})")

# 2. Standardize region names (fix mixed case and title case them)
# Also handle missing regions by imputing with "Unknown" or dropping. Let's impute with "Unknown" to preserve row volume.
df = df.withColumn("region", initcap(col("region"))) \
       .withColumn("region", when(col("region").isNull() | (col("region") == "Nan"), "Unknown").otherwise(col("region")))

after_region = df.count()
print(f"Row count after region standardization & missing handling: {after_region}")

# 3. Clean unit_price (remove currency symbols/commas and cast to float)
df = df.withColumn("unit_price_clean", 
                   regexp_replace(regexp_replace(col("unit_price"), "₱", ""), ",", "").cast("float"))

# 4. Drop or correct negative quantities
df = df.filter(col("quantity") > 0)
final_count = df.count()
print(f"Final clean row count (after filtering negative quantities): {final_count}")

# Stop spark session
spark.stop()
