from data_cleaner import *


def intro():
    import streamlit as st

    st.write("# Welcome to Streamlit! 👋")
    st.sidebar.success("Select a demo above.")

    st.markdown(
        """
        Streamlit is an open-source app framework built specifically for
        Machine Learning and Data Science projects.

        **👈 Select a demo from the dropdown on the left** to see some examples
        of what Streamlit can do!

        ### Want to learn more?

        - Check out [streamlit.io](https://streamlit.io)
        - Jump into our [documentation](https://docs.streamlit.io)
        - Ask a question in our [community
          forums](https://discuss.streamlit.io)

        ### See more complex demos

        - Use a neural net to [analyze the Udacity Self-driving Car Image
          Dataset](https://github.com/streamlit/demo-self-driving)
        - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
    """
    )

def viewMenu():
    pass

def buildApp(transaction_data, cur_balance_data, swipe_data):
    import streamlit as st
    # from dataParser import getData
    import pandas as pd
    import matplotlib.pyplot as plt
    import altair as alt
    # cur_balance_screen data
    card_dollars = cur_balance_data['Meal Plan Cardinal $']
    meals_left = cur_balance_data['15 Meal Plan']
    guest_left = cur_balance_data['Guest Meals - 5']

    # transactions_screen data
    raw_transaction_data = get_pos_transaction_data(transaction_data)
    grouped_location_spending_data = aggregate_loc_names(raw_transaction_data)
    total_spending = grouped_location_spending_data['Amount'].sum()

    #swipe_screen data
    raw_swipe_data = get_swipe_transaction_data(swipe_data)
    grouped_swipe_data = aggregate_swipe_names(raw_swipe_data)
    total_swipes = grouped_swipe_data['Amount'].sum()

    ############ SECTION 0: INTRO
    st.title('YOUR MEAL DATA')
    st.write(f"Total Amount Spent: ${total_spending:.2f}")
    st.write(f"Total # Swipes Used: {total_swipes}")

    st.button("Login to your Stanford (Google) Account")
    st.button("Clear Data")
    st.button("Example Dataset")

    ############ SECTION 1: ISOLATED METRICS
    # Streamlit app layout
    st.title('Your Info')
    st.write('Welcome to my Streamlit app!')

    # Create three columns
    col1, col2, col3 = st.columns(3)

    # Deltas
    delta_dollars = raw_transaction_data.sort_values(by='Timestamp', ascending=False).iloc[0]['Amount']
    # Display data in each column using st.metric
    display_column_number(col1, card_dollars, 'Cardinal Meal Plan Dollars Left', -delta_dollars)
    display_column_number(col2, meals_left, 'Number of Swipes Left', 0)
    display_column_number(col3, guest_left, 'Number of Guest Swipes Left', 0)

    ############ SECTION 2: Segmented Spending Bar
    st.title('Cardinal Dollars Spending by Location')

    # Pastel colors for each category
    num_categories = len(grouped_location_spending_data['Location'])
    pastel_colors = plt.cm.Pastel1(range(num_categories))
    # Segmented Total Spending Bar
    fig, ax = plt.subplots()
    grouped_location_spending_data.set_index('Location').T.plot(kind='bar', stacked=True, ax=ax, color=pastel_colors)
    ax.set_title('Total Spending: ${:.2f}'.format(total_spending))
    ax.set_ylabel('Amount Spent ($)')
    ax.set_xticks([])
    st.pyplot(fig)
    st.bar_chart(data=grouped_location_spending_data, x='Location', y='Amount', use_container_width=True)

    ############ SECTION 3: Timeseries Spending
    st.title('Cardinal Dollars Spending by Time')
    # Convert to DataFrame
    timeseries_data = get_timeseries_data(transaction_data)
    # Prepare data for area chart: resampling data by day and location
    area_chart_data = timeseries_data.set_index('Timestamp').groupby('Location').resample('D')['Amount'].sum().unstack(0, fill_value=0)
    # # Main Area Chart
    st.bar_chart(area_chart_data, use_container_width=True, height=600)

    ############ SECTION 4: Swipe Spending by Fraction
    # print(raw_swipe_data)
    # print(grouped_swipe_data)
    # print(total_swipes)
    st.title('Meal Swipes by Location')

    # Pastel colors for each category
    num_categories = len(grouped_swipe_data['Description'])
    pastel_colors = plt.cm.Pastel1(range(num_categories))
    # Segmented Total Spending Bar
    fig, ax = plt.subplots()
    grouped_swipe_data.set_index('Description').T.plot(kind='bar', stacked=True, ax=ax, color=pastel_colors)
    ax.set_title('Total Spending: ${:.2f}'.format(total_spending))
    ax.set_ylabel('Amount Spent ($)')
    ax.set_xticks([])
    st.pyplot(fig)
    st.bar_chart(data=grouped_swipe_data, x='Description', y='Amount', use_container_width=True)

    ############ SECTION 5: Swipe Spending overall Time Chart
    st.title('Overall Swipes by Time')
    df = get_timeseries_swipe_data(meal_data)
    # Aggregate data by Description and Date
    aggregated_data = df.groupby([df['Date'].dt.date, 'Description'])['Amount'].sum().reset_index()
    aggregated_data['Date'] = pd.to_datetime(aggregated_data['Date'])

    # Creating a bar chart with bars touching each other
    chart = alt.Chart(aggregated_data).mark_bar().encode(
        x=alt.X('Date:T', axis=alt.Axis(format='%Y-%m-%d'), scale=alt.Scale(padding=0)),
        y=alt.Y('Amount:Q'),
        color='Description:N',
        tooltip=['Date', 'Description', 'Amount']
    ).properties(width=700, height=400)

    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)

    ############ SECTION 6: Swipe Spending by Specific Time
    st.title('Meal Swipes by Date and Time')

    # Interactive widgets
    selected_date = st.date_input("Select a date", min_value=df['Date'].dt.date.min(), max_value=df['Date'].dt.date.max(),
                              value=df['Date'].dt.date.max())

    # Filtering data based on selection
    filtered_data = df[(df['Date'].dt.date == selected_date)]

    # Convert 'Timestamp' to a string formatted as 'hours:minutes:seconds'
    filtered_data['TimeString'] = filtered_data['Timestamp'].apply(lambda x: x.strftime('%H:%M:%S'))

    # Creating a bar chart
    chart = alt.Chart(filtered_data).mark_bar(size=20).encode(
        x=alt.X('TimeString:N', title='Time', axis=alt.Axis(labelAngle=0)),  # Use the formatted time string for the x-axis
        y=alt.Y('Amount:Q'),
        color='Description:N',
        tooltip=[
            alt.Tooltip('Date', title='Date', format='%Y-%m-%d'),
            'Description',
            'Amount',
            alt.Tooltip('Timestamp', title='Time', format='%H:%M:%S')
        ]
    ).properties(width=700, height=200)

    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)


if __name__ == '__main__':
    # Sample transaction data example
    transaction_data = [('11/01/2023 09:59:20 PM', 'The Axe & Palm Kiosk', '-$5.49'),
                        ('10/30/2023 11:48:57 PM', 'The Axe & Palm 3', '-$9.99'),
                        ('10/25/2023 11:34:04 PM', 'Late Night at Lakeside Kiosk2', '-$29.35'),
                        ('10/24/2023 11:59:12 PM', 'The Axe & Palm 2', '-$11.99'),
                        ('10/20/2023 12:59:13 AM', 'Late Night at Lakeside Kiosk2', '-$8.45'),
                        ('10/13/2023 12:58:09 AM', 'Late Night at Lakeside Kiosk2', '-$6.95'),
                        ('10/10/2023 11:23:00 PM', 'The Axe & Palm Kiosk', '-$7.99'),
                        ('10/08/2023 12:42:41 AM', 'The Axe & Palm 3', '-$10.99'),
                        ('10/03/2023 12:54:52 AM', 'Late Night at Lakeside 1', '-$7.50'),
                        ('10/01/2023 12:10:59 AM', 'The Axe & Palm 3', '-$7.99'),
                        ('09/19/2023 02:32:03 PM', 'System Transaction', '$110.00'),
                        ('09/15/2023 09:20:09 AM', 'System Transaction', '-$1.15')]

    # Sample data dictionary
    cur_balance_data = {'Plan Name': 'Balance',
                        'Meal Plan Cardinal $': '$3.31',
                        '15 Meal Plan': '7 Meals',
                        'Guest Meals - 5': '1 Meals'}

    # Sample meal data example
    meal_data = [('11/22/2023 05:21:43 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('11/22/2023 11:29:04 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('11/21/2023 12:31:10 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('11/20/2023 06:56:04 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('11/20/2023 12:37:52 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('11/19/2023 06:34:53 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('11/19/2023 10:47:39 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('11/18/2023 06:19:08 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('11/18/2023 10:14:47 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('11/17/2023 05:02:16 PM', 'Wilbur Dining 152', -1),
                 ('11/16/2023 06:39:02 PM', 'Lagunita Dining 158', -1),
                 ('11/16/2023 11:10:43 AM', 'Wilbur Dining 152', -1),
                 ('11/15/2023 12:37:54 PM', 'Wilbur Dining 152', -1),
                 ('11/14/2023 09:38:35 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('11/13/2023 05:57:55 PM', 'Wilbur Dining 152', -1),
                 ('11/13/2023 11:30:51 AM', 'Wilbur Dining 152', -1),
                 ('11/12/2023 10:48:54 AM', 'Wilbur Dining 152', -1),
                 ('11/11/2023 07:39:35 PM', 'Wilbur Dining 152', -1),
                 ('11/11/2023 10:47:20 AM', 'Wilbur Dining 152', -1),
                 ('11/10/2023 06:11:41 PM', 'Wilbur Dining 152', -1),
                 ('11/10/2023 12:28:12 PM', 'Wilbur Dining 152', -1),
                 ('11/09/2023 07:04:26 PM', 'Wilbur Dining 152', -1),
                 ('11/09/2023 01:27:08 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('11/08/2023 05:26:38 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('11/08/2023 11:36:31 AM', 'Wilbur Dining 152', -1),
                 ('11/08/2023 08:59:30 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('11/07/2023 12:08:03 PM', 'Wilbur Dining 152', -1),
                 ('11/07/2023 09:13:39 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('11/06/2023 05:41:37 PM', 'Wilbur Dining 152', -1),
                 ('11/06/2023 11:35:16 AM', 'Wilbur Dining 152', -1),
                 ('11/05/2023 10:36:24 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('11/04/2023 07:35:05 PM', 'Wilbur Dining 152', -1),
                 ('11/04/2023 12:06:17 PM', 'Wilbur Dining 152', -1),
                 ('11/03/2023 07:14:40 PM', 'Wilbur Dining 152', -1),
                 ('11/03/2023 11:10:40 AM', 'Wilbur Dining 152', -1),
                 ('11/02/2023 05:41:58 PM', 'Wilbur Dining 152', -1),
                 ('11/02/2023 11:03:14 AM', 'Wilbur Dining 152', -1),
                 ('11/01/2023 01:45:59 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('11/01/2023 08:57:59 AM', 'Wilbur Dining 152', -1),
                 ('10/31/2023 02:57:44 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/31/2023 10:07:31 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/30/2023 10:30:33 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/29/2023 06:41:38 PM', 'Wilbur Dining 152', -1),
                 ('10/29/2023 11:12:24 AM', 'Wilbur Dining 152', -1),
                 ('10/28/2023 06:34:29 PM', 'Wilbur Dining 152', -1),
                 ('10/28/2023 10:31:41 AM', 'Wilbur Dining 152', -1),
                 ('10/27/2023 07:13:34 PM', 'Wilbur Dining 152', -1),
                 ('10/27/2023 12:36:00 PM', 'Lagunita Dining 158', -1),
                 ('10/27/2023 09:16:51 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/26/2023 07:35:48 PM', 'Wilbur Dining 152', -1),
                 ('10/26/2023 09:16:03 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/25/2023 06:35:48 PM', 'Wilbur Dining 152', -1),
                 ('10/25/2023 09:19:51 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/24/2023 05:06:06 PM', 'Wilbur Dining 152', -1),
                 ('10/24/2023 09:39:14 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/23/2023 12:11:05 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/23/2023 08:57:57 AM', 'Wilbur Dining 152', -1),
                 ('10/22/2023 07:10:26 PM', 'Wilbur Dining 152', -1),
                 ('10/22/2023 10:28:46 AM', 'Wilbur Dining 152', -1),
                 ('10/20/2023 06:27:55 PM', 'Wilbur Dining 152', -1),
                 ('10/20/2023 02:41:45 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/20/2023 10:00:03 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/19/2023 06:32:14 PM', 'Wilbur Dining 152', -1),
                 ('10/19/2023 01:26:32 PM', 'Wilbur Dining 152', -1),
                 ('10/19/2023 08:24:49 AM', 'Wilbur Dining 152', -1),
                 ('10/18/2023 05:51:06 PM', 'Wilbur Dining 152', -1),
                 ('10/18/2023 11:31:15 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/17/2023 07:51:59 PM', 'Wilbur Dining 152', -1),
                 ('10/17/2023 03:00:22 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/16/2023 06:03:54 PM', 'Wilbur Dining 152', -1),
                 ('10/16/2023 01:04:17 PM', 'Wilbur Dining 152', -1),
                 ('10/16/2023 09:13:07 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/15/2023 05:35:10 PM', 'Wilbur Dining 153', -1),
                 ('10/15/2023 10:59:07 AM', 'Wilbur Dining 152', -1),
                 ('10/14/2023 05:49:34 PM', 'Wilbur Dining 152', -1),
                 ('10/14/2023 02:39:39 PM', 'Wilbur Dining 152', -1),
                 ('10/13/2023 10:08:55 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/12/2023 06:53:55 PM', 'Stern Dining 150', -1),
                 ('10/12/2023 11:14:42 AM', 'Wilbur Dining 152', -1),
                 ('10/11/2023 07:09:03 PM', 'Wilbur Dining 152', -1),
                 ('10/11/2023 08:28:24 AM', 'Wilbur Dining 152', -1),
                 ('10/10/2023 05:21:21 PM', 'Wilbur Dining 152', -1),
                 ('10/10/2023 09:56:49 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/09/2023 09:51:52 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/08/2023 11:04:34 AM', 'Wilbur Dining 152', -1),
                 ('10/07/2023 07:30:25 PM', 'Wilbur Dining 152', -1),
                 ('10/06/2023 05:10:33 PM', 'Wilbur Dining 153', -1),
                 ('10/06/2023 10:08:27 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/05/2023 06:29:30 PM', 'Wilbur Dining 152', -1),
                 ('10/05/2023 11:14:37 AM', 'Wilbur Dining 152', -1),
                 ('10/04/2023 05:33:21 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/04/2023 12:45:24 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/03/2023 05:02:09 PM', 'Wilbur Dining 152', -1),
                 ('10/03/2023 03:01:27 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('10/03/2023 08:52:56 AM', 'Wilbur Dining 152', -1),
                 ('10/02/2023 05:02:19 PM', 'Wilbur Dining 152', -1),
                 ('10/02/2023 11:33:18 AM', 'Wilbur Dining 152', -1),
                 ('10/02/2023 08:32:09 AM', 'Wilbur Dining 152', -1),
                 ('10/01/2023 05:45:54 PM', 'Wilbur Dining 152', -1),
                 ('10/01/2023 10:23:40 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('09/30/2023 06:23:58 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('09/30/2023 11:21:20 AM', 'Wilbur Dining 152', -1),
                 ('09/29/2023 07:09:20 PM', 'Wilbur Dining 152', -1),
                 ('09/29/2023 11:33:23 AM', 'Wilbur Dining 152', -1),
                 ('09/28/2023 07:31:00 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('09/27/2023 05:12:06 PM', 'Wilbur Dining 152', -1),
                 ('09/27/2023 11:32:25 AM', 'Wilbur Dining 152', -1),
                 ('09/27/2023 09:10:53 AM', 'Arrillaga Fam Din Commons 162', -1),
                 ('09/26/2023 01:58:34 PM', 'Arrillaga Fam Din Commons 162', -1),
                 ('09/26/2023 08:48:31 AM', 'Wilbur Dining 152', -1),
                 ('09/25/2023 06:09:08 PM', 'Wilbur Dining 152', -1),
                 ('09/25/2023 08:44:59 AM', 'Wilbur Dining 152', -1)]

    page_names_to_funcs = {
        "-": intro,
        "Today's Menu": viewMenu(),
        "Your Meal Data": buildApp,
    }

    demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
    if demo_name == "Your Meal Data":
        page_names_to_funcs[demo_name](transaction_data, cur_balance_data, meal_data)
    else:
        page_names_to_funcs[demo_name]()

    # buildApp(transaction_data, cur_balance_data, meal_data)