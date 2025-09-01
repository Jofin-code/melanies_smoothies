# Import python packages
import streamlit as st
from snowflake.snowpark.session import Session
from snowflake.snowpark.functions import col
import requests

# Streamlit UI
st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in the custom Smoothie!")

# ❌ This works only inside Native Apps
# from snowflake.snowpark.context import get_active_session
# session = get_active_session()

# ✅ Instead: build a session using credentials
# (You can also read these from st.secrets or environment variables)
connection_parameters = {
            "account" : "OWBEOHF-WLB55453",
            "user" : "jofin",
            "password" : "JofinRocks@123",
            "role" : "SYSADMIN",
            "warehouse" : "COMPUTE_WH",
            "database" : "SMOOTHIES",
            "schema" : "PUBLIC"
}

session = Session.builder.configs(connection_parameters).create()

# Load fruit options
my_dataframe = session.table("fruit_options").select(col("fruit_name"))

# Name input
name_on_order = st.text_input("Name:")

# Ingredients multiselect
ingredients_list = st.multiselect(
    "Choose up to five ingredients:",
    my_dataframe.collect(),  # convert Snowpark DataFrame -> list
    max_selections=5,
)

if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    my_insert_stmt = f"""
        INSERT INTO orders(name_on_order, ingredients)
        VALUES ('{name_on_order}', '{ingredients_string}')
    """
    st.write(my_insert_stmt)

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")

# Call external API
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)
