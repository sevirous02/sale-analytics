import streamlit as st
import pandas as pd
import os
from google import genai

st.set_page_config(page_title="11.11 Sale Analytics", page_icon="🛍️", layout="centered")

# Load summary metrics
@st.cache_data
def load_data():
    summary = pd.read_csv("results/summary_metrics.csv").iloc[0]
    cat_rev = pd.read_csv("results/category_revenue.csv")
    hourly = pd.read_csv("results/hourly_orders.csv")
    regions = pd.read_csv("results/region_stats.csv")
    return summary, cat_rev, hourly, regions

summary, cat_rev, hourly, regions = load_data()

st.title("🛍️ 11.11 Online Sale Analytics Dashboard")
st.markdown("Big data analytics for Manila-based online seller 11.11 performance.")

# Key Numbers at the top
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"₱{summary['total_revenue']:,.2f}")
col2.metric("Total Orders", f"{int(summary['total_orders']):,}")
col3.metric("Cancellation Rate", f"{summary['cancellation_rate']*100:.1f}%")
col4.metric("Avg Order Value", f"₱{summary['average_order_value']:,.2f}")

st.markdown("---")

# Region Filter
region_list = ["All"] + list(regions['region'].unique())
selected_region = st.selectbox("Filter by Region", region_list)

if selected_region != "All":
    reg_data = regions[regions['region'] == selected_region].iloc[0]
    st.subheader(f"Region Focus: {selected_region}")
    st.info(f"Orders: {int(reg_data['order_count']):,} | Revenue: ₱{reg_data['total_revenue']:,.2f}")

# Charts Section
st.subheader("📊 Revenue by Product Category")
st.bar_chart(cat_rev.set_index("category")['total_revenue'])

st.subheader("📈 Order Volume by Hour of Day")
st.line_chart(hourly.set_index("order_hour")['order_count'])

st.markdown("---")

# Part F: Generative AI Briefing
st.subheader("🤖 Gemini AI Sales Briefing")

prompt_text = f"""
Using only the following 11.11 sale numbers, write a 5-sentence executive briefing for the store owner, and include one concrete recommendation for next year's sale.
- Total Revenue: ₱{summary['total_revenue']:,.2f}
- Total Orders: {int(summary['total_orders']):,}
- Cancellation Rate: {summary['cancellation_rate']*100:.1f}%
- Average Order Value: ₱{summary['average_order_value']:,.2f}
"""

if st.button("Generate Briefing"):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
        if not api_key:
            st.error("Gemini API key not found in Streamlit secrets!")
        else:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_text,
            )
            st.success("Briefing generated successfully!")
            st.write(response.text)
    except Exception as e:
        st.warning(f"AI briefing generation failed: {e}. Please check your API key configuration.")

st.markdown("### Documented Prompt (for README)")
st.code(prompt_text, language="markdown")
