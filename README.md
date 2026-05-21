# 📊 SuperStore Strategic Sales Analytics & Customer Segmentation

An end-to-end data analytics project using **Advanced SQL Queries** and **Python (Streamlit)** to analyze retail transactions, perform data cleaning, and engineer a dynamic customer segmentation model.

## 🚀 Live Dashboard
You can interact with the live dashboard directly here: 
👉 **[Click Here to Open the Live Dashboard](https://sqlproject-fp5astcjybfrglsyvxi5dn.streamlit.app/)**

---

## 💼 Business Case & Objective
In retail, a "one-size-fits-all" marketing strategy is inefficient. The goal of this project is to analyze over 5,000+ transactions from the **SuperStore Dataset** to find high-value customer segments. 

By applying an **RFM-style monetary ranking algorithm**, we categorize customers into three strategic tiers:
1. **VIP Customers:** High-volume buyers driving premium revenue.
2. **Medium Customers:** Consistent buyers with high upselling potential.
3. **Normal Customers:** Standard retail shoppers.

---

## 🛠️ Technical Workflow & Features

### 1. Data Engineering & Cleaning (SQL)
Before building visual assets, a strict SQL pipeline was executed to ensure absolute data integrity:
* **Data Type Standardization:** Converted raw text metrics into precise `DECIMAL(10,2)` values for financial accuracy.
* **Data Quality Audit:** Handled structural text anomalies and null values using `ISNUMERIC` filters and conditional updates (`UPDATE`).

### 2. Analytical Segmentation Logic
Leveraged complex conditional logic (`CASE WHEN`) grouped by unique customer signatures to build a structural analytical view:

```sql
CREATE VIEW Customers_Levels AS 
SELECT 
    [Customer Name], 
    ROUND(SUM([Sales]), 2) AS Total_Sales,
    CASE 
        WHEN SUM([Sales]) > 10000 THEN 'VIP Customer'
        WHEN SUM([Sales]) > 5000 AND SUM([Sales]) <= 10000 THEN 'Medium Customer'
        ELSE 'Normal Customer'
    END AS Customer_Level
FROM Superstore_Data
GROUP BY [Customer Name];
