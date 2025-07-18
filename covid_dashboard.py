import streamlit as st
import requests
import pandas as pd
import plotly.express as px

def fetch_covid_data(country):
    url = f"https://disease.sh/v3/covid-19/historical/{country}?lastdays=all"
    response = requests.get(url)

    if response.status_code != 200:
        st.error(f"Failed to fetch data: {response.status_code}")
        return None

    data = response.json()
    
    if "timeline" not in data:
        st.error("No timeline data found for this country.")
        return None
    
    timeline = data["timeline"]
    
    df = pd.DataFrame(timeline["cases"].items(), columns=["Date", "Confirmed"])
    df["Deaths"] = pd.Series(timeline["deaths"]).values
    df["Recovered"] = pd.Series(timeline["recovered"]).values
    df["Date"] = pd.to_datetime(df["Date"], format='%m/%d/%y')
    df = df.sort_values("Date")
    df["Active"] = df["Confirmed"] - df["Deaths"] - df["Recovered"]
    
    return df

def main():
    st.title("COVID-19 Data Dashboard 🌍")

    country = st.text_input("Enter a country name (e.g., Nepal, India, USA):", "Nepal")
    
    if country:
        with st.spinner("Fetching data..."):
            df = fetch_covid_data(country.strip())
        
        if df is not None:
            st.success(f"Data loaded for {country.capitalize()} ({len(df)} records)")
            
            st.dataframe(df.tail(10))  # Show last 10 rows
            
            fig = px.line(df, x="Date", y=["Confirmed", "Deaths", "Recovered", "Active"],
                          title=f"COVID-19 Trends in {country.capitalize()}",
                          labels={"value": "Cases", "variable": "Category"})
            st.plotly_chart(fig, use_container_width=True)
            
            if st.button("Download CSV"):
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(label="Download CSV", data=csv, file_name=f"{country.lower()}_covid_data.csv", mime='text/csv')
        else:
            st.warning("No data available for this country.")

if __name__ == "__main__":
    main()
