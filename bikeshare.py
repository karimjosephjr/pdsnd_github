import time
import pandas as pd

CITY_DATA = {'Chicago': 'chicago.csv',
             'New York City': 'new_york_city.csv',
             'Washington': 'washington.csv'}

CITIES = {'Chicago': ['1', 'chicago'],
          'New York City': ['2', 'new york city', 'nyc', 'ny', 'new york'],
          'Washington': ['3', 'washington', 'dc', 'd.c.']}

MONTHS = {'All Months': ['0', 'all'],
          'January': ['1', 'jan'],
          'February': ['2', 'feb'],
          'March': ['3', 'mar'],
          'April': ['4', 'apr'],
          'May': ['5', 'may'],
          'June': ['6', 'jun'],
          'July': ['7', 'jul'],
          'August': ['8', 'aug'],
          'September': ['9', 'sep'],
          'October': ['10', 'oct'],
          'November': ['11', 'nov'],
          'December': ['12', 'dec']}

DAYS = {'All Days': ['0', 'a', 'all'],
        'Monday': ['1', 'm', 'mon'],
        'Tuesday': ['2', 't', 'tue'],
        'Wednesday': ['3', 'w', 'wed'],
        'Thursday': ['4', 'r', 'thu'],
        'Friday': ['5', 'f', 'fri'],
        'Saturday': ['6', 's', 'sat'],
        'Sunday': ['7', 'y', 'sun']}


# Was looking for something like Scala/Spark .flatten()
# Modified for sets
# https://stackoverflow.com/a/952952
def flatten(key_list_dict):
    """
    Flattens all the list of lists created from a {k: [v...]}.
    :param key_list_dict: A dictionary whose values are a list
    :return: A single list of all dictionary sub-list values
    """
    return [item for sub_values in key_list_dict.values() for item in sub_values]


# Make sure there are no duplicate values in each set of options
for i in [CITIES, MONTHS, DAYS]:
    flattened_input_options = flatten(i)
    assert (len(flattened_input_options) == len(set(flattened_input_options)))


def create_valid_lookup(valid_inputs):
    """
    Generates an inverted dictionary.
    :param valid_inputs: A dictionary of structure {K1: [V1 ... Vn], Kn...} where all list values are unique
    :return: {V1: K1, Vn: K1...}
    """
    valid_lookup = {}
    for k, vs in valid_inputs.items():
        for v in vs:
            valid_lookup[v] = k
    return valid_lookup


def confirm_selection(match):
    """
    A prompt to confirm the key match is what the user wants
    :param match: The string to confirm for selection
    :return: The original string or an empty string
    """
    confirmation = ''
    while len(confirmation) < 1:
        confirmation = input("Please confirm you would like to select '{}' [y/n]: ".format(match)).strip().lower()
        if len(confirmation) > 0:
            if confirmation[:1] == 'y':
                return match
            elif confirmation[:1] == 'n':
                return ''
            else:
                confirmation = ''


def validate_user_input(request, valid_inputs, trim=0):
    """
    An 'input' wrapper to clean and validate cities, months, and days requests
    :param request: Prompt for user input
    :param valid_inputs: Dictionary of {output: [acceptable_user_input]}
    :param trim: A length to trim user input by to make validation more straightforward
    :return: A key from the valid_inputs dictionary
    """
    valid_lookup = create_valid_lookup(valid_inputs)
    output = ''
    valid_list = [k for k in valid_inputs.keys()]
    attempted = False

    while output not in valid_list:
        if attempted:
            print('Unable to find a match. Please try again.')
        user_input = input(request).strip().lower()
        if user_input == 'options':
            attempted = False
            for k, v in valid_inputs.items():
                print('{}: {}, {}'.format(k, k, ', '.join(v)))
        else:
            attempted = True
            if len(user_input) > trim > 0:
                user_input = user_input[:trim]
            output = valid_lookup.get(user_input, '')
        if len(output) > 0:
            attempted = False
            output = confirm_selection(output)

    return output


def get_filters():
    """
    Asks user to specify a city, month, and day to analyze
    :return: (city, month, day) to be analyzed
    """
    print("Hello! Let's explore some US bikeshare data!")
    print("Type 'options' for options at any time.")
    # get user input for city (chicago, new york city, washington). HINT: Use a while loop to handle invalid inputs
    city = validate_user_input('\nWould you like to review Chicago, New York City, or Washington data? ', CITIES)

    # get user input for month (all, january, february, ... , june)
    month = validate_user_input('\nWhat month would you like to review? ', MONTHS, 3)

    # get user input for day of week (all, monday, tuesday, ... sunday)
    day = validate_user_input('\nWhat day of the week would you like to review? ', DAYS, 3)

    print('-' * 40)
    return city, month, day


def load_data(city, month, day):
    """
    Loads data for the specified city, filters by month and day if applicable, and adds columns for easy query
    :param city: name of the city to analyze
    :param month: name of the month to filter by, or 'All Months' to apply no month filter
    :param day: name of the day of week to filter by, or 'All Days' to apply no day filter
    :return: Pandas DataFrame containing city data filtered by month and day
    """

    # Load city data
    df = pd.read_csv(CITY_DATA[city])

    # Setup columns for filtering
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    df['Month of Year'] = df['Start Time'].dt.month_name()
    df['Day of Week'] = df['Start Time'].dt.day_name()
    df['Start Hour'] = df['Start Time'].dt.hour
    df['End Time'] = pd.to_datetime(df['End Time'])

    # Filter using provided parameters and extra columns
    if month != 'All Months':
        df = df[df['Month of Year'] == month]
    if day != 'All Days':
        df = df[df['Day of Week'] == day]

    # Convenience column for station stats
    df['Start and End Station'] = df['Start Station'].str.cat(df['End Station'], sep=' - ')

    # Clean Birth Year if it's even available
    if 'Birth Year' in df.columns:
        df['Birth Year'] = df['Birth Year'].astype('Int64')

    return df


def time_stats(df):
    """Displays statistics on the most frequent times of travel."""

    print('\nCalculating The Most Frequent Times of Travel...\n')
    start_time = time.time()

    try:
        # display the most common month
        months = df['Month of Year'].mode()
        print('Most Common Month: {}'.format(months.to_numpy()))

        # display the most common day of week
        day_of_week = df['Day of Week'].mode()
        print('Most Common Day of Week: {}'.format(day_of_week.to_numpy()))

        # display the most common start hour
        start_hour = df['Start Hour'].mode()
        print('Most Common Start Hour: {}'.format(start_hour.to_numpy()))
    except Exception as err:
        print('Error collecting frequency stats. Moving on.\n')
        print(f'Unexpected {err=}, {type(err)=}')

    print('\nThis took {} seconds.'.format(time.time() - start_time))
    print('-' * 40)


def station_stats(df):
    """Displays statistics on the most popular stations and trip."""

    print('\nCalculating The Most Popular Stations and Trip...\n')
    start_time = time.time()

    try:
        # display most commonly used start station
        start_location = df['Start Station'].mode()
        print('Most Common Start Location: {}'.format(start_location.to_numpy()))

        # display most commonly used end station
        end_location = df['End Station'].mode()
        print('Most Common End Location: {}'.format(end_location.to_numpy()))

        # display most frequent combination of start station and end station trip
        location_combo = df['Start and End Station'].mode()
        print("Most Common 'Start - End' Locations: {}".format(location_combo.to_numpy()))
    except Exception as err:
        print('Error collecting station stats. Moving on.\n')
        print(f'Unexpected {err=}, {type(err)=}')

    print('\nThis took {} seconds.'.format(time.time() - start_time))
    print('-' * 40)


def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration."""

    print('\nCalculating Trip Duration...\n')
    start_time = time.time()

    try:
        # display total travel time
        total_travel = df['Trip Duration'].sum() / 60
        print('Total Travel Time (in Minutes): {}'.format(total_travel))

        # display mean travel time
        average_travel = df['Trip Duration'].mean() / 60
        print('Average Travel Time (in Minutes): {}'.format(average_travel))
    except Exception as err:
        print('Error collecting duration stats. Moving on.\n')
        print(f'Unexpected {err=}, {type(err)=}')

    print('\nThis took {} seconds.'.format(time.time() - start_time))
    print('-' * 40)


def user_stats(df):
    """Displays statistics on bikeshare users."""

    print('\nCalculating User Stats...\n')
    start_time = time.time()

    try:
        # Display counts of user types
        user_type_counts = df['User Type'].value_counts()
        print('User Counts by Account Type:')
        print(user_type_counts.to_string())
    except Exception as err:
        print('Error collecting account type stats. Moving on.\n')
        print(f'Unexpected {err=}, {type(err)=}')

    # Display counts of gender
    print('\nUser Counts by Gender:')
    try:
        gender_counts = df['Gender'].value_counts()
        print(gender_counts.to_string())
    except KeyError:
        print('Gender is not available for this given set of data.')
    except Exception as err:
        print(f'Unexpected {err=}, {type(err)=}')

    # Display earliest, most recent, and most common year of birth
    print('\nBirth Year Stats ->')
    try:
        earliest = df['Birth Year'].min()
        latest = df['Birth Year'].max()
        mode = df['Birth Year'].mode()
        print('Earliest Birth Year: {}'.format(earliest))
        print('Latest Birth Year: {}'.format(latest))
        print('Most Common Birth Year: {}'.format(mode.to_numpy()))  # to_numpy()
    except KeyError:
        print('Birth Year is not available for this given set of data.')
    except Exception as err:
        print(f'Unexpected {err=}, {type(err)=}')

    print('\nThis took {} seconds.'.format(time.time() - start_time))
    print('-' * 40)


def show_raw_data(df):
    index = 0
    while True and len(df.index) > 0:
        df = df.iloc[index * 5:, :]
        print_dataset = input('\nWould you like to review (the next) 5 records of the dataset [y/n]? ')
        if len(print_dataset) > 0 and print_dataset[:1].lower() == 'y':
            if len(df.index) > 0:
                print(df.head(5).to_string())
            index += 1
        else:
            break


def main():
    while True:
        city, month, day = get_filters()
        df = load_data(city, month, day)
        time_stats(df)
        station_stats(df)
        trip_duration_stats(df)
        user_stats(df)
        show_raw_data(df)

        restart = input('\nWould you like to restart [y/n]? ')
        if len(restart) < 1 or restart[:1].lower() != 'y':
            break


if __name__ == '__main__':
    main()
