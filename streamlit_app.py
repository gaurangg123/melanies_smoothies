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

# ✅ Get FRUIT_NAME and SEARCH_ON columns
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# ✅ Convert to Pandas
pd_df = my_dataframe.to_pandas()

# ✅ Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Checkbox for FILLED status
filled_status = st.checkbox("Mark as Filled")

# ✅ Display selected fruits and fetch info
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        # Get SEARCH_ON value using loc + iloc
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Show nutrition info header
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Fetch nutrition info
        try:
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            if smoothiefroot_response.status_code == 200:
                st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            else:
                st.warning("Nutrition data not found")
        except Exception:
            st.warning("Could not retrieve nutrition data")

# ✅ Submit order if name and ingredients are provided
if ingredients_list and name_on_order:
    st.markdown("---")
    st.markdown("### Order Summary")
    st.write(f"**Name:** {name_on_order}")
    st.write(f"**Ingredients:** {', '.join(ingredients_list)}")
    st.write(f"**Filled:** {'Yes' if filled_status else 'No'}")

    # Convert checkbox to SQL literal
    filled_sql_value = 'TRUE' if filled_status else 'FALSE'

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order, filled)
            VALUES ('{ingredients_string.strip()}', '{name_on_order}', {filled_sql_value})
        """
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
