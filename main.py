import tobii_research as tr
import tkinter as tk
from tkinter import filedialog
import time
import pygame
import numpy as np
import csv

pygame.init()

WIDTH, HEIGHT = 1440, 900
WHITE = (255, 255, 255)

# Initialize Pygame window
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Eye Gaze Plot")

# Lists to store gaze data
right_gaze_data_with_time = []
left_gaze_data_with_time = []


def load_and_scale_background(filename, max_width, max_height):
    image = pygame.image.load(filename)
    image_width, image_height = image.get_size()

    # Calculate the scaled dimensions while maintaining aspect ratio
    if image_width > max_width or image_height > max_height:
        aspect_ratio = image_width / image_height
        if image_width > image_height:
            new_width = max_width
            new_height = int(max_width / aspect_ratio)
        else:
            new_height = max_height
            new_width = int(max_height * aspect_ratio)
        image = pygame.transform.scale(image, (new_width, new_height))

    return image


def choose_background_image():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename(
        title="Choose a background image",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tif *.tiff")]
    )

    return file_path


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
    file_name = choose_background_image()

    # file_name = "./sample.png"
    background_image = load_and_scale_background(file_name, WIDTH, HEIGHT)
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
                pygame.image.save(screen, 'screenshot_1.png')
                pygame.display.flip()
                screen.fill(WHITE)

                for (_, rx, ry), (_, lx, ly) in zip(right_gaze_data_with_time, left_gaze_data_with_time):
                    if not np.isnan(rx) and not np.isnan(ry) and not np.isnan(lx) and not np.isnan(ly):
                        x = (rx + lx) / 2
                        y = (ry + ly) / 2
                        pygame.draw.circle(screen, (0, 0, 0), (int(x * WIDTH), int(y * HEIGHT)), 2)

                pygame.image.save(screen, 'screenshot_2.png')
                running = False
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pygame.image.save(screen, 'screenshot_1.png')
                pygame.display.flip()
                screen.fill(WHITE)

                for (_, rx, ry), (_, lx, ly) in zip(right_gaze_data_with_time, left_gaze_data_with_time):
                    if not np.isnan(rx) and not np.isnan(ry) and not np.isnan(lx) and not np.isnan(ly):
                        x = (rx + lx) / 2
                        y = (ry + ly) / 2
                        pygame.draw.circle(screen, (0, 0, 0), (int(x * WIDTH), int(y * HEIGHT)), 2)

                pygame.image.save(screen, 'screenshot_2.png')
                running = False
                break

        # Clear the screen with white
        screen.fill(WHITE)

        # Calculate the position to center the background image
        bg_x = (WIDTH - background_image.get_width()) // 2
        bg_y = (HEIGHT - background_image.get_height()) // 2

        # Draw the centered background image
        screen.blit(background_image, (bg_x, bg_y))

        # Draw gaze points
        for (_, rx, ry), (_, lx, ly) in zip(right_gaze_data_with_time, left_gaze_data_with_time):
            if not np.isnan(rx) and not np.isnan(ry) and not np.isnan(lx) and not np.isnan(ly):
                x = (rx + lx) / 2
                y = (ry + ly) / 2
                pygame.draw.circle(screen, (0, 0, 0), (int(x * WIDTH), int(y * HEIGHT)), 2)
        pygame.display.flip()

    my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
    save_gaze_data_to_csv('gaze_data.csv', right_gaze_data_with_time, left_gaze_data_with_time)
    pygame.quit()


if __name__ == "__main__":
    main()
