from manim import *
from typing import List, Tuple, Callable, Any, Dict


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
            x_range=[0, TAU, 1],
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
            bounding_function = lambda x: 0.0

        # generate intervals
        x_min, x_max, dx = x_range
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
        # axes for the epicycle projection
        x_min = 0
        x_max = 4 * TAU
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

        # Fourier parameters: (omega, length, phase)
        fourier_params: List[Tuple[float, float, float]] = self.get_fourier_params(10)

        # chain of arrows (epicycles)
        arrows: VGroup = VGroup(
            *[
                Arrow(start=ORIGIN, end=[length, 0, 0], buff=0)
                for (omega, length, phase) in fourier_params
            ]
        ).shift(LEFT * 4)

        for arrow, (omega, length, phase) in zip(arrows, fourier_params):
            arrow.rotate(phase, about_point=arrow.get_start())

        for i in range(1, len(arrows)):
            shift_val = arrows[i - 1].get_end() - arrows[i].get_start()
            arrows[i].shift(shift_val)

        omega0, _, _ = fourier_params[0]
        arrows[0].add_updater(self.arrow_updater(omega0, None))

        for prev_arrow, current_arrow, (omega, length, phase) in zip(
            arrows[:-1], arrows[1:], fourier_params[1:]
        ):
            current_arrow.add_updater(self.arrow_updater(omega, prev_arrow))

        # trace the endpoint of the last arrow
        dot = Dot(radius=0.03, color=YELLOW).add_updater(
            lambda mob: mob.move_to(arrows[-1].get_end())
        )
        path = TracedPath(lambda: dot.get_center()).set_color(YELLOW)
        self.add(arrows, dot, path)

        # time tracker for plotting y(t)
        t_tracker = ValueTracker(0.0)
        run_time = 7.0
        t_scale = x_max / run_time

        def update_time(mob, dt):
            t_tracker.increment_value(dt * t_scale)

        time_dot = Dot(radius=0).set_opacity(0)
        time_dot.add_updater(update_time)
        self.add(time_dot)

        base_y = arrows[0].get_start()[1]

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

            trace = TracedPath(
                (lambda d=y_dot: d.get_center()),
                stroke_color=color,
                stroke_width=2,
                stroke_opacity=0.3,
            )
            self.add(trace)

        self.wait(run_time)

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

        omega  – angular frequency of the arrow
        length – length (amplitude)
        phase  – initial phase (in radians)
        """
        params: List[Tuple[float, float, float]] = []

        # f(t) = 4/π * Σ_{k=0}^{∞} sin((2k+1)t)/(2k+1)
        for k in range(num_terms):
            n = 2 * k + 1
            omega = float(n)
            length = 4.0 / (np.pi * n)
            phase = 0.0

            params.append((omega, length, phase))

        return params


class Slider1(Group):
    def __init__(
        self,
        x_range: List,
        length: float,
        traker: ValueTracker,
        label: str,
        post_label: str,
        font_size: int = 25,
        decimal_places: int = 1,
        color: ManimColor = YELLOW,
        marker_scale: float = 0.1,
        marker_direction: np.ndarray = DOWN,
        numberline_kwargs: Dict[str, Any] = {},
        position_updater: Callable[[float], float] | None = None,
        position_kwargs: Dict[str, Any] | None = None,
        *args,
        **kwargs,
    ):
        self.tracker = traker
        self.dot_function_updator = position_updater
        self.position_kwargs = position_kwargs

        self.numberline = NumberLine(x_range, length, **numberline_kwargs)

        self.marker: VGroup = self._create_marker(
            self.numberline, self.tracker, color, marker_scale, marker_direction
        )
        self.label: Group = self._create_label(
            label,
            post_label,
            decimal_places,
            font_size,
            self.numberline,
            self.marker[0],
        )

        super().__init__(self.numberline, self.marker, self.label, *args, **kwargs)

    def _create_label(
        self,
        label: str,
        post_label: str,
        decimal_places: int,
        font_size: int,
        numberline: NumberLine,
        dot: Dot,
    ) -> Group:
        basic_label = MathTex(label, font_size=font_size)
        numeric_label = DecimalNumber(
            numberline.p2n(dot.get_center()),
            num_decimal_places=decimal_places,
            font_size=font_size,
        )
        post_label = MathTex(post_label, font_size=font_size)
        group: Group = Group(basic_label, numeric_label, post_label).arrange(
            RIGHT, SMALL_BUFF
        )
        group.add_updater(lambda mob: mob.next_to(dot, DOWN, SMALL_BUFF * 3))
        return group

    def _create_marker(
        self,
        numberline: NumberLine,
        traker: ValueTracker,
        color: ManimColor,
        marker_scale: float,
        marker_direction: np.ndarray,
        **kwargs,
    ) -> VGroup:
        dot = Dot().set_color(color)

        dot.move_to(numberline @ (traker.get_value()))

        dot.add_updater(
            self.dot_updater(
                self.numberline,
                self.tracker,
                self.dot_function_updator,
                self.position_kwargs,
            )
        )
        marker = (
            Triangle()
            .scale(marker_scale)
            .set_color(color)
            .set_fill(color, 1)
            .next_to(dot, marker_direction, SMALL_BUFF)
        )
        marker.add_updater(lambda mob, dt: mob.next_to(dot, DOWN, SMALL_BUFF))
        return VGroup(dot, marker)

    def dot_updater(
        self,
        numberline: NumberLine,
        traker: ValueTracker,
        position_function: Callable[[float], float] | None = None,
        updater_kwargs: Dict[str, Any] | None = None,
    ) -> Callable[[Dot, float], None]:
        def updater(mob: Dot, dt: float) -> None:
            x = traker.get_value()

            if position_function is not None:
                kwargs = updater_kwargs or {}
                x = position_function(x, **kwargs)

            mob.move_to(numberline @ x)

        return updater


class Slider1Scene(Scene):
    def construct(self):
        traker: ValueTracker = ValueTracker(1)
        nl_kw: Dict[str, Any] = {
            "include_numbers": True,
            "font_size": 45,
            "label_direction": LEFT,
            "rotation": PI / 2,
        }

        def foo(value: float, **kwargs) -> float:
            return np.sin(value) * kwargs["ampl"] + kwargs["shift"]

        slider = Slider1(
            x_range=[-5, 5, 1],
            length=10,
            traker=traker,
            label=r"\vec{r}",
            post_label="cm",
            numberline_kwargs=nl_kw,
            position_updater=foo,
            position_kwargs={"ampl": 2, "shift": 1},
        )
        self.add(slider)

        self.play(traker.animate.set_value(TAU), run_time=TAU, rate_func=linear)
        self.wait()
