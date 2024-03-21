def combine_last_4_cols(row):
    """
    Combines the last 4 columns of a row into a list.
    """
    return row[1:].tolist()

def combine_last_18_cols(row):
    """
    Combines the last 18 columns of a row into a list.
    """
    return row[1:].tolist()

def count_visits(date_list):
    """
    Calculates the number of visits based on a list of dates.
    """
    return len(date_list)

def get_first_date(date_list):
    """
    Extracts the first date from a list of dates.
    """
    return min(date_list)

def get_last_date(date_list):
    """
    Extracts the last date from a list of dates.
    """
    return max(date_list)

def inter_visits(date_list):
    """
    Calculates the number of intermediate visits based on a list of dates.
    """
    num_visits = len(date_list) - 2 # Subtract 2 for intermediate visits
    return max(num_visits, 0)

def calc_date_diff(date_list):
    """
    Calculates the difference in days between the first and last date in a list of dates.
    """
    first_date = min(date_list)
    last_date  = max(date_list)
    return (last_date - first_date).days

def divide_by_x(value, x):
    """
    Performs division of a value by x.
    """
    if x != 0:
        return value / x
    else:
        return None

def divide_by_y(value, y):
    """
    Performs division of a value by y.
    """
    if y != 0:
        return value / y
    else:
        return None
    
def get_pattern(row):
    """
    Determines the pattern of customer behavior based on their monthly frequency and weekly frequency.
    """
    values            = row['Monthly Frequency']
    last_value        = values[-1]
    second_last_value = values[-2]

    if all(value == 0 for value in values[:-2]) and (last_value > 0 or second_last_value > 0):

        if last_value > 0 and second_last_value > 0:
            return 'Regular'
        
        if second_last_value > 1:
            moving_avg = sum(values[-3:]) / 3
            if moving_avg > 0.75:  
                return 'Regular'
            else:
                return 'Occasional'
        else:
            return 'New'
        
    elif (last_value == 0 and second_last_value == 0) :

        if (values[-3]==0):
            return 'Lost'
        else:
            moving_avg = sum(values[-3:]) / 3
            if moving_avg > 0.85:
                return 'Regular'
            else:
                return 'Occasional'

    elif any(values[i] == values[i+1] for i in range(len(values)-1)) and (1 in values and 0 in values):
        return 'Regular'
    
    elif any(values[i] == values[i+1] == 0 for i in range(len(values)-1)):
        return 'Occasional'
    
    else:
        # Perform additional analysis such as moving average calculation
        # For example, let's assume we calculate the 3-week moving average
        moving_avg = sum(values[-3:]) / 3

        if moving_avg > 0.65:  
            return 'Regular'
        else:
            return 'Occasional'
