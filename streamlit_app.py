# Import python packages
import streamlit as st
import subprocess, streamlit as st
st.write("✅ Python version:", subprocess.getoutput("python --version"))
st.write("✅ Installed packages:", subprocess.getoutput("pip freeze | grep snowflake"))
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be', name_on_order)

# Get active Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect('Choose up to 5 ingredients:', my_dataframe, max_selections=5)

if ingredients_list and name_on_order:
    # Combine selected fruits into a string
    ingredients_string = ' '.join(ingredients_list)

    # Prepare SQL insert statement with both columns
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Show the SQL for debugging
    # st.write("SQL to execute:", my_insert_stmt)

    # Button to submit order
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
