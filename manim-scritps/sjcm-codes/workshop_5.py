from manim import *
from typing import List, Dict, Any, Callable


class Homework1(Scene):
    def construct(self):
        # epicycle-like chain of arrows
        arrow_length = 0.5

        # updater factory: rotate each arrow and keep it connected
        def arrow_updater(
            omega: float, previous_arrow: Arrow | None = None
        ) -> Callable[[Arrow, float], None]:
            def updater(mob: Arrow, dt: float) -> None:
                if previous_arrow is not None:
                    shift_value = previous_arrow.get_end() - mob.get_start()
                    mob.shift(shift_value)
                mob.rotate(omega * dt, about_point=mob.get_start())

            return updater

        # create a chain of arrows
        arrows: VGroup = VGroup(
            *[Arrow(start=ORIGIN, end=[arrow_length, 0, 0], buff=0) for _ in range(5)]
        )

        for i in range(1, len(arrows)):
            shift_val = arrows[i - 1].get_end() - arrows[i].get_start()
            arrows[i].shift(shift_val)

        omegas = list(range(1, len(arrows) + 1))
        arrows[0].add_updater(arrow_updater(float(omegas[0]), None))

        for i in range(1, len(arrows)):
            upd = arrow_updater(float(omegas[i]), arrows[i - 1])
            arrows[i].add_updater(upd)

        # trace the end of the chain
        dot = Dot(color=YELLOW).add_updater(
            lambda mob: mob.move_to(arrows[-1].get_end())
        )
        path = (
            TracedPath(lambda: dot.get_center()).set_color(YELLOW).set_stroke_width(2)
        )
        self.add(arrows, dot, path)

        self.wait(7)


class Homework2(Scene):
    def construct(self):
        # animated harmonic motion with live plot
        time_tracker = ValueTracker(0)
        numberplane = (
            NumberPlane(
                x_length=5,
                y_length=5,
                x_range=[0, 10.1, 2],
                y_range=[-6.01, 6.01, 2],
                y_axis_config={"label_direction": LEFT},
            )
            .add_coordinates()
            .to_edge(RIGHT, MED_SMALL_BUFF)
        )
        numberplane_lables = numberplane.get_axis_labels("t", "x(t)")
        numberline = NumberLine(
            x_range=[-6, 6, 2], length=6, include_numbers=True
        ).to_edge(LEFT, MED_SMALL_BUFF)
        dot = Dot()
        time_value = 0
        amplitude = ValueTracker(1)
        omega = ValueTracker(1)
        phase = ValueTracker(0)
        c = ValueTracker(0)

        # move the dot on the number line
        def dot_updater(numberline: NumberLine, *valuetrackers):
            def updater(mob: Dot, dt: float):
                nonlocal time_value
                time_value += dt
                A, w, phi, c = list(map(lambda it: it.get_value(), valuetrackers))
                dot_position = A * np.sin(w * time_value + phi) + c
                mob.move_to(numberline @ dot_position)

            return updater

        dot.add_updater(dot_updater(numberline, amplitude, omega, phase, c))

        # build a plot that grows with time
        def create_plot(nb: NumberPlane, *args):
            def create():
                A, w, phi, c, t = list(map(lambda it: it.get_value(), args))
                func = lambda loc_t: A * np.sin(w * loc_t + phi) + c
                return nb.plot(function=func, x_range=[0, t, 0.01], color=YELLOW)

            return create

        plot = always_redraw(
            create_plot(numberplane, amplitude, omega, phase, c, time_tracker)
        )
        self.add(numberplane, numberline, numberplane_lables, dot, plot)

        self.play(time_tracker.animate.set_value(10), rate_func=linear, run_time=10)
        self.wait(3)
        # self.play(omega.set_value(4))
        omega.set_value(4)
        self.wait(3)
        self.play(amplitude.animate.set_value(4))
        self.wait(3)
        self.play(phase.animate.set_value(TAU), run_time=5)
        self.wait(3)
        self.play(c.animate.set_value(2))
        self.wait(3)
        self.wait()


class PonitTransformations(Scene):
    def construct(self):
        # visualize point-by-point transformations
        tr = Triangle(color=YELLOW_A)
        tr_points = always_redraw(
            lambda: VGroup(Dot(color=YELLOW).move_to(p) for p in tr.get_all_points())
        )

        c = Circle(color=BLUE_A).shift(3 * RIGHT)
        c_points = always_redraw(
            lambda: VGroup(Dot(color=BLUE).move_to(p) for p in c.get_all_points())
        )

        self.add(tr, c, tr_points, c_points)
        self.play(
            ReplacementTransform(tr.copy(), c),
            ReplacementTransform(tr_points.copy(), c_points),
            run_time=10,
        )
        self.wait()


class AreaBetweenGraphsFixI(Scene):
    def construct(self):
        # area between two time-shifted curves
        axes = NumberPlane(
            axis_config={"include_ticks": False, "include_numbers": True}
        )
        val = ValueTracker(0)

        def sin(x):
            return np.sin(x + val.get_value())

        def cos(x):
            return np.cos(x - val.get_value())

        graph = always_redraw(lambda: axes.plot(sin, x_range=[0, 2 * PI, 0.01]))
        graph1 = always_redraw(lambda: axes.plot(cos, x_range=[0, 2 * PI, 0.01]))

        graph.set(color=BLUE)
        self.play(Create(axes))
        self.play(Create(VGroup(graph, graph1)))

        area = always_redraw(
            lambda: axes.get_area(
                graph=graph,
                bounded_graph=graph1,
                x_range=[0, val.get_value()],
                color=(RED, ORANGE, YELLOW, GREEN),
            )
        )

        self.play(Create(area))
        self.play(val.animate.set_value(2 * PI), run_time=5)
        self.wait()


class AreaBetweenCurvesFix2(Scene):
    def construct(self):
        # alternative area fill using updaters
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

        upper_x_range_tracker: ValueTracker = ValueTracker(0.01)

        # helper for building plots
        def generate_plot(func, **kwargs) -> ParametricFunction:
            return axes.plot(lambda x: func(x), **kwargs)

        # keep t_max in sync with a tracker
        def t_max_updater(value_t: ValueTracker):
            def updater(mob: ParametricFunction, dt):
                mob.t_max = value_t.get_value()

            return updater

        sin_plot = generate_plot(
            func=np.sin,
            x_range=[0, upper_x_range_tracker.get_value(), 0.01],
            color=YELLOW,
        )
        sin_plot.add_updater(
            lambda mob: mob.become(
                generate_plot(
                    func=np.sin,
                    x_range=[0, upper_x_range_tracker.get_value(), 0.01],
                    color=YELLOW,
                )
            )
        )
        sin_plot.add_updater(t_max_updater(upper_x_range_tracker))

        cos_plot = generate_plot(
            func=np.cos,
            x_range=[0, upper_x_range_tracker.get_value(), 0.01],
            color=YELLOW,
        )
        cos_plot.add_updater(t_max_updater(upper_x_range_tracker))
        cos_plot.add_updater(
            lambda mob: mob.become(
                generate_plot(
                    func=np.cos,
                    x_range=[0, upper_x_range_tracker.get_value(), 0.01],
                    color=YELLOW,
                )
            )
        )
        area_under_the_curve = always_redraw(
            lambda: axes.get_area(
                graph=sin_plot,
                bounded_graph=cos_plot,
                x_range=[0, upper_x_range_tracker.get_value()],
                color=[BLUE, GREEN],
                opacity=0.7,
            )
        )
        self.add(axes, sin_plot, cos_plot, area_under_the_curve)
        self.play(upper_x_range_tracker.animate.set_value(TAU), run_time=3)
        self.wait()


from workshop_preparation import Slider


class Slider1(Group):
    def __init__(
        self,
        x_range: List,
        length: float,
        traker: ValueTracker,
        color: ManimColor = YELLOW,
        numberline_kwargs: Dict[str, Any] = {},
        position_updater: Callable[Any, np.ndarray] = None,
        *args,
        **kwargs,
    ):
        self.tracker = traker
        self.numberline = NumberLine(x_range, length, **numberline_kwargs)

        self.dot = Dot().set_color(color)
        self.dot.move_to(self.numberline @ (traker.get_value()))

        self.dot.add_updater(self.dot_updater(self.numberline, self.tracker))

        super().__init__(self.numberline, self.dot, *args, **kwargs)

    def dot_updater(
        self, numberline: NumberLine, traker: ValueTracker
    ) -> Callable[[Dot, float], None]:
        def updater(mob: Dot, dt: float) -> None:
            mob.move_to(numberline @ (traker.get_value()))

        return updater


class Slider1Scene(Scene):
    def construct(self):
        traker: ValueTracker = ValueTracker(1)
        nl_kw: Dict[str, Any] = {
            "include_numbers": True,
            "font_size": 45,
        }
        slider = Slider1(
            x_range=[-5, 5, 1],
            length=10,
            traker=traker,
            numberline_kwargs=nl_kw,
            position_updater=np.sin,
        )

        self.add(slider)
        self.play(traker.animate.set_value(3))
        self.wait()
        slider.dot.remove_updater(slider.dot.get_updaters()[0])
        slider.dot.add_updater(
            lambda mob: mob.move_to(slider.numberline @ (np.sin(traker.get_value())))
        )
        self.play(traker.animate.set_value(10), run_time=7, rate_func=linear)
        self.wait()


class SliderExample(Scene):
    def construct(self):
        tracker = ValueTracker(0)
        sliders_length = 6
        numberline_kwargs = {
            "rotation": PI / 2,
            "label_direction": LEFT,
            "include_numbers": True,
            "font_size": 30,
        }
        slider = Slider(
            x_range=[0, 2, 0.2],
            length=sliders_length,
            tracker=tracker,
            color=YELLOW,
            label=f"E_g = ",
            post_label=" [eV]",
            numberline_kwargs=numberline_kwargs,
        )
        self.add(slider)
        self.play(tracker.animate.set_value(2), run_time=2.5, rate_func=linear)
        self.wait()


class Exampl(Scene):

    def get_T_label(
        self, axes: Axes, traker: ValueTracker, function: Callable
    ) -> VGroup:
        value = traker.get_value()
        return VGroup(line, label)

    def construct(self):

        axes = Axes(x_range=[0, 4 * PI, 1], y_range=[-1, 1, 1], x_length=8, tips=True)
        foo = lambda x: np.sin(x)
        plot = axes.plot(lambda x: foo(x), color=BLUE)

        tracker = ValueTracker(0.01)
        value = tracker.get_value()

        line = Line(
            start=axes @ (value, 0, 0),
            end=axes @ (value, foo(value)),
            color=YELLOW,
        )
        line.add_updater(
            lambda mob: mob.put_start_and_end_on(
                start=axes @ (tracker.get_value(), 0, 0),
                end=axes @ (tracker.get_value(), foo(tracker.get_value())),
            )
        )
        label = VGroup(MathTex("x = "), DecimalNumber(value))
        label.add_updater(
            lambda mob: mob.arrange(RIGHT, SMALL_BUFF).next_to(
                line.get_start(), DOWN, SMALL_BUFF
            )
        )
        label[1].add_updater(lambda mob: mob.set_value(round(tracker.get_value(), 2)))

        # t_label = always_redraw(lambda: self.get_T_label(axes,tracker,foo))
        self.add(axes, plot, line, label)
        self.play(tracker.animate.set_value(2 * TAU), run_time=2 * TAU)
        self.wait()


class Ex2(Scene):
    def construct(self):
        l = Line()
        self.add(l)
        self.play(l.animate.put_start_and_end_on(start=[-1, 0, 0], end=[2, 2, 0]))
        self.wait()
