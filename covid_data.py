import requests
import pandas as pd
import plotly.express as px

def fetch_covid_data(country):
    url = f"https://disease.sh/v3/covid-19/historical/{country}?lastdays=all"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"[!] Failed to fetch data: {response.status_code}")
        return None

    data = response.json()
    
    if "timeline" not in data:
        print("[!] No timeline data found for this country.")
        return None
    
    timeline = data["timeline"]
    
    # Convert timeline dicts into DataFrame
    df = pd.DataFrame(timeline["cases"].items(), columns=["Date", "Confirmed"])
    df["Deaths"] = pd.Series(timeline["deaths"]).values
    df["Recovered"] = pd.Series(timeline["recovered"]).values
    
    # Convert 'Date' to datetime format
    df["Date"] = pd.to_datetime(df["Date"], format='%m/%d/%y')

    # Sort by date just in case
    df = df.sort_values("Date")

    # Calculate active cases (Confirmed - Deaths - Recovered)
    df["Active"] = df["Confirmed"] - df["Deaths"] - df["Recovered"]

    return df

def plot_covid_trends(df, country):
    fig = px.line(df, x="Date", y=["Confirmed", "Deaths", "Recovered", "Active"],
                  title=f"COVID-19 Trends in {country.capitalize()}")
    fig.show()

def main():
    country = input("Enter country name (e.g., Nepal, India, USA): ").strip()
    df = fetch_covid_data(country)

    if df is not None and not df.empty:
        print(df.tail())  # preview last few rows
        plot_covid_trends(df, country)
        df.to_csv(f"{country.lower()}_covid_data.csv", index=False)
        print(f"[✔] Data saved to {country.lower()}_covid_data.csv")
    else:
        print("[!] No data available.")

if __name__ == "__main__":
    main()
