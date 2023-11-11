import pandas as pd
import numpy as np

def euclidean_distance(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def analyze_gaze_data(file_path, output_path):
    # Load the gaze data
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

    # Save the updated data
    gaze_data.to_csv(output_path, index=False)
    print(f"Updated gaze data saved to {output_path}")


# Replace with the path to your input and output CSV files
input_file_path = 'gaze_data.csv'
output_file_path = 'gaze_data_with_fixations.csv'

analyze_gaze_data(input_file_path, output_file_path)
