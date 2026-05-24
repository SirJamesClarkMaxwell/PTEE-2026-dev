from manim import *
from typing import List, Callable, Tuple


class PlottingExample(Scene):
    def construct(self):
        # axes and ranges for plotting
        x_range: List[float] = [0, TAU, PI / 2]
        y_range: List[float] = [-1.5, 1.5, 0.5]
        axes: Axes = Axes(
            x_range=x_range,
            y_range=y_range,
            x_length=10,
            y_length=5,
            tips=False,
            x_axis_config={"decimal_number_config": {"num_decimal_places": 2}},
        ).add_coordinates()

        # helper function
        def sin(x: float) -> float:
            return np.sin(x)

        # sin_graph = axes.plot(sin,x_range=[0,TAU,0.01], color=YELLOW)
        # cos_graph = axes.plot(lambda x: np.cos(x),x_range=[0,TAU,0.01], color=BLUE)
        # plot a discontinuous curve
        hyperbolic_plot = axes.plot(lambda x: (x**2 - 2) / (x**2 - 4), color=RED)

        # self.add(axes, sin_graph, cos_graph)
        self.add(axes, hyperbolic_plot)


class RiemmanReactangles(Scene):
    def construct(self):
        # axes and base plots
        x_range: List[float] = [0, TAU, PI / 2]
        y_range: List[float] = [-1.5, 1.5, 0.5]
        axes: Axes = Axes(
            x_range=x_range,
            y_range=y_range,
            x_length=10,
            y_length=5,
            tips=False,
            x_axis_config={"decimal_number_config": {"num_decimal_places": 2}},
        ).add_coordinates()

        sin_graph = axes.plot(lambda x: np.sin(x), color=GREEN)
        cos_graph = axes.plot(lambda x: np.cos(x), color=RED)
        # compute rectangles between sin and cos
        riemman_reactangles = self.get_riemann_rectangles(
            axes,
            lambda x: np.sin(x),
            x_range=[0, TAU, 0.1],
            bounding_function=lambda x: np.cos(x),
        )

        self.add(axes, sin_graph, riemman_reactangles, cos_graph)

    def get_riemann_rectangles(
        self,
        axes: Axes,
        function: Callable[[float], float],
        x_range: List[float],
        value_point: str = "center",  # "left", "right", "center"
        colors: List[ManimColor] | None = None,
        opacity: float = 0.5,
        direction: np.ndarray = UP,
        bounding_function: Callable[[float], float] | None = None,
    ) -> VGroup:

        # default colors and bounds
        if colors is None:
            colors = [BLUE, GREEN]

        if bounding_function is None:
            # e.g. x axis
            bounding_function = lambda x: 0.0

        # generate intervals
        x_min, x_max, dx = x_range
        # No +dx, otherwise it may go out of range
        x_intervals = [(x, x + dx) for x in np.arange(x_min, x_max, dx)]

        vp = value_point.lower()
        if vp == "left":
            sample_x = [x1 for (x1, x2) in x_intervals]
        elif vp == "right":
            sample_x = [x2 for (x1, x2) in x_intervals]
        else:  # "center"
            sample_x = [(x1 + x2) * 0.5 for (x1, x2) in x_intervals]

        f_values = [function(x) for x in sample_x]
        g_values = [bounding_function(x) for x in sample_x]

        rectangles = VGroup()
        for (x1, x2), y1, y2 in zip(x_intervals, f_values, g_values):
            # for safety, ensure top/bottom ordering
            top = max(y1, y2)
            bottom = min(y1, y2)

            rect = Polygon(
                axes.c2p(x1, bottom),  # bottom left
                axes.c2p(x1, top),  # top left
                axes.c2p(x2, top),  # top right
                axes.c2p(x2, bottom),  # bottom right
            )
            rectangles.add(rect)

        rectangles.set_color(color=colors)
        rectangles.set_fill(opacity=opacity)
        rectangles.set_sheen_direction(direction)

        return rectangles


class FourierSeries(Scene):
    def construct(self):
        # --- axis parameters ---
        x_min = 0
        x_max = 4 * TAU  # we want to reach 4? on the x axis
        x_step = PI
        x_range: List[float] = [x_min, x_max, x_step]
        y_range: List[float] = [-1.5, 1.5, 0.5]

        axes: Axes = (
            Axes(
                x_range=x_range,
                y_range=y_range,
                x_length=7,
                y_length=5,
                tips=False,
                axis_config={"font_size": 25},
                x_axis_config={"decimal_number_config": {"num_decimal_places": 1}},
                y_axis_config={"label_direction": RIGHT},
            )
            .add_coordinates()
            .to_edge(RIGHT, SMALL_BUFF)
        )
        self.add(axes)

        # --- Fourier parameters: (omega, length, phase) ---
        fourier_params: List[Tuple[float, float, float]] = self.get_fourier_params(10)

        # --- epicycle arrows on the left ---
        arrows: VGroup = VGroup(
            *[
                Arrow(start=ORIGIN, end=[length, 0, 0], buff=0)
                for (omega, length, phase) in fourier_params
            ]
        ).shift(LEFT * 4)

        # initial phases (one-time setup)
        for arrow, (omega, length, phase) in zip(arrows, fourier_params):
            arrow.rotate(phase, about_point=arrow.get_start())

        # connect ends to starts
        for i in range(1, len(arrows)):
            shift_val = arrows[i - 1].get_end() - arrows[i].get_start()
            arrows[i].shift(shift_val)

        # --- arrow rotation updaters ---
        omega0, _, _ = fourier_params[0]
        arrows[0].add_updater(self.arrow_updater(omega0, None))

        for prev_arrow, current_arrow, (omega, length, phase) in zip(
            arrows[:-1], arrows[1:], fourier_params[1:]
        ):
            current_arrow.add_updater(self.arrow_updater(omega, prev_arrow))

        # point tracking the end of the last arrow (epicycles)
        dot = Dot(radius=0.03, color=YELLOW).add_updater(
            lambda mob: mob.move_to(arrows[-1].get_end())
        )
        path = TracedPath(lambda: dot.get_center()).set_color(YELLOW)
        self.add(arrows, dot, path)

        # --- time tracker t (for plots on axes) ---
        t_tracker = ValueTracker(0.0)
        run_time = 7.0
        t_scale = x_max / run_time  # w 7 s przechodzimy z 0 do 4Ï„

        def update_time(mob, dt):
            t_tracker.increment_value(dt * t_scale)

        time_dot = Dot(radius=0).set_opacity(0)
        time_dot.add_updater(update_time)
        self.add(time_dot)

        # reference y level = start of the first arrow
        base_y = arrows[0].get_start()[1]

        # --- y(t) plots for each arrow ---
        colors = color_gradient([BLUE, GREEN, RED, PURPLE], len(arrows))

        for arrow, color in zip(arrows, colors):
            y_dot = Dot(radius=0.02, color=color, stroke_width=0)

            def make_y_updater(arrow_ref):
                def _upd(mob):
                    t = t_tracker.get_value()
                    y = arrow_ref.get_end()[1] - base_y
                    mob.move_to(axes @ (t, y))

                return _upd

            y_dot.add_updater(make_y_updater(arrow))
            self.add(y_dot)

            # NOTE: we need to "freeze" the reference to a specific y_dot
            trace = TracedPath(
                (lambda d=y_dot: d.get_center()),
                stroke_color=color,
                stroke_width=2,
                stroke_opacity=0.3,  # lekko przezroczyste
            )
            self.add(trace)

        self.wait(run_time)

    # rotation only with omega frequency - phase was already applied at start
    def arrow_updater(
        self, omega: float, previous_arrow: Arrow | None = None
    ) -> Callable[[Arrow, float], None]:
        def updater(mob: Arrow, dt: float) -> None:
            if previous_arrow is not None:
                shift_value = previous_arrow.get_end() - mob.get_start()
                mob.shift(shift_value)
            mob.rotate(omega * dt, about_point=mob.get_start())

        return updater

    def get_fourier_params(self, num_terms: int) -> List[Tuple[float, float, float]]:
        """
        Returns a list (omega, length, phase) for subsequent arrows.

        omega  - angular frequency of the arrow
        length - length (amplitude)
        phase  - initial phase (in radians)
        """
        params: List[Tuple[float, float, float]] = []

        # EXAMPLE: square wave:
        # f(t) = 4/Ï€ * Î£_{k=0}^{âˆž} sin((2k+1)t)/(2k+1)
        for k in range(num_terms):
            n = 2 * k + 1  # odd harmonics only
            omega = float(n)  # angular frequency
            length = 4.0 / (np.pi * n)  # amplituda
            phase = 0.0  # sin => phase 0

            params.append((omega, length, phase))

        return params
