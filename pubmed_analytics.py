import re
import pandas as pd

# Load file
file_path = "/mnt/data/abstract-RochesterM-set.txt"
with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# Regex patterns for country and US states
country_pattern = r"\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b"  # naive capitalized word sequences (we'll filter later)
us_states = [
    "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware",
    "Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana",
    "Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana",
    "Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina",
    "North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina",
    "South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia",
    "Wisconsin","Wyoming","District of Columbia"
]

# Extract all matches
matches = re.findall(country_pattern, text)

# Load list of countries from pycountry for filtering
import pycountry
country_names = [country.name for country in pycountry.countries]

# Filter for countries
countries_found = [m for m in matches if m in country_names]

# Filter for states
states_found = []
for state in us_states:
    if state in text:
        count = text.count(state)
        states_found.extend([state]*count)

# Build frequency tables
country_counts = pd.Series(countries_found).value_counts().reset_index()
country_counts.columns = ["Country", "Count"]

state_counts = pd.Series(states_found).value_counts().reset_index()
state_counts.columns = ["US State", "Count"]

import caas_jupyter_tools
caas_jupyter_tools.display_dataframe_to_user("Country and US State Counts", country_counts)
caas_jupyter_tools.display_dataframe_to_user("Country and US State Counts", state_counts)
