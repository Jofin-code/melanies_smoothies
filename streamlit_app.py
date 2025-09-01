# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import json
import requests

# Title
st.title(f":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in the custom Smoothie!")

# --- Setup Snowflake session ---
try:
    session = get_active_session()  # works inside Snowflake Native Apps
except Exception:
    # Fallback for local / Streamlit Cloud
    with open("connection.json") as f:  # keep your creds in connection.json
        connection_parameters = json.load(f)
    session = Session.builder.configs(connection_parameters).create()

# --- Load fruit options ---
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'))

# Name input
name_on_order = st.text_input("Name:")

# Ingredients multiselect
ingredients_list = st.multiselect(
    "Choose up five ingredients:",
    my_dataframe.collect(),   # make sure it’s a Python list, not a Snowpark DF
    max_selections=5,
    format_func=lambda row: row["FRUIT_NAME"],  # show fruit_name nicely
)

# If user picked fruits
if ingredients_list:
    ingredients_string = " ".join([row["FRUIT_NAME"] for row in ingredients_list])

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(name_on_order, ingredients)
        VALUES('{name_on_order}', '{ingredients_string}');
    """
    st.write(my_insert_stmt)

    time_to_insert = st.button("Submit Order")
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

# External API check
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)
