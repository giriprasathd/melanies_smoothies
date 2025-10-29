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

# Fetch fruit options (with SEARCH_ON) from Snowflake
fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]  # Convert to Python list

# Show available fruits
st.dataframe(data=fruit_df, use_container_width=True)

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

if ingredients_list:
    # Convert Snowpark DataFrame to Pandas for easy lookup
    pd_df = fruit_df.to_pandas()

    # Clean ingredient names
    clean_ingredients = [fruit.strip() for fruit in ingredients_list]

    # Format ingredients like 'Apples','Lime','Ximenia'
    ingredients_string = ",".join(f"'{fruit}'" for fruit in clean_ingredients)

    # Display info for each fruit
    for fruit_chosen in clean_ingredients:
        # Fetch corresponding search name
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        st.write(f"🔍 The search value for **{fruit_chosen}** is **{search_on}**")
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # FruityVice API call using SEARCH_ON
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")

        if fruityvice_response.status_code == 200:
            fruityvice_normalized = pd.json_normalize(fruityvice_response.json())
            st.dataframe(fruityvice_normalized, use_container_width=True)
        else:
            st.error(f"❌ Failed to fetch data for {fruit_chosen}")

    # Show formatted ingredients
    st.write("🧾 Ingredients string (for SQL insert):")
    st.code(ingredients_string)

    # When user submits order
    if st.button("Submit Order"):
        try:
            # Insert into orders table safely
            session.sql(
                "INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER) VALUES (?, ?)",
                params=[ingredients_string, name_on_order]
            ).collect()
            st.success("✅ Your Smoothie has been ordered!")
        except Exception as e:
            st.error(f"❌ Something went wrong: {e}")

else:
    st.info("Please select up to 5 ingredients to create your smoothie.")
