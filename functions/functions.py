import random, datetime
import pandas as pd
from langchain.llms import OpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain

def map_to_alphabet(digit_str):
    """
    Maps digits in a string to corresponding letters based on a predefined mapping.
    """
    digit_strs = ''.join(filter(str.isdigit, str(digit_str)))

    if not digit_str:
        return ''
    unique_digits = set(digit_strs)

    digit_to_letter = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J'}
    return ''.join([digit_to_letter[int(d)] for d in digit_strs])

def assign_time_label(hour):
    """
    Assigns a label based on the time of the day.
    """
    if hour < 12:
        return 'Morning'
    elif hour < 18:
        return 'Evening'
    else:
        return 'Night'

def find_birthday(year, month, day, df):
    """
    Finds birthdays in a DataFrame matching the given year, month, and day.
    """
    df['Birthday'] = pd.to_datetime(df['Birthday'])

    matching_birthday = df[(df['Birthday'].dt.month == month) & (df['Birthday'].dt.day == day) & (df['Birthday'].dt.year == year)]
    return matching_birthday

def top_ordered_items(person_id, df):
    """
    Retrieves the top 2 ordered items and their prices for a given person ID from a DataFrame.
    """
    person_df = df[df['Last 4 Card Digits'] == person_id]

    item_counts = person_df['Menu Item'].value_counts()
    item_prices = person_df.groupby('Menu Item')['Total'].sum()

    # Get the top 2 ordered items
    top_items = item_counts.head(2).index.tolist()
    top_prices = item_prices.nlargest(2).values.tolist()

    return top_items, top_prices

def get_discount(sp):
    """
    Retrieves the discount percentage based on the service package.
    """
    if sp == "Premium":
        discount_percent = 5
    elif sp == "Standard":
        discount_percent = 10
    elif sp == "Economy":
        discount_percent = 25
    else:
        discount_percent = 10

    return discount_percent

def extract_last_4_digits(df, target_name):
    """
    Extracts the last 4 digits of the card associated with a target name from a DataFrame.
    """
    try:
        last_4_digits = df.loc[df['Name'] == target_name, 'Last 4 Card Digits'].values[0]
        return last_4_digits
    except IndexError:
        return f"No information found for {target_name}"

def generate_birthdays(ungrouped):
    """
    Generates a list of random birthdays.
    """
    birthdays = []
    for _ in range(len(ungrouped)):
        year  = random.randint(1980, 2012)
        month = random.randint(1, 12)
        day   = random.randint(1, 28) 
        birthdays.append(datetime.date(year, month, day))
    return birthdays

def convert_to_orderwise(ungrouped):
    """
    Converts ungrouped order data to order-wise format.
    """
    ungrouped['Total'] = ungrouped['Total'].str.replace('[^\d.]', '', regex=True)
    ungrouped['Total'] = pd.to_numeric(ungrouped['Total'])

    ungrouped['Tip'] = ungrouped['Tip'].str.replace('[^\d.]', '', regex=True)
    ungrouped['Tip'] = pd.to_numeric(ungrouped['Tip'])

    ungrouped['Qty'] = ungrouped['Qty'].str.replace('[^\d.]', '', regex=True)
    ungrouped['Qty'] = pd.to_numeric(ungrouped['Qty'])

    grouped = ungrouped.groupby(['Last 4 Card Digits', 'Order Date']).agg({
        'Menu Item': lambda x: ', '.join(x), 'Qty' : 'sum' , 
        'Total': 'sum' , 'Tip': 'first'}).reset_index()
    grouped['Last 4 Card Digits'] = grouped['Last 4 Card Digits'].astype(str).str.split('.').str[0].str.zfill(4)

    return grouped


def initialize_chain(max_token):

    template = """
    You are a helpful marketing agent and content writer for restaurants that writes textual content like message, email etc for offers
    like discount offer, promotional offer, special day offer, birthday offer and items like item of the day, item of the week etc.

    Follow these instructions carefully while generating the content.
    - Do not generate any biased content that may offend any caste, race or nationality.

    User: {user_input}
    """

    prompt = PromptTemplate(
        input_variables=["user_input"],
        template=template
    )

    llm = OpenAI(
        model_name="gpt-3.5-turbo-1106",
        max_tokens=max_token,
        temperature=0.5,
        api_key = ""
    )

    chain = LLMChain(llm=llm, prompt=prompt, verbose=False)

    return chain

def birthday_message(format, name, birthday, top_items, initial_price, discount_percent, discounted_price):

    if format == "small message":
        output = "simple one paragraph text message"
        max_token = 92
    elif format == "email":
        output = "Subject, Message, From: AIO Team"
        max_token = 192

    query = f"""
    Generate a birthday offer message for the customer in {format} format using customer data from our restaurant.
    Congratulate the customer and give him discount message on his liked products as given in Customer Data.
    Do not do any further calculation, display prices given by me.

    Our Restaurant Name: AIO

    Customer Data is given below.
    Customer Name: {name}
    Birthday: {birthday}
    Bundle Items: {top_items}
    Total Price of items: {initial_price}
    Discount Percent: {discount_percent}
    After Discount Price: {discounted_price}

    Output Format : {output}
    """

    chain = initialize_chain(max_token)
    return chain.predict(user_input=query)

def special_day_offer(format, name, occasion, top_items, initial_price, discount_percent, discounted_price):

    if format == "small message":
        output = "simple one paragraph text message"
        max_token = 92
    elif format == "email":
        output = "Subject, Message, \nRegards, \nAIO Team"
        max_token = 192

    query = f"""
    Generate a special day offer message for customers in {format} format using information regarding the Special Occasion and general customer data from our restaurant.
    Congratulate and give discount message on the most selling products from our restaurant as given in below data. Do not do any further calculation, display prices given by me.

    Our Restaurant Name: AIO

    Occasion Data is given below.
    Customer Name: {name}
    Special Occasion: {occasion}
    Most Selling Items: {top_items}
    Total Price of items: {initial_price}
    Discount Percent: {discount_percent}
    After Discount Price: {discounted_price}

    Output Format : {output}
    """

    chain = initialize_chain(max_token)
    return chain.predict(user_input=query)

def cluster_based_offer(format, name, top_items, initial_price, discount_percent, discounted_price):

    if format == "small message":
        output = "simple one paragraph text message"
        max_token = 92
    elif format == "email":
        output = "Subject, Message, \nRegards, \nAIO Team"
        max_token = 192

    query = f"""
    Generate a special offer message for the customer in {format} format using customer data from our restaurant.
    Invite the customer and give him discount message on his liked products as given in Customer Data.
    Do not do any further calculation, display prices given by me.

    Our Restaurant Name: AIO

    Occasion Data is given below.
    Customer Name: {name}
    Most Liked Items: {top_items}
    Total Price of items: {initial_price}
    Discount Percent: {discount_percent}
    After Discount Price: {discounted_price}

    Output Format : {output}
    """

    chain = initialize_chain(max_token)
    return chain.predict(user_input=query)

def churn_message(format, name, top_items, initial_price, discount_percent, discounted_price):

    if format == "small message":
        output = "simple one paragraph text message"
        max_token = 92
    elif format == "email":
        output = "Subject, Message, From: AIO Team"
        max_token = 192

    query = f"""
    Generate a customer retention message for the customer in {format} format using customer data from our restaurant.
    Tell him that we Express Gratitude that they were our customer, Highlight their Value, and give them personalized discount offer using below data.
    Do not do any further calculation, display prices gien by me.

    Our Restaurant Name: AIO

    Customer Data is given below.
    Customer Name: {name}
    Favorite Items: {top_items}
    Actual Price: {initial_price}
    Discount Percent: {discount_percent}
    After Discount Price: {discounted_price}

    Output Format : {output}
    """

    chain = initialize_chain(max_token)
    return chain.predict(user_input=query)

def top_item_finder():
    """
    Finds the top items and their prices from the item data.
    """
    # Item Data to get the price and categoy of the Items
    item_data = pd.read_excel('data/Campbell Menu Data - 2.xlsx', index_col=0)

    # Rename the column 'itemName' to 'Menu Item'
    item_data.rename(columns={"itemName": "Menu Item"}, inplace=True)
    ungrouped_data = pd.read_csv('data/Churn.csv', index_col=0)
    category_dict = item_data.groupby('Category')['Menu Item'].apply(list).to_dict()
    itemp = item_data.groupby('Menu Item')['itemPrice'].apply(list).to_dict()

    # Splitting Menu Item and creating new rows
    df_split = ungrouped_data.assign(Menu_Item=ungrouped_data['Menu Item'].str.split(', ')).explode('Menu_Item')

    # Dropping original 'Menu Item' column
    df_split.drop(columns='Menu Item', inplace=True)
    # Renaming the column
    df_split.rename(columns={'Menu_Item': 'Menu Item'}, inplace=True)
    df_split = df_split[['Menu Item', 'Qty', 'Total', 'Tip', 'Date_x', 'Time']]

    for category, items in category_dict.items():
        df_split.loc[df_split['Menu Item'].isin(items), 'Category'] = category

    for item, price in itemp.items():
        df_split.loc[df_split['Menu Item'] == item, 'ItemPrice'] = price[0]

    top_items = []
    for cat in ['Burgers & Sandwiches','Flights Cocktails','Brunch Food','Desserts']:
        top_items.append(list(df_split[df_split.Category == cat]['Menu Item'].value_counts().to_dict().keys())[0])

    top_items = list(set(top_items))
    prices = []
    for i in top_items:
        prices.append(df_split[df_split['Menu Item'] == i].ItemPrice.values[0])

    return top_items, prices

def churn_verifier(ungrouped_data, val):
    """
    Verifies customer churn and returns top recurring items and their prices for a specific customer.
    """
    df1 = pd.read_csv('data/Churn.csv', index_col=0)

    # Splitting Menu Item and creating new rows
    df = df1.assign(Menu_Item=ungrouped_data['Menu Item'].str.split(', ')).explode('Menu_Item')

    # Dropping original 'Menu Item' column
    df.drop(columns='Menu Item', inplace=True)
    df.rename(columns={'Menu_Item': 'Menu Item'}, inplace=True)
    customer_item_counts = df.groupby(['Last 4 Card Digits', 'Menu Item']).size().reset_index(name='Item_Count')

    # Sort the DataFrame based on the item count in descending order
    customer_item_counts = customer_item_counts.sort_values(by='Item_Count', ascending=False)

    # Create an empty DataFrame to store the top two recurring items for each customer
    top_recurring_items = pd.DataFrame(columns=['Last 4 Card Digits', 'Menu Item', 'Item_Count'])

    # Iterate over each customer and get their top two recurring items
    unique_customers = customer_item_counts['Last 4 Card Digits'].unique()
    for customer_id in unique_customers:
        customer_items = customer_item_counts[customer_item_counts['Last 4 Card Digits'] == customer_id]
        top_two_items = customer_items.nlargest(2, 'Item_Count')  # Select top two items
        top_recurring_items = top_recurring_items.append(top_two_items)

    # Reset the index of the final DataFrame
    top_recurring_items.reset_index(drop=True, inplace=True)
    top_recurring_items=top_recurring_items[top_recurring_items['Last 4 Card Digits']==val]


    item_data = pd.read_excel('data/Campbell Menu Data - 2.xlsx', index_col=0)
    item_data.rename(columns={"itemName": "Menu Item"}, inplace=True)
    category_dict = item_data.groupby('Category')['Menu Item'].apply(list).to_dict()
    for category, items in category_dict.items():
        top_recurring_items.loc[top_recurring_items['Menu Item'].isin(items), 'Category'] = category

    itemp = item_data.groupby('Menu Item')['itemPrice'].apply(list).to_dict()
    for item, price in itemp.items():
        top_recurring_items.loc[top_recurring_items['Menu Item'] == item, 'ItemPrice'] = price[0]

    return top_recurring_items['Menu Item'].values,top_recurring_items['ItemPrice'].values