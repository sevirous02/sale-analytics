# 11.11 Sale Analytics

Big Data analytics pipeline and interactive Streamlit dashboard for a Manila-based online seller's 11.11 mega sale.

## Project Structure
- `generate_data.py`: Generates 1,000,000 simulated orders with dirty data and traffic spikes.
- `clean_data.py`: Cleans and standardizes the dataset using PySpark.
- `analyze_data.py`: Computes large-scale metrics and exports summaries to `results/`.
- `app.py`: Streamlit dashboard with key metrics, charts, region filter, and Gemini AI briefing.
