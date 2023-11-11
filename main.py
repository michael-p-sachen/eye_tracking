import tobii_research as tr
import time
import pygame
import numpy as np
import csv
from fixation_analysis import do_analysis

# Initialize Pygame
pygame.init()

# Constants for the display
# write these out as metadata in the csv file
WIDTH, HEIGHT = 1440, 900

WHITE = (255, 255, 255)

# Initialize Pygame window
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Eye Gaze Plot")

# Lists to store gaze data
right_gaze_data_with_time = []
left_gaze_data_with_time = []

def gaze_data_callback(gaze_data):
    right_x, right_y = gaze_data['right_gaze_point_on_display_area']
    left_x, left_y = gaze_data['left_gaze_point_on_display_area']

    # Handle NaN cases
    if not (np.isnan(right_x) or np.isnan(right_y)):
        timestamp = time.time()  # Get the current time
        right_gaze_data_with_time.append((timestamp, right_x, right_y))

    if not (np.isnan(left_x) or np.isnan(left_y)):
        timestamp = time.time()  # Get the current time
        left_gaze_data_with_time.append((timestamp, left_x, left_y))

def save_gaze_data_to_csv(filename, right_gaze_data, left_gaze_data):
    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Timestamp', 'Right_X', 'Right_Y', 'Left_X', 'Left_Y'])  # Write header
        for right_timestamp, right_x, right_y in right_gaze_data:
            left_x, left_y = None, None
            for left_timestamp, x, y in left_gaze_data:
                if abs(left_timestamp - right_timestamp) < 0.02:  # Adjust the time threshold as needed
                    left_x, left_y = x, y
                    break
            csv_writer.writerow([right_timestamp, right_x, right_y, left_x, left_y])



def main():
    found_eyetrackers = tr.find_all_eyetrackers()
    my_eyetracker = found_eyetrackers[0]
    print("Address: " + my_eyetracker.address)
    print("Model: " + my_eyetracker.model)
    print("Name (It's OK if this is empty): " + my_eyetracker.device_name)
    print("Serial number: " + my_eyetracker.serial_number)

    my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                running = False

        # Update the display
        screen.fill(WHITE)

        # Draw gaze points
        for (_, rx, ry), (_, lx, ly) in zip(right_gaze_data_with_time, left_gaze_data_with_time):
            if not np.isnan(rx) and not np.isnan(ry) and not np.isnan(lx) and not np.isnan(ly):
                x = (rx + lx) / 2
                y = (ry + ly) / 2
                pygame.draw.circle(screen, (0, 0, 0), (int(x * WIDTH), int(y * HEIGHT)), 2)
        # for _, x, y in left_gaze_data_with_time:
        #     if not np.isnan(x) and not np.isnan(y):
        #         pygame.draw.circle(screen, (0, 0, 255), (int(x * WIDTH), int(y * HEIGHT)), 2)

        pygame.display.flip()
        # time.sleep(0.01)  # Limit the frame rate

    my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

    save_gaze_data_to_csv('gaze_data.csv', right_gaze_data_with_time, left_gaze_data_with_time)
    fixation_data = do_analysis('gaze_data.csv')

    # Prepare to display the statistics on the screen
    font = pygame.font.Font(None, 36)  # Use a default font and size 36

    # Render the statistics to display
    fixation_text = [
        f'Number of fixations: {fixation_data["number_of_fixations"]}',
        f'Mean fixation time: {fixation_data["mean_fixation_time"]}',
        f'SD fixation time: {fixation_data["sd_fixation_time"]}'
    ]

    # Clear the screen and display the fixation data
    screen.fill(WHITE)
    for i, text in enumerate(fixation_text):
        rendered_text = font.render(text, True, (0, 0, 0))
        screen.blit(rendered_text, (50, 50 + i * 40))  # Adjust position as needed

    pygame.display.flip()

    # Wait for the user to press the spacebar again to quit
    waiting_for_quit = True
    while waiting_for_quit:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting_for_quit = False

    pygame.image.save(screen, 'screenshot.png')
    pygame.quit()

if __name__ == "__main__":
    main()
