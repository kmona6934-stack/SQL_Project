import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os

# إعدادات الصفحة الاحترافية
st.set_page_config(page_title="SuperStore SQL Analytics", page_icon="📊", layout="wide")

st.title("📊 SuperStore Customer Segmentation Dashboard")
st.markdown("This dashboard executes your **SQL Queries** live to segment customers based on their sales volume.")

# 1. تحميل الداتا بأكثر طريقة مستقرة وآمنة للسيرفرات
@st.cache_data
def load_data():
    # اسم الملف المعتمد في الفولدر
    file_name = "Superstore_Data_with_Sales_Agent.csv"
    
    # التأكد أولاً من وجود الملف في الفولدر قبل القراءة
    if os.path.exists(file_name):
        try:
            df = pd.read_csv(file_name)
            return df
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء قراءة الملف المحلي: {e}")
            return None
    else:
        # حل بديل ذكي: لو السيرفر مغير المسار، يبحث عن أي ملف CSV متوفر
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if csv_files:
            try:
                df = pd.read_csv(csv_files[0])
                return df
            except:
                pass
        st.error("❌ لم نتمكن من العثور على ملف البيانات المستهدف في المستودع. تأكدي من وجود الملف في الفولدر الرئيسي.")
        return None

df = load_data()

if df is not None:
    # تنظيف أسماء الأعمدة لتجنب مشاكل المسافات في الـ SQL
    df.columns = [c.replace(' ', '_') for c in df.columns]
    
    # 2. بناء قاعدة بيانات SQL مؤقتة في الذاكرة
    conn = sqlite3.connect(':memory:')
    df.to_sql('Superstore_Data', conn, index=False, if_exists='replace')
    
    # 3. استعلام الـ SQL بتاعك بالظبط
    sql_query = """
    WITH CustomerSales AS (
        SELECT 
            Customer_Name,
            SUM(CAST(Sales AS DECIMAL)) as Total_Sales
        FROM Superstore_Data
        GROUP BY Customer_Name
    )
    SELECT *,
        CASE 
            WHEN Total_Sales > 10000 THEN 'VIP Customer'
            WHEN Total_Sales > 5000 AND Total_Sales <= 10000 THEN 'Medium Customer'
            ELSE 'Normal Customer'
        END AS Customer_Level
    FROM CustomerSales
    """
    
    try:
        segmented_data = pd.read_sql_query(sql_query, conn)
        
        # --- قسم الـ KPIs (المؤشرات الرئيسية) ---
        total_customers = len(segmented_data)
        vip_count = len(segmented_data[segmented_data['Customer_Level'] == 'VIP Customer'])
        total_sales_sum = segmented_data['Total_Sales'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("👥 Total Unique Customers", f"{total_customers:,}")
        col2.metric("👑 VIP Customers (> $10k)", f"{vip_count:,}")
        col3.metric("💰 Total Analyzed Sales", f"${total_sales_sum:,.2f}")
        
        st.markdown("---")
        
        # --- قسم الأشكال البيانية ---
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📊 Customers Distribution per Segment")
            fig, ax = plt.subplots(figsize=(8, 4.5))
            colors = ['#cbd5e1', '#3b82f6', '#deff9a'] 
            sns.countplot(data=segmented_data, x='Customer_Level', palette=colors, 
                          order=['Normal Customer', 'Medium Customer', 'VIP Customer'], ax=ax)
            ax.set_ylabel("Number of Customers")
            ax.set_xlabel("Segment Level")
            st.pyplot(fig)
            
        with col_right:
            st.subheader("🍰 Revenue Contribution Percentage")
            segment_revenue = segmented_data.groupby('Customer_Level')['Total_Sales'].sum().reset_index()
            fig2, ax2 = plt.subplots(figsize=(8, 4.5))
            ax2.pie(segment_revenue['Total_Sales'], labels=segment_revenue['Customer_Level'], 
                    autopct='%1.1f%%', colors=['#3b82f6', '#cbd5e1', '#deff9a'], startangle=90)
            ax2.axis('equal')  
            st.pyplot(fig2)
            
        # --- قسم الفلترة التفاعلية ---
        st.markdown("---")
        st.subheader("🔍 Deep Dive into Customer Levels")
        selected_level = st.selectbox("Filter Table by Segment:", ['All', 'VIP Customer', 'Medium Customer', 'Normal Customer'])
        
        if selected_level != 'All':
            filtered_df = segmented_data[segmented_data['Customer_Level'] == selected_level]
        else:
            filtered_df = segmented_data
            
        st.dataframe(filtered_df.sort_values(by='Total_Sales', ascending=False), use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ حدث خطأ في تنفيذ كود الـ SQL: {e}")
