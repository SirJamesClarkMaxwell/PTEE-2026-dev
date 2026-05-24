from manim import *
from scipy.integrate import quad


class FourierTransform(Scene):
    def construct(self):
        # base axes for time-domain plots
        x_range = [-3 * PI, 3 * PI, PI / 2]
        main_axes = (
            Axes(
                x_range=x_range,
                y_range=[-1.5, 1.5, 0.5],
                x_length=6,
                y_length=3,
                tips=False,
            )
            .to_edge(LEFT, buff=LARGE_BUFF)
            .to_edge(UP, buff=LARGE_BUFF * 0.5)
        )
        axes_multiplied = main_axes.copy().next_to(
            main_axes, DOWN, buff=LARGE_BUFF * 1.25
        )
        main_axes_label = main_axes.get_axis_labels(x_label="t", y_label="f(t), g(t)")
        axes_multiplied_label = axes_multiplied.get_axis_labels(
            x_label="t", y_label="f * g"
        )

        # axes for the frequency-domain plot
        axes_fft = (
            Axes(
                x_range=[-6, 6, 2],
                y_range=[0, 12, 5],
                x_length=6,
                y_length=3,
                tips=False,
            )
            .add_coordinates()
            .next_to(main_axes, RIGHT, buff=SMALL_BUFF)
        )
        axes_fft_labels = axes_fft.get_axis_labels(
            x_label=MathTex(r"\omega"), y_label=MathTex(r"f\cdot g")
        )

        # parameters for the sliding window
        center = ValueTracker(0)
        width = ValueTracker(1.1)
        omega = ValueTracker(-5)

        def square_function(x: float) -> float:
            if (
                x > center.get_value() - width.get_value() / 2
                and x < center.get_value() + width.get_value() / 2
            ):
                return 1
            return 0

        # input and probe functions
        square_function_plot = always_redraw(
            lambda: main_axes.plot(
                lambda x: square_function(x), x_range=[-3 * PI, 3 * PI, 0.01], color=RED
            )
        )
        cos_func_plot = always_redraw(
            lambda: main_axes.plot(
                lambda x: np.cos(x * omega.get_value()),
                x_range=[-3 * PI, 3 * PI, 0.01],
                color=BLUE,
            )
        )

        # product of the two functions
        def multiplied_function(x: float, omega: ValueTracker) -> float:
            return square_function(x) * np.cos(x * omega.get_value())

        # Fourier coefficient magnitude (energy)
        def dot_product(omega):
            func = lambda x: square_function(x) * np.exp(-1j * omega * x)
            real_part, _ = quad(lambda x: np.real(func(x)), -3 * PI, 3 * PI)
            imaginary_part, _ = quad(lambda x: np.imag(func(x)), -3 * PI, 3 * PI)
            return real_part**2 + imaginary_part**2

        # plot product and area under the curve
        multiplied_function_plot = always_redraw(
            lambda: axes_multiplied.plot(
                lambda x: multiplied_function(x, omega),
                x_range=[-3 * PI, 3 * PI, 0.01],
                color=GREEN,
            )
        )
        multiplied_area = always_redraw(
            lambda: axes_multiplied.get_area(
                multiplied_function_plot,
                x_range=[-3 * PI, 3 * PI],
                color=GREEN,
                opacity=0.8,
            )
        )

        # FFT curve grows with omega sweep
        fft_plot = always_redraw(
            lambda: axes_fft.plot(
                lambda x: dot_product(x), x_range=[-5, omega.get_value()], color=GREEN
            )
        )

        # add all objects to the scene
        self.add(
            main_axes,
            axes_multiplied,
            main_axes_label,
            axes_multiplied_label,
            square_function_plot,
            cos_func_plot,
            multiplied_function_plot,
            multiplied_area,
            axes_fft,
            axes_fft_labels,
            fft_plot,
        )

        self.play(omega.animate.set_value(5), run_time=5)
        self.wait()
        self.play(center.animate.set_value(2 * PI), run_time=3)
        self.wait()
        self.play(width.animate.set_value(2 * PI), run_time=3)
        self.wait()
        self.play(center.animate.set_value(-2 * PI), run_time=6)
        self.wait()
