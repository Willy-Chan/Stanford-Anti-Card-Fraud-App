import pandas as pd
import altair as alt
import streamlit as st

# def display_column_number(col, number, description):
#     # Using Markdown with custom HTML and CSS for large numbers and descriptions
#     col.markdown(f"<h1 style='text-align: center; color: white; font-size: 60px;'>{number}</h1>",
#                  unsafe_allow_html=True)
#     col.markdown(f"<h4 style='text-align: center; color: gray;'>{description}</h4>", unsafe_allow_html=True)
#     col.markdown("<hr style='height: 2px; margin: 10px 0;'>", unsafe_allow_html=True)  # Horizontal line

# Function to display number, description, and delta using st.metric
def display_column_number(col, number, description, *delta):
    col.metric(label=description, value=number, delta=delta[0])

# Function to group locations
def group_location(location):
    if 'Late Night at Lakeside' in location:
        return 'Late Night at Lakeside'
    elif 'The Axe & Palm' in location:
        return 'The Axe & Palm'
    elif 'Arrillaga' in location:
        return 'Arrillaga'
    elif 'Wilbur' in location:
        return 'Wilbur'
    elif 'Lagunita' in location:
        return 'Lagunita'
    else:
        return 'Other'


def get_pos_transaction_data(transaction_data):
    df = pd.DataFrame(transaction_data, columns=['Timestamp', 'Location', 'Amount'])
    df['Amount'] = df['Amount'].replace('[\$,]', '', regex=True).astype(float)
    df['Location'] = df['Location'].apply(group_location)

    # Filter out positive values and invert amounts
    df = df[df['Amount'] < 0]
    df['Amount'] = df['Amount'].abs()
    return df

def get_timeseries_data(transaction_data):
    df = pd.DataFrame(transaction_data, columns=['Timestamp', 'Location', 'Amount'])
    df['Amount'] = df['Amount'].replace('[\$,]', '', regex=True).astype(float)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # Filter out positive values and invert amounts
    df = df[df['Amount'] < 0]
    df['Amount'] = df['Amount'].abs()
    return df

def aggregate_loc_names(data):
    spending_by_grouped_location = data.groupby('Location')['Amount'].sum().reset_index()
    spending_by_grouped_location = spending_by_grouped_location.sort_values(by='Amount')
    return spending_by_grouped_location



### SWIPE PARSING
def get_swipe_transaction_data(transaction_data):
    df = pd.DataFrame(transaction_data, columns=['Date', 'Description', 'Amount'])
    df['Description'] = df['Description'].apply(group_location)

    # Filter out positive values and invert amounts
    df = df[df['Amount'] < 0]
    df['Amount'] = df['Amount'].abs()
    return df

def get_timeseries_swipe_data(transaction_data):
    df = pd.DataFrame(transaction_data, columns=['Date', 'Description', 'Amount'])
    df['Amount'] = df['Amount'].replace('[\$,]', '', regex=True).astype(float)
    df['Date'] = pd.to_datetime(df['Date'])

    # Extract just the time part from the Date column
    df['Timestamp'] = df['Date'].dt.time

    # Filter out positive values and invert amounts
    df = df[df['Amount'] < 0]
    df['Amount'] = df['Amount'].abs()
    return df


def aggregate_swipe_names(data):
    spending_by_grouped_location = data.groupby('Description')['Amount'].sum().reset_index()
    return spending_by_grouped_location
