"""
Course: CSE 351
Assignment: 06
Author: Dylan

Instructions:

- see instructions in the assignment description in Canvas

"""

import multiprocessing as mp
import os
import cv2
import numpy as np

from cse351 import *

# Folders
BASE_DIR = os.path.dirname(__file__)
INPUT_FOLDER = os.path.join(BASE_DIR, "faces")
STEP1_OUTPUT_FOLDER = os.path.join(BASE_DIR, "step1_smoothed")
STEP2_OUTPUT_FOLDER = os.path.join(BASE_DIR, "step2_grayscale")
STEP3_OUTPUT_FOLDER = os.path.join(BASE_DIR, "step3_edges")

# Parameters for image processing
GAUSSIAN_BLUR_KERNEL_SIZE = (5, 5)
CANNY_THRESHOLD1 = 75
CANNY_THRESHOLD2 = 155

# Allowed image extensions
ALLOWED_EXTENSIONS = ['.jpg']

# ---------------------------------------------------------------------------
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

# ---------------------------------------------------------------------------
def task_convert_to_grayscale(image):
    if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
        return image  # Already grayscale
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# ---------------------------------------------------------------------------
def task_smooth_image(image, kernel_size):
    return cv2.GaussianBlur(image, kernel_size, 0)

# ---------------------------------------------------------------------------
def task_detect_edges(image, threshold1, threshold2):
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(image, threshold1, threshold2)

# ---------------------------------------------------------------------------
def worker_smooth(input_queue, output_queue):
    while True:
        filename = input_queue.get()
        if filename is None:
            output_queue.put(None)
            break

        input_path = os.path.join(INPUT_FOLDER, filename)
        output_path = os.path.join(STEP1_OUTPUT_FOLDER, filename)

        img = cv2.imread(input_path)
        if img is None:
            continue

        smoothed = task_smooth_image(img, GAUSSIAN_BLUR_KERNEL_SIZE)
        cv2.imwrite(output_path, smoothed)

        output_queue.put(filename)

# ---------------------------------------------------------------------------
def worker_grayscale(input_queue, output_queue):
    while True:
        filename = input_queue.get()
        if filename is None:
            output_queue.put(None)
            break

        input_path = os.path.join(STEP1_OUTPUT_FOLDER, filename)
        output_path = os.path.join(STEP2_OUTPUT_FOLDER, filename)

        img = cv2.imread(input_path)
        if img is None:
            continue

        gray = task_convert_to_grayscale(img)
        cv2.imwrite(output_path, gray)

        output_queue.put(filename)

# ---------------------------------------------------------------------------
def worker_edges(input_queue):
    while True:
        filename = input_queue.get()
        if filename is None:
            break

        input_path = os.path.join(STEP2_OUTPUT_FOLDER, filename)
        output_path = os.path.join(STEP3_OUTPUT_FOLDER, filename)

        img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue

        edges = task_detect_edges(img, CANNY_THRESHOLD1, CANNY_THRESHOLD2)
        cv2.imwrite(output_path, edges)

# ---------------------------------------------------------------------------
def run_image_processing_pipeline():
    print("Starting image processing pipeline...")

    # Create output folders
    create_folder_if_not_exists(STEP1_OUTPUT_FOLDER)
    create_folder_if_not_exists(STEP2_OUTPUT_FOLDER)
    create_folder_if_not_exists(STEP3_OUTPUT_FOLDER)

    # Create Queues
    queue1 = mp.Queue()
    queue2 = mp.Queue()
    queue3 = mp.Queue()

    # Create the three process groups
    process_smooth = mp.Process(target=worker_smooth, args=(queue1, queue2))
    process_gray = mp.Process(target=worker_grayscale, args=(queue2, queue3))
    process_edges = mp.Process(target=worker_edges, args=(queue3,))

    # Start processes
    process_smooth.start()
    process_gray.start()
    process_edges.start()

    # Feed filenames into first queue
    for filename in os.listdir(INPUT_FOLDER):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext in ALLOWED_EXTENSIONS:
            queue1.put(filename)

    # Send termination signal
    queue1.put(None)

    # Wait for processes to finish
    process_smooth.join()
    process_gray.join()
    process_edges.join()

    print("\nImage processing pipeline finished!")
    print(f"Original images are in: '{INPUT_FOLDER}'")
    print(f"Smoothed images are in: '{STEP1_OUTPUT_FOLDER}'")
    print(f"Grayscale images are in: '{STEP2_OUTPUT_FOLDER}'")
    print(f"Edge images are in: '{STEP3_OUTPUT_FOLDER}'")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    log = Log(show_terminal=True)
    log.start_timer('Processing Images')

    # check for input folder
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: The input folder '{INPUT_FOLDER}' was not found.")
        print(f"Create it and place your face images inside it.")
        print('Link to faces.zip:')
        print('   https://drive.google.com/file/d/1eebhLE51axpLZoU6s_Shtw1QNcXqtyHM/view?usp=sharing')
    else:
        run_image_processing_pipeline()

    log.write()
    log.stop_timer('Total Time To complete')
