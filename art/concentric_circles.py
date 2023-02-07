import colorsys
import os
import random
from typing import Optional

import numpy as np
from PySide6.QtCore import QRectF, Qt, QPointF, QRect
from PySide6.QtGui import QPainter, QPen, QColor, QRadialGradient, QBrush
from tqdm import tqdm

from qt5 import CreativePainter
from utils.num_utils import remap


def get_color(hue: float, sat: float, value: float) -> QColor:
    rgb_dec = colorsys.hsv_to_rgb(hue, sat, value)

    return QColor(int(rgb_dec[0] * 255), int(rgb_dec[1] * 255), int(rgb_dec[2] * 255), 255)


def draw_arc(cp: CreativePainter, thickness: int, left: float, right: float, start_angle: float, end_angle: float,
             hues: [], color_value: float, color_sat: float):
    # pick our color randomly
    color_index = np.random.randint(low=0, high=len(hues), size=1)[0]

    # Draw the border. We're adjusting the "value" in the HSV up a hair to make it brighter than the fill color.
    color = get_color(hues[color_index], color_sat, min(color_value + .1, 1))
    pen = QPen(color, thickness)
    pen.setCapStyle(Qt.PenCapStyle.FlatCap)
    cp.painter.setPen(pen)
    rect = QRectF(left, left, right - left, right - left)
    # actually draw the border now that the pen is configured.
    cp.painter.drawArc(rect, start_angle, end_angle)

    # set-up for the fill color by just re-using the pen
    color = get_color(hues[color_index], color_sat, color_value)
    pen.setColor(color)
    pen.setWidth(thickness - 4)
    # since we adjusted the pen, you'll need to re-attach it to the painter object
    cp.painter.setPen(pen)
    # draw the fill
    cp.painter.drawArc(rect, start_angle, end_angle)


def run(cp: CreativePainter, hues: [],
        min_thickness: Optional[int] = None, max_thickness: Optional[int] = None,
        min_padding: Optional[float] = None, max_padding: Optional[float] = None,
        seed: Optional[int] = None, arc_probability: Optional[float] = 10000):
    if seed is None:
        seed = random.randint(0, 100000000)

    total_degrees = 360 * 16  # QT goes by 16th degrees.
    np.random.seed(seed)
    long_edge_size = max(cp.width, cp.height)

    if min_thickness is None:
        min_thickness = long_edge_size * 0.01

    if max_thickness is None:
        max_thickness = long_edge_size * 0.08

    if min_padding is None:
        min_padding = long_edge_size * 0.03

    if max_padding is None:
        max_padding = long_edge_size * 0.08

    min_value = .07
    max_value = .95
    min_sat = .25
    max_sat = .75

    with cp:
        cp.painter.setRenderHint(QPainter.Antialiasing)

        min_offset = int(-long_edge_size / 2)
        cur_offset = min_offset
        max_offset = int(long_edge_size / 2)
        iteration = 0
        min_angle_size = 5 * 16  # 5 degree

        while cur_offset < max_offset:
            cur_thickness = remap(cur_offset, min_offset, max_offset, max_thickness, min_thickness)
            cur_value = remap(cur_offset, min_offset, max_offset, max_value, min_value)
            cur_sat = remap(cur_offset, min_offset, max_offset, max_sat, min_sat)
            cur_padding = remap(cur_offset, min_offset, max_offset, max_padding, min_padding)

            left = cur_offset + cur_thickness / 2

            right = cp.width - left

            cur_angle = 0
            max_angle = total_degrees

            # decides where we start drawing. Need to randomize as this starting point will always create an unnatural
            # seam if not handled.
            seam_angle = 0 # np.random.uniform(low=0, high=total_degrees, size=1)[0]

            while cur_angle < max_angle:
                start_angle = seam_angle + cur_angle + cur_padding
                span_angle = np.random.uniform(low=min_angle_size, high=max_angle, size=1)[0]
                should_draw = np.random.randint(0, 10000, 1)[0]
                cur_angle = start_angle + span_angle + (cur_padding * 32)

                if should_draw > arc_probability:
                    continue

                draw_arc(cp, cur_thickness, left, right, start_angle, span_angle, hues, cur_value, cur_sat)

            cur_offset += cur_thickness + cur_padding
            iteration += 1


def default_run(output_folder: str, num_to_generate: int = 25):
    for i in tqdm(range(0, num_to_generate)):
        base_seed = random.randint(0, 100000000)
        np.random.seed(base_seed)
        p = CreativePainter(2000, 2000, QColor(11, 9, 9, 255))

        # Draw a gradient background
        with p:
            gradient = QRadialGradient(QPointF(p.width / 2, p.height / 2), max(p.width, p.height))
            gradient.setColorAt(0, QColor(11, 9, 9, 255))
            gradient.setColorAt(1, QColor(25, 23, 23, 255))
            brush = QBrush(gradient)
            p.painter.fillRect(QRect(0, 0, p.width, p.height), brush)

        min_thickness = np.random.randint(10, 20)
        max_thickness = np.random.randint(50, 200)
        min_padding = np.random.randint(5, 25)
        max_padding = np.random.randint(75, 150)
        available_hues = [
            0.58611,
            0.98611,
            0.25
        ]

        run(
            p,
            available_hues,
            min_thickness=min_thickness,
            max_thickness=max_thickness,
            min_padding=min_padding,
            max_padding=max_padding,
            arc_probability=9000,
            seed=base_seed
        )

        did_save = p.save_image(os.path.join(output_folder, f'concentric_circles_{base_seed}.png'))

        if not did_save:
            print('ERROR: Failed to save image.')
