# Import Python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# App title and description
st.title("🥤 Customize Your Smoothie Cup 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# Create Snowflake connection
conn = st.connection("snowflake")
session = conn.session()

# Input: Smoothie name
name_on_order = st.text_input("Name your smoothie")
if name_on_order:
    st.write("The name of the smoothie:", name_on_order)

# Fetch fruit options (FRUIT_NAME + SEARCH_ON)
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert to Pandas so we can display in Streamlit
pd_df = my_dataframe.to_pandas()

# ✅ Show both FRUIT_NAME and SEARCH_ON columns in Streamlit
st.subheader("🍓 Available Fruits and Their API Search Values")
st.dataframe(pd_df, use_container_width=True)

# Multiselect for fruit selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# When fruits are selected
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)
    st.write("You chose:", ingredients_string)

    # Submit button to store order
    if st.button("Submit Order"):
        try:
            session.sql(
                """
                INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER)
                VALUES (?, ?)
                """,
                params=[ingredients_string, name_on_order]
            ).collect()
            st.success("✅ Your smoothie has been ordered!")
        except Exception as e:
            st.error(f"❌ Something went wrong: {e}")

    # For each fruit, show nutrition information
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"].iloc[0]
        st.subheader(f"{fruit_chosen} Nutrition Information")

        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")

        if fruityvice_response.status_code == 200:
            data = fruityvice_response.json()
            st.json(data)
        else:
            st.error(f"❌ Failed to fetch data for {fruit_chosen}")
else:
    st.info("Please select up to 5 ingredients to create your smoothie.")
