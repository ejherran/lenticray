import pandas as pd

from dateutil.relativedelta import relativedelta

from system.commons import enums


def process_data_in_temporal_space(dataset, temporal_space):
    # Copy dataset
    internal_dataset = dataset.copy()

    # Convert 'Sample Date' to datetime format
    internal_dataset['Sample Date'] = pd.to_datetime(internal_dataset['Sample Date'])

    # Process data based on temporal space
    if temporal_space == enums.TemporalSpace.MONTHLY:
        return process_monthly_data(internal_dataset)

    if temporal_space == enums.TemporalSpace.WEEKLY:
        return process_weekly_data(internal_dataset)

    if temporal_space == enums.TemporalSpace.DAILY:
        return process_daily_data(internal_dataset)

def process_monthly_data(internal_dataset):
    # Extract Year and Month from 'Sample Date'
    internal_dataset['Year'] = internal_dataset['Sample Date'].dt.year
    internal_dataset['Month'] = internal_dataset['Sample Date'].dt.month

    # Create an empty DataFrame to store the results
    all_data = pd.DataFrame()

    # Process each Water Body separately
    for body, body_data in internal_dataset.groupby('Water Body'):
        # Group by Year and Month, calculating the mean for each group excluding non-numeric columns
        monthly_data = body_data.groupby(['Year', 'Month']).mean(numeric_only=True).reset_index()

        # Create a complete range of months from the minimum to the maximum date for this station
        start_date = body_data['Sample Date'].min() - relativedelta(months=1)  # Subtract one month from the start date
        end_date = body_data['Sample Date'].max()

        # Generate a complete date range with one entry per month
        all_months = pd.date_range(start=start_date, end=end_date, freq='MS')
        all_months_df = pd.DataFrame({'Year': all_months.year, 'Month': all_months.month})

        # Merge with the monthly data to ensure all months are represented, filling missing values with NaN
        body_monthly_data = pd.merge(all_months_df, monthly_data, on=['Year', 'Month'], how='left', sort=True)

        # Add the 'Water Body' column
        body_monthly_data['Water Body'] = body

        # Append to the overall DataFrame
        all_data = pd.concat([all_data, body_monthly_data], ignore_index=True)

    # Reorder columns to place 'Water Body' at the beginning
    columns_order = ['Water Body', 'Year', 'Month'] + [col for col in all_data.columns if col not in ['Water Body', 'Year', 'Month']]
    all_data = all_data[columns_order]

    return all_data

def process_weekly_data(internal_dataset):
    # Extract Year and Week from 'Sample Date'
    internal_dataset['Year'] = internal_dataset['Sample Date'].dt.isocalendar().year
    internal_dataset['Week'] = internal_dataset['Sample Date'].dt.isocalendar().week

    # Create an empty DataFrame to store the results
    all_data = pd.DataFrame()

    # Process each Water Body separately
    for body, body_data in internal_dataset.groupby('Water Body'):
        # Group by Year and Week, calculating the mean for each group excluding non-numeric columns
        weekly_data = body_data.groupby(['Year', 'Week']).mean(numeric_only=True).reset_index()

        # Create a complete range of weeks from the minimum to the maximum date for this station
        start_date = body_data['Sample Date'].min() - pd.DateOffset(weeks=1)  # Subtract one week from the start date
        end_date = body_data['Sample Date'].max()

        # Generate a complete date range with one entry per week (Monday as the start of the week)
        all_weeks = pd.date_range(start=start_date, end=end_date, freq='W-MON')
        all_weeks_df = pd.DataFrame({'Year': all_weeks.isocalendar().year, 'Week': all_weeks.isocalendar().week})

        # Merge with the weekly data to ensure all weeks are represented, filling missing values with NaN
        body_weekly_data = pd.merge(all_weeks_df, weekly_data, on=['Year', 'Week'], how='left', sort=True)

        # Add the 'Water Body' column
        body_weekly_data['Water Body'] = body

        # Append to the overall DataFrame
        all_data = pd.concat([all_data, body_weekly_data], ignore_index=True)

    # Reorder columns to place 'Water Body' at the beginning
    columns_order = ['Water Body', 'Year', 'Week'] + [col for col in all_data.columns if col not in ['Water Body', 'Year', 'Week']]
    all_data = all_data[columns_order]

    return all_data

def process_daily_data(internal_dataset):
    # Extract Year, Month, and Day from 'Sample Date'
    internal_dataset['Year'] = internal_dataset['Sample Date'].dt.year
    internal_dataset['Month'] = internal_dataset['Sample Date'].dt.month
    internal_dataset['Day'] = internal_dataset['Sample Date'].dt.day

    # Create an empty DataFrame to store the results
    all_data = pd.DataFrame()

    # Process each Water Body separately
    for body, body_data in internal_dataset.groupby('Water Body'):
        # Group by Year, Month, and Day, calculating the mean for each group excluding non-numeric columns
        daily_data = body_data.groupby(['Year', 'Month', 'Day']).mean(numeric_only=True).reset_index()

        # Create a complete range of days from the minimum to the maximum date for this station
        start_date = body_data['Sample Date'].min()
        end_date = body_data['Sample Date'].max()

        # Generate a complete date range with one entry per day
        all_days = pd.date_range(start=start_date, end=end_date, freq='D')
        all_days_df = pd.DataFrame({'Year': all_days.year, 'Month': all_days.month, 'Day': all_days.day})

        # Merge with the daily data to ensure all days are represented, filling missing values with NaN
        body_daily_data = pd.merge(all_days_df, daily_data, on=['Year', 'Month', 'Day'], how='left', sort=True)

        # Add the 'Water Body' column
        body_daily_data['Water Body'] = body

        # Append to the overall DataFrame
        all_data = pd.concat([all_data, body_daily_data], ignore_index=True)

    # Reorder columns to place 'Water Body' at the beginning
    columns_order = ['Water Body', 'Year', 'Month', 'Day'] + [col for col in all_data.columns if col not in ['Water Body', 'Year', 'Month', 'Day']]
    all_data = all_data[columns_order]

    return all_data
