# Import Python packages
import streamlit as st
from snowflake.snowpark.functions import col

# App title and description
st.title("🥤Customize Your Smoothie Cup🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# Get active Snowflake session
conn = st.connection("snowflake")   # create connection
session = conn.session()            # get Snowpark session

# Input: Smoothie name
name_on_order = st.text_input("Name your smoothie")
if name_on_order:
    st.write("The name of the smoothie:", name_on_order)

# Fetch fruit options from Snowflake
fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]  # Convert to Python list

# Show available fruits
st.dataframe(data=fruit_df, use_container_width=True)

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Process selected ingredients
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)
    st.write("You chose:", ingredients_string)

    # Build SQL safely with parameters
    if st.button("Submit Order"):
        try:
            session.sql(
                "INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER) VALUES (?, ?)",
                params=[ingredients_string, name_on_order]
            ).collect()

            st.success("✅ Your Smoothie has been ordered!")
        except Exception as e:
            st.error(f"❌ Something went wrong: {e}")
else:
    st.info("Please select up to 5 ingredients to create your smoothie.")

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
#st.text(smoothiefroot_response.json())
sf_df st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
