from re import L
from turtle import position
from typing import List, Callable, Dict
from manim import *


# from manim_slides import Slide
class Spring2D(VMobject):
    def __init__(
        self,
        XY_start=np.array([0, 0]),  # Start spring point
        XY_end=np.array([1, 0]),  # End spring point
        num_loops=2,  # number of loops of spring
        r=0.2,  # radius of spring loop
        *args,
        **kwargs,
    ):
        VMobject.__init__(self)
        L = np.sqrt(
            np.square(XY_end[0] - XY_start[0]) + np.square(XY_end[1] - XY_start[1])
        )  # Length of spring
        theta = np.arctan2(
            XY_end[1] - XY_start[1], XY_end[0] - XY_start[0]
        )  # Angle of spring from horizontal

        T = (
            L - 2 * r
        )  # Intermediate parameter end value: Length of spring minus start and end parts
        alpha = (
            np.pi * (2 * num_loops + 1) / (L - 2 * r)
        )  # Intermediate const: Rotation constant (determines how fast to do loops)

        num_pts = 1000
        t = np.linspace(0, T, num_pts)  # Intermediate parameter, t
        x = np.zeros(num_pts)  # preallocating space for x and y
        y = np.zeros(num_pts)

        x = t + r * np.cos(alpha * t - np.pi) + r
        y = r * np.sin(alpha * t - np.pi)
        z = (
            0 * t
        )  # need to times it by t so that it becomes an zero array of size num_pts

        # multiply by rotation matrix R(theta) and add offset
        x_rot = x * np.cos(theta) - y * np.sin(theta)
        y_rot = x * np.sin(theta) + y * np.cos(theta)

        x = x_rot + XY_start[0]
        y = y_rot + XY_start[1]

        ind_pts = np.array(
            [x, y, np.zeros(num_pts)]
        ).T  # need to transpose to get each point as a separate array
        self.set_points_as_corners(ind_pts)


class SpringDamper2D(VMobject):
    def __init__(
        self,
        XY_start=np.array([0, 0]),  # Start spring point
        XY_end=np.array([1, 0]),  # End spring point
        num_loops=2,  # number of loops of spring
        r=0.2,  # radius of spring loop
        *args,
        **kwargs,
    ):
        VMobject.__init__(self, **kwargs)

        L = np.sqrt(
            np.square(XY_end[0] - XY_start[0]) + np.square(XY_end[1] - XY_start[1])
        )  # Length of spring
        theta = np.arctan2(
            XY_end[1] - XY_start[1], XY_end[0] - XY_start[0]
        )  # Angle of spring from horizontal

        # slightly move spring up (to make room for damper)
        XY_start[0] = XY_start[0] - 1.2 * r * np.sin(theta)
        XY_start[1] = XY_start[1] + 1.2 * r * np.cos(theta)
        XY_end[0] = XY_end[0] - 1.2 * r * np.sin(theta)
        XY_end[1] = XY_end[1] + 1.2 * r * np.cos(theta)

        T = (
            L - 2 * r
        )  # Intermediate parameter end value: Length of spring minus start and end parts
        alpha = (
            np.pi * (2 * num_loops + 1) / (L - 2 * r)
        )  # Intermediate const: Rotation constant (determines how fast to do loops)

        num_pts = 1000
        t = np.linspace(0, T, num_pts)  # Intermediate parameter, t
        x = np.zeros(num_pts)  # preallocating space for x and y
        y = np.zeros(num_pts)

        x = t + r * np.cos(alpha * t - np.pi) + r
        y = r * np.sin(alpha * t - np.pi)
        z = (
            0 * t
        )  # need to times it by t so that it becomes an zero array of size num_pts

        # multiply by rotation matrix R(theta) and add offset
        x_rot = x * np.cos(theta) - y * np.sin(theta)
        y_rot = x * np.sin(theta) + y * np.cos(theta)

        x = x_rot + XY_start[0]
        y = y_rot + XY_start[1]

        ind_pts = np.array(
            [x, y, np.zeros(num_pts)]
        ).T  # need to transpose to get each point as a separate array
        self.set_points_as_corners(ind_pts)

        # damper
        # slightly move down damper
        XY_start[0] = XY_start[0] + 2 * 1.2 * r * np.sin(theta)
        XY_start[1] = XY_start[1] - 2 * 1.2 * r * np.cos(theta)
        XY_end[0] = XY_end[0] + 2 * 1.2 * r * np.sin(theta)
        XY_end[1] = XY_end[1] - 2 * 1.2 * r * np.cos(theta)

        gap = 0.15  # percentage (length of damper)
        piston = L * 0.5 * (1 - gap) + L * gap * np.exp(
            -L / 3
        )  # length of bit before piston casing + amount piston head goes into casing
        casing = L * 0.5 * (1 - gap)  # length of bit before casing
        h = 2 * r  # width of damper

        # casing
        damper_box = Rectangle(
            width=L * gap, height=h
        )  # the width is variable. Maybe I should make this an IF statement to make it more realistic
        # damper_box.set_stroke(width = 0)
        damper_box.set_fill(opacity=0.5, color="#25839D")
        damper_box.move_to(XY_start / 2 + XY_end / 2)
        damper_box.rotate(theta)
        self.add(damper_box)

        # piston rod
        piston_rod = Line(
            start=np.array([XY_start[0], XY_start[1], 0]),
            end=np.array(
                [
                    XY_start[0] + piston * np.cos(theta),
                    XY_start[1] + piston * np.sin(theta),
                    0,
                ]
            ),
        )
        # piston disk
        piston_disk = Line(
            start=np.array(
                [
                    XY_start[0] + piston * np.cos(theta) + 0.4 * h * np.sin(theta),
                    XY_start[1] + piston * np.sin(theta) - 0.4 * h * np.cos(theta),
                    0,
                ]
            ),
            end=np.array(
                [
                    XY_start[0] + piston * np.cos(theta) - 0.4 * h * np.sin(theta),
                    XY_start[1] + piston * np.sin(theta) + 0.4 * h * np.cos(theta),
                    0,
                ]
            ),
        )
        # casing rod
        casing_rod = Line(
            start=np.array(
                [
                    XY_end[0] - casing * np.cos(theta),
                    XY_end[1] - casing * np.sin(theta),
                    0,
                ]
            ),
            end=np.array([XY_end[0], XY_end[1], 0]),
        )

        self.add(piston_rod)
        self.add(piston_disk)
        self.add(casing_rod)

class HorizontalMassSpringSystem(VGroup):
    def __init__(
        self,
        x0: float,
        A: ValueTracker,
        k: ValueTracker,
        m: ValueTracker,
        time: ValueTracker,
        box_width: float = 1.5,
        box_height: float = 1,
        axes_x_length: float = 7,
        axes_y_length: float = 3,
        dumper: bool = False,
        loops_number: int = 4,
        vertical:bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.x0: float = x0
        self.A: ValueTracker = A
        self.k: ValueTracker = k
        self.m: ValueTracker = m
        self.time: ValueTracker = time
        x_min, x_max = 0, x0 + A.get_value() + 2
        step = round((x_max - x_min) / 10, 0)
        self.axes = Axes(
            x_range=[x_min, x_max, step],
            y_range=[0, 2, 2],
            x_length=axes_x_length,
            y_length=axes_y_length,
            # x_axis_config={"tip_shape": StealthTip},
            y_axis_config={"include_tip": False},
            x_axis_config={"include_tip": False, "tick_size": 0.05},
        )

        self.vertival:bool = vertical 
        self.box: Rectangle = Rectangle(
            height=box_height, width=box_width, stroke_width=0
        ).set_fill(BLUE, opacity=0.75)
        self.position_function = self.position
        self.position_function_kwargs = {}
        self.box.add_updater(self._box_updater())
        start: np.ndarray = (
            self.axes @ ([0, box_height / 2, 0])
            if not vertical
            else self.axes @ ([0, box_height / 2, 0])
        )
        end: np.ndarray = self.box.get_left()
        self.loops_number = loops_number
        self.spring_r = 0.15
        self.add_dummper = dumper
        font_size = 20
        x0_text = (
            MathTex(r"x_0", font_size=35)
            .move_to(self.axes @ (x0, 0))
            .shift(DOWN * MED_SMALL_BUFF)
        )
        x0_line = Line(
            start=self.axes.x_axis @ (x0),
            end=self.axes @ (x0, 1.5),
            color=YELLOW,
            stroke_width=1,
        )

        self.x0_marker: VGroup = VGroup(x0_text, x0_line)
        self.current_position_line = Line(color=YELLOW, stroke_width=1.1)
        self.current_position_line.add_updater(self._current_position_line_updater())

        self.delta_x_line = DashedVMobject(DoubleArrow(buff=0))
        self.delta_x_line.add_updater(self._delta_x_line_updater())
        self.delta_x_text = MathTex(r"\Delta x", font_size=font_size + 5)
        self.delta_x_text.add_updater(self._delta_x_text_updater())
        self.forces: Dict[str, Arrow] = {}
        self.add_force(self.force, RED, "F_T")
        # self.force_arrow = Arrow(color=RED, max_tip_length_to_length_ratio=0.15)
        # self.force_arrow.add_updater(self._force_arrow_updater(self.force))

        if dumper:
            self.spring = SpringDamper2D(
                XY_start=start, XY_end=end, num_loops=self.loops_number, r=self.spring_r
            )
        else:
            self.spring = Spring2D(
                XY_start=self.start,
                XY_end=self.end,
                num_loops=self.loops_number,
                r=self.spring_r,
            )

        self.dot = Dot(color=YELLOW, radius=0.05).add_updater(
            lambda mob: mob.move_to(self.box.get_center())
        )
        self.spring.add_updater(self._spring_updater())
        self.add(
            self.axes,
            self.box,
            self.spring,
            self.x0_marker,
            self.dot,
            self.current_position_line,
            self.delta_x_line,
            self.delta_x_text,
            *self.forces.values(),
        )

    def set_position_function(self, callback: Callable, **kwargs) -> None:
        self.position_function = callback
        self.position_function_kwargs = kwargs

    def _box_updater(self) -> Callable[[Mobject, float], None]:
        def updater(mob: Rectangle, dt: float) -> None:
            mob.move_to(
                self.axes
                @ ([self.position_function(**self.position_function_kwargs), 0])
            ).shift(UP * mob.get_height() / 2)

        return updater

    def _spring_updater(self) -> Callable[[Mobject, float], None]:
        def updater(mob: VMobject, dt: float) -> None:
            if self.add_dummper:
                spring = SpringDamper2D(
                    XY_start=self.start,
                    XY_end=self.end,
                    num_loops=self.loops_number,
                    r=self.spring_r,
                )
            else:
                spring = Spring2D(
                    XY_start=self.start,
                    XY_end=self.end,
                    num_loops=self.loops_number,
                    r=self.spring_r,
                )
            mob.become(spring)

        return updater

    def _current_position_line_updater(self) -> Callable[[Mobject, float], None]:
        def updater(mob: Line, dt: float) -> None:
            curr_pos_scene = self.dot.get_center()  # scene coords
            x_data = self.axes.p2c(curr_pos_scene)[0]  # scene -> data
            y_top_data = min(1.5, self.axes.y_range[1])  # keep inside axes
            end_scene = self.axes @ (x_data, y_top_data)  # data -> scene
            mob.put_start_and_end_on(curr_pos_scene, end_scene)

        return updater

    def _delta_x_line_updater(self) -> Callable[[Mobject, float], None]:
        def updater(mob: Mobject, dt: float) -> None:
            start = self.x0_marker[1].get_end()
            end = self.current_position_line.get_end()

            if np.linalg.norm(end - start) < 1e-6:
                end = start + np.array([1e-6, 0.0, 0.0])

            base = DoubleArrow(
                start=start, end=end, buff=0, max_tip_length_to_length_ratio=0.1
            ).match_style(mob)
            dashed = DashedVMobject(base, num_dashes=10, dashed_ratio=0.7).match_style(
                mob
            )
            mob.become(dashed)

        return updater

    def _delta_x_text_updater(self) -> Callable[[Mobject, float], None]:
        def updater(mob: MathTex, dt: float) -> None:
            x_pos = self.axes.p2c(self.delta_x_line.get_center())[0]
            mob.move_to(self.axes @ (x_pos, 1.7, 0))

        return updater

    def _force_arrow_updater(self, callback) -> Callable[[Mobject, float], None]:
        def updater(mob: Arrow, dt: float) -> None:
            start_scene = self.dot.get_center()
            x_data = self.axes.p2c(start_scene)[0]
            F = callback()

            end_scene = start_scene + np.array([F * 2, 0.0, 0.0])  # 3D

            if np.allclose(end_scene, start_scene):
                end_scene = start_scene + np.array([1e-6, 0.0, 0.0])

            mob.put_start_and_end_on(start_scene, end_scene)

        return updater

    @property
    def start(self):
        y_axis_units = self.axes.p2c(self.box.get_center())[1]  # scene -> data
        return self.axes.c2p(0, y_axis_units, 0)

    @property
    def end(self):
        return self.box.get_left()

    def position(self):
        A, k, m, t = self.A.get_value(), self.k.get_value(), self.m.get_value(), self.time.get_value()
        omega = np.sqrt(k / m)
        return self.x0 + A * np.cos(omega * t)

    def force(self):
        A, k, m, t = self.A.get_value(), self.k.get_value(), self.m.get_value(), self.time.get_value()
        omega = np.sqrt(k / m)
        # return -A * omega**2 * np.cos(omega * t) / m
        return -A * np.cos(omega * t) / m

    def add_force(self, callback: Callable, color: ManimColor, label: str):
        arrow = Arrow(color=color, buff=0, max_tip_length_to_length_ratio=0.1)
        arrow.add_updater(self._force_arrow_updater(callback))
        arrow_label = MathTex(rf"{label}", font_size=20).match_color(arrow)
        arrow_label.add_updater(lambda mob: mob.next_to(arrow, UP, SMALL_BUFF))
        self.forces[label] = VGroup(arrow, arrow_label)
        self.add(self.forces[label])
        return arrow, arrow_label


class VerticalMassSpringSystem(VGroup):
    """
    Vertical 1D mass–spring (optionally damper) attached to the ceiling.
    The spring connects from the ceiling (top support) straight down to the TOP of the box.
    Position y(t) is analytic: y = y0 + A cos(sqrt(k/m) t). Force = -k (y - y0).
    """

    def __init__(
        self,
        y0: float,  # equilibrium height (data y)
        A: ValueTracker,
        k: ValueTracker,
        m: ValueTracker,
        time: ValueTracker,
        box_width: float = 1.2,
        box_height: float = 0.9,
        axes_x_length: float = 3.0,
        axes_y_length: float = 5.0,
        dumper: bool = True,
        loops_number: int = 5,
        spring_r: float = 0.15,
    ) -> None:
        super().__init__()

        # ---- parameters / state ----
        self.y0 = float(y0)
        self.A, self.k, self.m, self.time = A, k, m, time
        self.loops_number = int(loops_number)
        self.spring_r = float(spring_r)
        self.add_damper = bool(dumper)

        # ---- axes (0 at floor, larger y upwards; ceiling at y_max) ----
        y_min, y_max = 0.0, self.y0 + min(-2.0, -A.get_value() - 2.0)
        step = min(0.5, round((y_max - y_min) / 10.0, 1))
        self.axes = Axes(
            x_range=[0, 2, 2],
            y_range=[y_max, y_min, step],
            x_length=axes_x_length,
            y_length=axes_y_length,
            x_axis_config={"include_tip": False},
            y_axis_config={"include_tip": False, "tick_size": 0.05},
        )

        # ---- mass (box) ----
        self.box = Rectangle(
            width=box_width, height=box_height, stroke_width=0
        ).set_fill(BLUE, opacity=0.75)
        self.position_function = self.position
        self.position_function_kwargs = {}
        self.box.add_updater(self._box_updater())

        # dot follows box center (handy for arrows/lines)
        self.dot = Dot(color=YELLOW, radius=0.05).add_updater(
            lambda d: d.move_to(self.box.get_center())
        )

        # ---- equilibrium marker y0 ----
        fs = 34
        y0_text = (
            MathTex(r"y_0", font_size=fs)
            .move_to(self.axes.c2p(0, self.y0))
            .shift(LEFT * MED_SMALL_BUFF)
        )
        y0_line = Line(
            start=self.axes.y_axis.n2p(self.y0),
            end=self.axes.c2p(1.5, self.y0),
            color=YELLOW,
            stroke_width=1,
        )
        self.y0_marker = VGroup(y0_text, y0_line)

        # ---- current position horizontal line ----
        self.current_pos_line = Line(color=YELLOW, stroke_width=1.1)
        self.current_pos_line.add_updater(self._current_pos_line_updater())

        # ---- Δy dashed arrow + label ----
        self.delta_line = DashedVMobject(DoubleArrow(buff=0))
        self.delta_line.add_updater(self._delta_y_line_updater())
        self.delta_text = MathTex(r"\Delta y", font_size=26)
        self.delta_text.add_updater(self._delta_text_updater())

        # ---- force arrow (vertical) ----
        self.forces: Dict[str, VGroup] = {}
        self.add_force(self.force, RED, "F_k")
        # self.force_arrow = Arrow(color=RED, max_tip_length_to_length_ratio=0.15)
        # self.force_arrow.add_updater(self._force_arrow_updater())

        # ---- spring / damper (rebuilt every frame to follow endpoints) ----
        self.spring = VGroup()
        self.spring.add_updater(self._spring_updater())

        # ---- add everything ----
        self.add(
            self.axes,
            self.box,
            self.spring,
            self.y0_marker,
            self.dot,
            self.current_pos_line,
            self.delta_line,
            self.delta_text,
            *self.forces.values(),
            # self.force_arrow,
        )

    # ---------- Analytic kinematics / dynamics ----------
    def position(self) -> float:
        """y(t) in data units."""
        A, k, m, t = self.A.get_value(), self.k.get_value(), self.m.get_value(), self.time.get_value()
        omega = np.sqrt(k / m)
        return self.y0 - A * np.cos(omega * t)

    def force(self) -> float:
        """F = -k (y - y0) = -m ω² A cos(ωt) (no damping). Positive up."""
        A, k, m, t = self.A.get_value(), self.k.get_value(), self.m.get_value(), self.time.get_value()
        omega = np.sqrt(k / m)
        return A * omega**2 * np.cos(omega * t)

    # ---------- Anchors (ceiling -> top of box) ----------
    @property
    def start_anchor(self) -> np.ndarray:
        """Ceiling point (top support) directly above the box."""
        # match the box's x (in data), at the ceiling y = y_max
        x_data = self.axes.p2c(self.box.get_center())[0]
        y_support = self.axes.y_range[1]  # ceiling
        return self.axes.c2p(x_data, y_support)

    @property
    def end_anchor(self) -> np.ndarray:
        """Top of the box."""
        return self.box.get_top()

    # ---------- Updaters ----------
    def _box_updater(self) -> Callable[[Mobject, float], None]:
        def updater(mob: Rectangle, dt: float) -> None:
            # keep box centered at x ~ 1.0 (data), move along y
            target = (
                self.axes.c2p(
                    1.0, self.position_function(**self.position_function_kwargs)
                )
                + RIGHT * 0.0
            )
            # nudge so the box "sits" at its y (center is at y; no floor snap here)
            mob.move_to(target)

        return updater

    def _spring_updater(self) -> Callable[[Mobject, float], None]:
        def updater(mob: VMobject, dt: float) -> None:
            cls = SpringDamper2D if self.add_damper else Spring2D
            s = cls(
                XY_start=self.start_anchor,  # ceiling
                XY_end=self.end_anchor,  # top of box
                num_loops=self.loops_number,
                r=self.spring_r,
            )
            mob.become(s)

        return updater

    def _current_pos_line_updater(self) -> Callable[[Mobject, float], None]:
        def updater(mob: Line, dt: float) -> None:
            c = self.dot.get_center()  # scene coords
            y_data = self.axes.p2c(c)[1]
            end = self.axes.c2p(min(1.5, self.axes.x_range[1]), y_data)
            mob.put_start_and_end_on(c, end)

        return updater

    def _delta_y_line_updater(self) -> Callable[[Mobject, float], None]:
        def updater(mob: Mobject, dt: float) -> None:
            start = self.y0_marker[1].get_end()  # right end of y0 horizontal line
            end = self.current_pos_line.get_end()  # right end of current position line
            if np.linalg.norm(end - start) < 1e-6:
                end = start + np.array([1e-6, 0.0, 0.0])

            base = DoubleArrow(
                start=start, end=end, buff=0, max_tip_length_to_length_ratio=0.1
            ).match_style(mob)
            dashed = DashedVMobject(base, num_dashes=10, dashed_ratio=0.7).match_style(
                mob
            )
            mob.become(dashed)

        return updater

    def _delta_text_updater(self) -> Callable[[Mobject, float], None]:
        def updater(mob: MathTex, dt: float) -> None:
            y_pos = self.axes.p2c(self.delta_line.get_center())[1]
            # y_pos = self.delta_line.get_center()[1]
            mob.move_to(self.axes @ (1.8, y_pos, 0))

        return updater

    def _force_arrow_updater(
        self, callback: Callable
    ) -> Callable[[Mobject, float], None]:
        def updater(mob: Arrow, dt: float) -> None:
            start = self.dot.get_center()
            F = callback()
            end = start + UP * (F * 0.12)
            if np.allclose(end, start):
                end = start + UP * 1e-6
            mob.put_start_and_end_on(start, end)

        return updater

    def add_force(self, callback: Callable, color: ManimColor, label: str):
        arrow = Arrow(color=color, buff=0, max_tip_length_to_length_ratio=0.1)
        arrow.add_updater(self._force_arrow_updater(callback))
        arrow_label = MathTex(rf"{label}", font_size=20).match_color(arrow)
        arrow_label.add_updater(lambda mob: mob.next_to(arrow, RIGHT, SMALL_BUFF))
        self.forces[label] = VGroup(arrow, arrow_label)
        self.add(self.forces[label])
        return arrow, arrow_label

    def set_position_function(self, callback: Callable, **kwargs) -> None:
        self.position_function = callback
        self.position_function_kwargs = kwargs


class BaseClass(Scene):
    def __init__(self, vertical: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.k_trackers: List[ValueTracker] = [ValueTracker(i) for i in [1, 4, 16]]
        self.m_trackers: List[ValueTracker] = [ValueTracker(i) for i in [1, 1, 1]]
        self.beta_trackers: List[ValueTracker] = [
            ValueTracker(i) for i in [1, 1, 1]
        ]  # unused now
        self.amplitudes: List[ValueTracker] = [ValueTracker(i) for i in [1, 1, 1]]
        self.time_tracker = ValueTracker(0)

    def position_plot(
        self,
        axes: Axes,
        A: ValueTracker,
        k: ValueTracker,
        m: ValueTracker,
        color: ManimColor,
        time_tracker: ValueTracker,
    ):
        # f(τ) = A cos(√(k/m) τ)
        return axes.plot(
            lambda tau: A.get_value()
            * np.cos(np.sqrt(k.get_value() / m.get_value()) * tau),
            x_range=[0, time_tracker.get_value()],
            color=color,
        )

    def velocity_plot(
        self,
        axes: Axes,
        A: ValueTracker,
        k: ValueTracker,
        m: ValueTracker,
        color: ManimColor,
        time_tracker:ValueTracker
    ):
        # v(τ) = -A ω sin(ω τ)
        return axes.plot(
            lambda tau: -A.get_value()
            * np.sqrt(k.get_value() / m.get_value())
            * np.sin(np.sqrt(k.get_value() / m.get_value()) * tau),
            x_range=[0, time_tracker.get_value()],
            color=color,
        )

    def acceleration_plot(
        self,
        axes: Axes,
        A: ValueTracker,
        k: ValueTracker,
        m: ValueTracker,
        color: ManimColor,
        time_tracker:ValueTracker
    ):
        # a(τ) = -A ω^2 cos(ω τ)
        return axes.plot(
            lambda tau: -A.get_value()
            * (k.get_value() / m.get_value())
            * np.cos(np.sqrt(k.get_value() / m.get_value()) * tau),
            x_range=[0, time_tracker.get_value()],
            color=color,
        )


class SimpleHarmonicMotion(BaseClass):
    def __init__(self, *args, **kwargs):
        super().__init__(False, *args, **kwargs)

    def construct(self):
        MAX_TIME = 12

        # 3 stacked axes on the right: x(t), v(t), a(t)
        axes = (
            VGroup(
                *[
                    Axes(
                        x_range=[0, MAX_TIME, 3],
                        y_range=[-i, i, step],  # allow ± range
                        x_length=5,
                        y_length=3,
                    ).add_coordinates()
                    for i,step in zip([3,7,25],[2,4,10])
                ]
            )
            .arrange(DOWN, buff=SMALL_BUFF)
            .scale_to_fit_height(7.5)
            .to_edge(RIGHT)
        )

        # 3 horizontal mass–spring systems on the left
        systems = (
            VGroup(
                *[
                    HorizontalMassSpringSystem(5, A, k, m, self.time_tracker)
                    for A, k, m in zip(
                        self.amplitudes, self.k_trackers, self.m_trackers
                    )
                ]
            )
            .arrange(DOWN, buff=SMALL_BUFF)
            .scale_to_fit_height(7.5)
            .to_edge(LEFT)
        )

        # Colors per system
        colors = [RED, GREEN, BLUE]

        # position, velocity, acceleration plots – each on its own axes
        position_plots = VGroup(
            *[
                always_redraw(
                    lambda ax=axes[0],A=A, k=k, m=m, c=c: self.position_plot(
                        ax, A, k, m, c, self.time_tracker
                    )
                )
                for A, k, m, c in zip(
                    self.amplitudes,
                    self.k_trackers,
                    self.m_trackers,
                    colors,
                )
            ]
        )
        # The above line draws only x(t) in the top axes for each system color. If you want
        # one curve per system on the SAME top axes, this is correct. If you prefer separate axes per curve,
        # create 3 separate Axes groups; below I put v(t) on axes[1], a(t) on axes[2]:

        velocity_plots = VGroup(
            *[
                always_redraw(
                    lambda ax=axes[1], A=A, k=k, m=m, c=c: self.velocity_plot(
                        ax, A, k, m, c, self.time_tracker
                    )
                )
                for A, k, m, c in zip(
                    self.amplitudes, self.k_trackers, self.m_trackers, colors
                )
            ]
        )

        acceleration_plots = VGroup(
            *[
                always_redraw(
                    lambda ax=axes[2], A=A, k=k, m=m, c=c: self.acceleration_plot(
                        ax, A, k, m, c, self.time_tracker
                    )
                )
                for A, k, m, c in zip(
                    self.amplitudes, self.k_trackers, self.m_trackers, colors
                )
            ]
        )

        # Add labels to axes
        # labels = VGroup(
        #     axes[0].get_axis_labels(MathTex("t"), MathTex("x(t)")),
        #     axes[1].get_axis_labels(MathTex("t"), MathTex("v(t)")),
        #     axes[2].get_axis_labels(MathTex("t"), MathTex("a(t)")),
        # )

        self.add(
            systems, axes,  position_plots, velocity_plots, acceleration_plots
        )

        # drive time
        self.wait()
        self.play(
            self.time_tracker.animate.set_value(MAX_TIME),
            run_time=MAX_TIME,
            rate_func=linear,
        )
        self.wait()


class TestingScene(Scene):
    def construct(self):
        A = ValueTracker(1)
        k = ValueTracker(9)
        m = ValueTracker(1)
        time = ValueTracker(0)
        horizontal_system = (
            HorizontalMassSpringSystem(x0=5, A=A, k=k, m=m, time=time, axes_y_length=2)
            .to_edge(LEFT)
            .scale_to_fit_height(8)
        )
        vertical_system = VerticalMassSpringSystem(
            y0=-4.0,
            A=A,
            k=k,
            m=m,
            time=time,
            dumper=True,
            loops_number=5,
            box_width=1.2,
            box_height=0.9,
        ).to_edge(RIGHT)
        vertical_system.add_force(lambda: -9.81 * m.get_value(), GREEN, "F_g")

        # obj = NumberPlane()
        # spring = SpringDamper2D(XY_start=np.array([-3,4,0]),XY_end=np.array([-3,0,0]),num_loops=5)
        # self.add(obj,spring)
        self.add(horizontal_system, vertical_system)
        self.play(time.animate.set_value(8), run_time=12, rate_func=linear)
        self.wait()


# with tempconfig({"quality": "low_quality", "preview": True}):
#     SimpleHarmonicMotion().render()
