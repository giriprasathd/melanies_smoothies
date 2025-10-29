# Import Python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# App title and description
st.title("🥤 Customize Your Smoothie Cup 🥤")
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

    # 🍓 Fetch nutrition info for selected fruits dynamically
    fruit_data = []
    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}")
            if response.status_code == 200:
                data = response.json()
                data["fruit_name"] = fruit_chosen
                fruit_data.append(data)
            else:
                st.warning(f"⚠️ Could not retrieve data for {fruit_chosen}.")
        except Exception as e:
            st.warning(f"⚠️ Error fetching data for {fruit_chosen}: {e}")

    # Combine and display nutrition info
    if fruit_data:
        df = pd.DataFrame(fruit_data)
        st.subheader("🍇 Combined Nutrition Info")
        st.dataframe(df, use_container_width=True)

    # 🍹 Submit order to Snowflake
    if st.button("Submit Order"):
        try:
            session.sql(
                "INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER) VALUES (?, ?)",
                params=[ingredients_string, name_on_order]
            ).collect()
            st.success("✅ Your Smoothie has been ordered!")
        except Exception as e:
            st.error(f"❌ Something went wrong while saving order: {e}")

else:
    st.info("Please select up to 5 ingredients to create your smoothie.")
