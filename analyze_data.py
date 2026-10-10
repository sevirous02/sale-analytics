import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, hour, when, avg, sum as _sum, count, lit, round, regexp_replace

spark = SparkSession.builder.appName("1111SaleAnalysis").getOrCreate()

os.makedirs("results", exist_ok=True)

df = spark.read.option("header", "true").option("inferSchema", "true").csv("orders.csv")

# Clean columns and properly strip currency symbols before casting
df = df.dropDuplicates(["order_id"]) \
       .filter(col("quantity") > 0) \
       .withColumn("unit_price_clean", 
                   regexp_replace(regexp_replace(col("unit_price"), "₱", ""), ",", "").cast("float")) \
       .withColumn("revenue", col("unit_price_clean") * col("quantity")) \
       .withColumn("order_hour", hour(col("timestamp")))

print("--- COMPUTING ANALYTICS ---")

# 1. Total revenue by category (Delivered orders only)
cat_revenue = df.filter(col("status") == "Delivered") \
                .groupBy("category") \
                .agg(_sum("revenue").alias("total_revenue")) \
                .orderBy(col("total_revenue").desc())
cat_revenue.toPandas().to_csv("results/category_revenue.csv", index=False)

# 2. Orders per hour of the day
hourly_orders = df.groupBy("order_hour") \
                  .agg(count("order_id").alias("order_count")) \
                  .orderBy("order_hour")
hourly_orders.toPandas().to_csv("results/hourly_orders.csv", index=False)

# 3. Revenue and order count by region
region_stats = df.groupBy("region") \
                 .agg(_sum("revenue").alias("total_revenue"), count("order_id").alias("order_count")) \
                 .orderBy(col("total_revenue").desc())
region_stats.toPandas().to_csv("results/region_stats.csv", index=False)

# 4. Cancellation rate by payment method
payment_cancel = df.groupBy("payment_method") \
                   .agg(
                       count("order_id").alias("total_orders"),
                       _sum(when(col("status") == "Cancelled", 1).otherwise(0)).alias("cancelled_orders")
                   ) \
                   .withColumn("cancellation_rate", round(col("cancelled_orders") / col("total_orders"), 4))
payment_cancel.toPandas().to_csv("results/payment_cancellation.csv", index=False)

# 5. Overall Summary
summary_df = df.agg(
    _sum("revenue").alias("total_revenue"),
    count("order_id").alias("total_orders"),
    _sum(when(col("status") == "Cancelled", 1).otherwise(0)).alias("total_cancelled"),
    avg("revenue").alias("average_order_value")
).withColumn("cancellation_rate", round(col("total_cancelled") / col("total_orders"), 4))

summary_df.toPandas().to_csv("results/summary_metrics.csv", index=False)

print("Analytics completed successfully! Results saved to results/ folder.")
spark.stop()
