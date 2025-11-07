import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
import requests

# Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be', name_on_order)

# Get active Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# ✅ Step 1: Add SEARCH_ON column and inspect
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
st.dataframe(my_dataframe, use_container_width=True)  # Debug view
st.stop()  # Pause here to inspect before moving forward

# ✅ Step 2: Convert Snowflake DataFrame to Pandas
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)  # Debug view
st.stop()  # Pause here to inspect pandas DataFrame

# ✅ Step 3: Multiselect using FRUIT_NAME
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Show selected ingredients
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        # Get SEARCH_ON value using loc + iloc
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        # Fetch nutrition info
        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            if response.status_code == 200:
                st.subheader(fruit_chosen + ' Nutrition Information')
                st.dataframe(response.json(), use_container_width=True)
            else:
                st.warning(f"Nutrition data not available for {fruit_chosen}")
        except Exception as e:
            st.warning(f"Could not retrieve nutrition data for {fruit_chosen}: {e}")

# ✅ Submit order if name and ingredients are provided
if ingredients_list and name_on_order:
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
