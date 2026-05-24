from manim import *
from typing import List, Callable
from manim import *


class PlottingExample(Scene):
    def construct(self):
        # axes and plotting setup
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

        # tracker drives the visible plot extent
        upper_x_range_tracker: ValueTracker = ValueTracker(0.1)
        sin_plot = always_redraw(
            lambda: axes.plot(
                lambda x: np.sin(x),
                x_range=[0, upper_x_range_tracker.get_value(), 0.01],
                color=YELLOW,
            )
        )
        cos_plot = always_redraw(
            lambda: axes.plot(
                lambda x: np.cos(x),
                x_range=[0, upper_x_range_tracker.get_value(), 0.01],
                color=YELLOW,
            )
        )
        # shaded area between the two curves
        area_under_the_curve = always_redraw(
            lambda: axes.get_area(
                graph=sin_plot,
                bounded_graph=cos_plot,
                x_range=[0, upper_x_range_tracker.get_value() - 0.001],
                color=[BLUE, GREEN],
                opacity=0.7,
            )
        )
        self.add(axes, sin_plot, cos_plot, area_under_the_curve)
        self.play(upper_x_range_tracker.animate.set_value(TAU), run_time=3)
        self.wait()


class UpdaterExample(Scene):
    def construct(self):
        # demonstrate updater-driven rotation
        square: Square = Square()
        dot: Dot = Dot().next_to(square, RIGHT, buff=MED_LARGE_BUFF)
        # dot.add_updater(lambda mob: mob.next_to(square,RIGHT,buff=MED_LARGE_BUFF))

        # updater factory for rotations
        def dot_updater1(angle: float, omega: float):
            def updater(mob: Dot, dt: float) -> None:
                mob.rotate(dt * angle * omega)

            return updater

        # def dot_updater2(mob:Square,dt:float)->None:
        #     mob.next_to(square,RIGHT,MED_LARGE_BUFF)
        # grid of squares with different angular speeds
        square_group = (
            VGroup(
                Square().add_updater(dot_updater1(angle, speed))
                for angle in np.arange(0.0, PI / 4, PI / 16)
                for speed in np.arange(0.0, 1.0, 0.2)
            )
            .arrange_in_grid(8, 5, buff=LARGE_BUFF)
            .scale_to_fit_width(9)
        )
        self.add(square_group)
        self.wait(5)


class DiscontinuousExample(Scene):
    def construct(self):
        # compare naive vs discontinuity-aware plotting
        # ax1 = NumberPlane([-TAU, TAU, PI / 2],[-4, 4, 0.5])
        ax1 = NumberPlane((-3, 3, 0.5), (-1.5, 1.5, 0.5))

        ax2 = NumberPlane((-3, 3), (-4, 4))
        VGroup(ax1, ax2).arrange()
        discontinuous_function = lambda x: (x**2 - 2) / (x**2 - 4)
        incorrect = ax1.plot(
            lambda x: (x**2 - 2) / (x**2 - 4), x_range=[-3.01, 3, 0.1], color=RED
        )
        correct = ax2.plot(
            discontinuous_function,
            x_range=[-3.001, 3, 0.1],
            discontinuities=[-2, 2],  # discontinuous points
            dt=0.1,  # left and right tolerance of discontinuity
            color=GREEN,
        )
        self.add(ax1, ax2, incorrect, correct)
