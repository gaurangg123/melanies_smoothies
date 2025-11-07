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

# Get FRUIT_NAME and SEARCH_ON columns from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Checkbox for FILLED status
filled_status = st.checkbox("Mark as Filled")

# Display selected fruits and fetch nutrition info
if ingredients_list:
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            if response.status_code == 200:
                st.dataframe(data=response.json(), use_container_width=True)
            else:
                st.warning("Nutrition data not found")
        except Exception:
            st.warning("Could not retrieve nutrition data")

# Submit order if name and ingredients are provided
if ingredients_list and name_on_order:
    st.markdown("---")
    
    # Build ingredients string with different separators to test
    ingredients_string = ' '.join([fruit.strip() for fruit in ingredients_list])
    
    # Try different possible correct formats
    test_formats = {
        'Space separated': ' '.join(ingredients_list),
        'Newline separated': '\n'.join(ingredients_list),
        'Comma separated': ','.join(ingredients_list),
        'Comma-space separated': ', '.join(ingredients_list),
    }
    
    st.markdown("### 🔍 Hash Testing (for debugging)")
    st.write("Try these formats to find which hash matches:")
    
    for format_name, test_string in test_formats.items():
        st.code(f"{format_name}: '{test_string}'")
        # Note: Can't calculate hash in Streamlit, but show the string
    
    st.info("💡 Copy each format above and test in Snowflake using: SELECT hash('paste_here_exactly')")
    
    st.markdown("### Order Summary")
    st.write(f"**Name:** {name_on_order}")
    st.write(f"**Ingredients:** {ingredients_string}")
    st.write(f"**Filled:** {'Yes' if filled_status else 'No'}")
    
    filled_sql_value = 'TRUE' if filled_status else 'FALSE'
    
    if st.button('Submit Order'):
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order, order_filled)
            VALUES ('{ingredients_string}', '{name_on_order}', {filled_sql_value})
        """
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
