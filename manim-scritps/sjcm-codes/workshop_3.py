from manim import *
from typing import List

"""
*) choose x range and step
*) in a loop
    *) create a MathTex object <- mathematical text with LaTeX support
    *) move the previously created object to a position on the axis
    *) shift the object in a chosen direction
"""


class RelativePositions(Scene):
    def create_tick_labels(
        self, x_range: List[float], axes: Axes, buff: float
    ) -> VGroup:
        # build custom tick labels for multiples of pi/2
        start, stop, step = x_range[0], x_range[1], x_range[2]
        number_of_steps = int((stop - start) / step)
        labels: VGroup = VGroup()
        font_size: int = 30
        string_label: str = ""
        color = YELLOW
        for i in range(1, number_of_steps + 1):
            if i == 1:
                string_label = r"\frac{\pi}{2}"
            elif i % 2 == 0:
                string_label = rf"{round(i/2)}\pi"
                if round(i / 2) == 1:
                    string_label = rf"\pi"
            else:
                string_label = rf"\frac{{{i}\pi}}{2}"

            label = MathTex(string_label, font_size=font_size, color=color)
            label.move_to(axes @ (start + i * step, 0)).shift(DOWN * buff)
            labels.add(label)
        return labels

    def construct(self):
        # axes with custom x labels
        x_range: List[float] = [0, TAU, PI / 2]
        y_range: List[float] = [-1.5, 1.5, 0.5]
        axes: Axes = Axes(
            x_range=x_range,
            y_range=y_range,
            x_length=10,
            y_length=5,
            tips=False,
            # x_axis_config={"decimal_number_config": {"num_decimal_places": 2}},
        )  # .add_coordinates()

        # compare absolute vs axis-based positions
        dot1: Dot = Dot(color=YELLOW)
        dot2: Dot = Dot(color=RED)

        dot1.move_to(np.array([2, 1, 0]))
        dot2.move_to(axes.c2p(2, 1))

        x_axis_labels: VGroup = self.create_tick_labels(x_range, axes, LARGE_BUFF)
        self.add(axes, x_axis_labels)


class Homework1(Scene):
    def construct(self):
        # plot sin and cos using different techniques
        amplitude: float = 1.0
        x_range: List[float] = [0, TAU, PI / 2]
        y_range: List[float] = [-(amplitude + 0.5), (amplitude + 0.5), 0.5]
        axes: Axes = Axes(
            x_range=x_range,
            y_range=y_range,
            x_length=10,
            y_length=5,
            tips=False,
            x_axis_config={"decimal_number_config": {"num_decimal_places": 2}},
        ).add_coordinates()

        # scatter plot for sin and smooth curve for cos
        plot1 = VGroup(
            Dot(radius=0.03).move_to(axes @ (x, np.sin(x)))
            for x in np.arange(0, TAU, 0.01)
        )
        plot2 = (
            VMobject()
            .set_points_smoothly(
                np.array([axes @ (x, np.cos(x)) for x in np.arange(0, TAU, 0.01)])
            )
            .set_color(YELLOW)
        )
        self.add(axes, plot1, plot2)
