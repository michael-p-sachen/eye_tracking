import pandas as pd
import numpy as np


def euclidean_distance(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def find_fixations(file_path):
    gaze_data = pd.read_csv(file_path)

    # Define threshold and minimum duration for fixations
    distance_threshold = 0.01  # 1% of the screen
    min_fixation_samples = 10  # Assuming 100ms per sample

    # Calculate the mean gaze position
    gaze_data['Mean_X'] = gaze_data[['Right_X', 'Left_X']].mean(axis=1)
    gaze_data['Mean_Y'] = gaze_data[['Right_Y', 'Left_Y']].mean(axis=1)

    # Initialize columns for fixation starts and ends
    gaze_data['Fixation_Start'] = False
    gaze_data['Fixation_End'] = False

    # Analyze fixations
    fixation_start_index = None
    for i in range(1, len(gaze_data)):
        distance = euclidean_distance(
            gaze_data.at[i, 'Mean_X'], gaze_data.at[i, 'Mean_Y'],
            gaze_data.at[i - 1, 'Mean_X'], gaze_data.at[i - 1, 'Mean_Y']
        )

        if distance < distance_threshold and fixation_start_index is None:
            fixation_start_index = i
        elif distance >= distance_threshold and fixation_start_index is not None:
            if i - fixation_start_index >= min_fixation_samples:
                gaze_data.at[fixation_start_index, 'Fixation_Start'] = True
                gaze_data.at[i - 1, 'Fixation_End'] = True
            fixation_start_index = None

    if fixation_start_index is not None and len(gaze_data) - fixation_start_index >= min_fixation_samples:
        gaze_data.at[fixation_start_index, 'Fixation_Start'] = True
        gaze_data.at[len(gaze_data) - 1, 'Fixation_End'] = True

    # Remove calculation columns
    gaze_data.drop(['Mean_X', 'Mean_Y'], axis=1, inplace=True)

    return gaze_data


def fixation_analysis(df):
    # number of fixations, mean fixation time, SD fixation time

    fixations = []
    starts = df[df['Fixation_Start'] == True]
    ends = df[df['Fixation_End'] == True]
    for start, end in zip(starts.itertuples(), ends.itertuples()):
        period = df.iloc[end.Index - 1].Timestamp - start.Timestamp
        fixations.append(period)

    mean = np.mean(fixations)
    sd = np.std(fixations)

    return {
        'number_of_fixations': len(fixations),
        'mean_fixation_time': mean,
        'sd_fixation_time': sd
    }


def do_analysis(file_path):
    df = find_fixations(file_path)
    fixation_data = fixation_analysis(df)
    return fixation_data


