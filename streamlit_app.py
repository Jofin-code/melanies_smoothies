import streamlit as st
import requests
import snowflake.connector
from snowflake.snowpark.context import get_active_session

st.title("🥤 Build Your Smoothie!")
st.write("Pick your favorite fruits and order a fresh smoothie!")

# === Snowflake session ===
session = get_active_session()

# Load available fruits
fruit_options = session.sql("SELECT fruit_name FROM smoothies.public.fruit_options").collect()
fruits_list = [row["FRUIT_NAME"] for row in fruit_options]

# Input fields
name = st.text_input("Enter your name:")
chosen_fruits = st.multiselect("Choose up to 5 fruits:", fruits_list, max_selections=5)

# Build order string
if chosen_fruits:
    ingredients_string = ", ".join(chosen_fruits)
    st.write(f"Your smoothie mix: **{ingredients_string}**")
else:
    ingredients_string = ""

# Submit order
if st.button("Submit Order"):
    if name and chosen_fruits:
        order_sql = f"""
            INSERT INTO smoothies.public.orders (NAME, FRUITS)
            VALUES ('{name}', '{ingredients_string}')
        """
        session.sql(order_sql).collect()
        st.success(f"✅ Order submitted for {name} with {ingredients_string}")
    else:
        st.error("Please enter your name and select at least one fruit.")

# --- Fruit API details ---
st.subheader("🍉 Fruit Nutrition Info")

if chosen_fruits:
    for fruit in chosen_fruits:
        url = f"https://my.smoothiefroot.com/api/fruit/{fruit.lower()}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                st.markdown(f"### {fruit.capitalize()}")
                st.write(f"**Calories**: {data.get('calories', 'N/A')}")
                st.write(f"**Sugar**: {data.get('sugar', 'N/A')} g")
                st.write(f"**Carbohydrates**: {data.get('carbohydrates', 'N/A')} g")
                st.write(f"**Protein**: {data.get('protein', 'N/A')} g")
                st.write(f"**Fat**: {data.get('fat', 'N/A')} g")
                st.divider()
            else:
                st.warning(f"⚠️ No data available for {fruit}")
        except Exception as e:
            st.error(f"Error fetching data for {fruit}: {e}")
else:
    st.info("Select fruits above to view their nutrition details.")
