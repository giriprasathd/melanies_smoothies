# Import packages
import streamlit as st
from snowflake.snowpark.context import get_active_session

# Connect to active Snowflake session
session = get_active_session()

# Title
st.title("🥤 Customize Your Smoothie Cup 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# Text input for smoothie name
name_on_order = st.text_input("Name your smoothie")
if name_on_order:
    st.write("Smoothie name:", name_on_order)

# Load fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select("FRUIT_NAME")
st.dataframe(my_dataframe)

# Multiselect
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    [row["FRUIT_NAME"] for row in my_dataframe.collect()],
    max_selections=5
)

# If ingredients selected
if ingredients_list:
    ingredients_string = ""

    # 👇 Join fruits exactly as lab expects: “Apples, Lime, Ximenia ”
    for fruit_chosen in ingredients_list:
        if ingredients_string == "":
            ingredients_string = fruit_chosen
        else:
            ingredients_string = ingredients_string + ", " + fruit_chosen

    # Add trailing space for correct hash
    ingredients_string = ingredients_string + " "

    st.write("You chose:", ingredients_string)

    # 👇 Build SQL insert manually like you shared
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('""" + ingredients_string + """', '""" + name_on_order + """')
    """

    st.write(my_insert_stmt)  # Show the final SQL for debugging

    # Insert when button clicked
    time_to_insert = st.button("Submit Order")
    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success("✅ Your Smoothie has been ordered!")
        except Exception as e:
            st.error(f"❌ Error inserting order: {e}")
else:
    st.info("Please choose up to 5 ingredients.")
