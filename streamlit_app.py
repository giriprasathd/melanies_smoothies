# Import Python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

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
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]  # Convert to Python list

# Show available fruits
st.dataframe(data=my_dataframe, use_container_width=True)

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

    # Submit order button
    if st.button("Submit Order"):
        try:
            session.sql(
                "INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER) VALUES (?, ?)",
                params=[ingredients_string, name_on_order]
            ).collect()
            st.success("✅ Your Smoothie has been ordered!")
        except Exception as e:
            st.error(f"❌ Something went wrong: {e}")

    # Convert Snowpark DataFrame to Pandas for lookup
    pd_df = my_dataframe.to_pandas()

    # Loop through selected fruits and show nutrition info
    for fruit_chosen in ingredients_list:
        # Get the SEARCH_ON value for the chosen fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f"The search value for {fruit_chosen} is {search_on}.")
        
        # Display fruit nutrition info
        st.subheader(f"{fruit_chosen} Nutrition Information")
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        
        if fruityvice_response.status_code == 200:
            fruityvice_df = fruityvice_response.json()
            st.dataframe(data=fruityvice_df, use_container_width=True)
        else:
            st.error(f"❌ Failed to fetch data for {fruit_chosen}")

else:
    st.info("Please select up to 5 ingredients to create your smoothie.")
