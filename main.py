import os

from art import concentric_circles

output_folder = 'Images'
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

concentric_circles.default_run(output_folder, num_to_generate=1)
