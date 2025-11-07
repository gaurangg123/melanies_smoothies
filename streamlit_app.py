import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be', name_on_order)

# Get active Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options with SEARCH_ON column
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert to Pandas for the multiselect
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:', 
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Get the search term for this fruit from the pandas dataframe
        search_row = pd_df[pd_df['FRUIT_NAME'] == fruit_chosen]
        
        if not search_row.empty:
            search_term = search_row.iloc[0]['SEARCH_ON']
            
            # Get nutrition data using the search term
            try:
                smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_term}")
                
                if smoothiefroot_response.status_code == 200:
                    st.subheader(fruit_chosen + ' Nutrition Information')
                    st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
                else:
                    st.warning(f"Nutrition data not available for {fruit_chosen}")
            except:
                st.warning(f"Could not retrieve nutrition data for {fruit_chosen}")

if ingredients_list and name_on_order:
    # Prepare SQL insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """
    
    # Button to submit order
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
