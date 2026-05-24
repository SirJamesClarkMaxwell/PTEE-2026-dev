from manim import *
from typing import List, Dict, Any, Tuple


#########################################################
###################### Workshop 1 ######################
#########################################################
class AddingObjectsToScene(Scene):
    def construct(self):
        # basic shapes for add/play demo
        square: Square = Square(side_length=2)
        circle: Circle = Circle(radius=3)
        triangle: Triangle = Triangle()

        # self.play(Create(NumberPlane()))
        self.add(square)
        self.wait()
        self.play(Create(circle))
        self.wait()
        self.play(FadeIn(triangle, shift=UP))
        self.wait()
        self.play(FadeOut(square), FadeOut(circle), FadeOut(triangle), run_time=2)
        self.wait()


class PositioningObjects(Scene):
    def construct(self):
        # show positioning and shifting examples
        title = Title("Pozycjonowanie ObiektÃ³w").to_edge(UP, buff=MED_LARGE_BUFF)
        square: Square = Square(side_length=2)
        triangle: Triangle = Triangle()
        dot: Dot = Dot()
        directions: List[np.ndarray] = [RIGHT, UP, LEFT, DOWN]
        self.add(title, square, triangle)

        self.play(square.animate.shift(LEFT))
        self.wait()
        self.play(square.animate.shift(RIGHT))
        self.wait()
        self.play(square.animate.shift(UP))
        self.wait()
        self.play(square.animate.shift(DOWN))
        self.wait()

        for direction in directions:
            self.play(square.animate.shift(direction * 2))
            self.wait()

        for buff in [0, SMALL_BUFF, MED_SMALL_BUFF, MED_LARGE_BUFF, LARGE_BUFF]:
            self.play(triangle.animate.next_to(square, RIGHT, buff=buff))
            self.wait()

        for aligned_edge in [UP, DOWN]:
            self.play(
                triangle.animate.next_to(
                    square, RIGHT, aligned_edge=aligned_edge, buff=MED_SMALL_BUFF
                )
            )
            self.wait()
        self.play(FadeOut(square), FadeOut(triangle))

        number_plane = NumberPlane()
        axes = Axes().add_coordinates()
        self.play(Create(number_plane), Create(dot))
        self.play(dot.animate.move_to([1, 2, 0]))
        self.wait()
        self.play(Create(axes))
        self.play(dot.animate.move_to(axes @ ([1, 2])))
        self.wait()


#########################################################
###################### Workshop 2 ######################
#########################################################


def shift_object(mobject: Mobject, direction: np.ndarray, amount: float) -> Animation:
    # helper: shift a mobject by direction * amount
    return mobject.animate.shift(direction * amount)


class Workshop1Summary(Scene):
    def construct(self):
        # quick recap scene
        circ: Circle = Circle(2)
        sq: Square = Square().set_fill(BLUE, 0.5)
        dot: Dot = Dot().set_color(YELLOW)
        self.add(circ)
        self.play(Create(sq), FadeIn(dot))
        self.wait()
        self.play(sq.animate.next_to(circ, RIGHT, LARGE_BUFF))
        self.wait()
        self.play(dot.animate.shift((LEFT + RIGHT) * 2))
        self.wait()


class ForLoopExample(Scene):
    def construct(self):
        # 1. Add a variable controlling square side length; first set it manually for all squares
        # 2. Add individual squares to a list manually
        # 3. Arrange squares in a loop -> indexing (slicing operator)
        # 4. Introduce VGroup and the arrange method
        # 5. List comprehension + arrange <- as a side note, emphasize this is used very often
        # 6. Add a function that generates a list of objects of given length from a template
        # manual layout of squares for demonstration
        square: Square = Square()
        square1: Square = Square()
        square2: Square = Square()
        square3: Square = Square()
        square4: Square = Square()
        square5: Square = Square()

        square.to_edge(LEFT)
        square1.next_to(square, RIGHT, MED_LARGE_BUFF)
        square2.next_to(square1, RIGHT, MED_LARGE_BUFF)
        square3.next_to(square2, RIGHT, MED_LARGE_BUFF)
        square4.next_to(square3, RIGHT, MED_LARGE_BUFF)
        square5.next_to(square4, RIGHT, MED_LARGE_BUFF)
        self.add(square, square1, square2, square3, square4, square5)


class MoveToPositioning(Scene):
    def construct(self):
        axes: Axes = Axes().add_coordinates()
        plane: NumberPlane()
        dot: Dot()
        # 1. plain move_to
        # 2. move_to + shift
        # 3. difference between local and global coordinate systems


class Plotting(Scene):
    def construct(self):
        # 1. parameters accepted by Axes
        # plot a simple sine function
        axes: Axes = Axes(
            x_range=[-5, 5, 2], y_range=[-1.2, 1.2, 0.4], x_length=10, y_length=5
        ).add_coordinates()
        axes_labels = axes.get_axis_labels("x", MathTex(r"f(x)=x^2"))

        sine_plot: ParametricFunction = axes.plot(
            lambda x: np.sin(x), x_range=[-5, 5, 0.01], color=YELLOW
        )
        self.add(axes, axes_labels, sine_plot)


DEFAULT_MEDIUM_DOT_RADIUS = 0.04


class Slider(Group):
    def __init__(
        self,
        x_range: List[float],
        length: float,
        tracker: ValueTracker,
        color: ManimColor,
        label: str = "",
        post_label: str = "",
        label_font_size: int = 25,
        marker_size: float = 0.1,
        marker_direction=RIGHT,
        label_direction=DOWN,
        attach_label_to_marker: bool = False,
        number_label_scientific: bool = False,
        numberline_kwargs: Dict[str, Any] = {},
    ) -> None:

        # number line and tracker-driven marker
        self.numberline = NumberLine(x_range, length=length, **numberline_kwargs)

        self.tracker = tracker
        self.marker = self._make_marker(marker_size, marker_direction, color)
        self.label = self._make_label(
            label=label,
            post_label=post_label,
            label_font_size=label_font_size,
            number_label_scientific=number_label_scientific,
            color=color,
            label_direction=label_direction,
            attach_label_to_marker=attach_label_to_marker,
        )

        super().__init__(self.numberline, self.marker, self.label)

    def _make_marker(self, marker_size, marker_direction, color) -> VGroup:
        # marker dot + triangle pointer
        dot = Dot(
            self.numberline.n2p(self.tracker.get_value()), DEFAULT_MEDIUM_DOT_RADIUS
        ).set_color(color)
        dot.add_updater(
            lambda mob, dt: mob.move_to(self.numberline.n2p(self.tracker.get_value()))
        )

        marker = (
            Triangle()
            .rotate(PI / 2)
            .scale(marker_size)
            .next_to(dot, marker_direction, buff=SMALL_BUFF)
            .set_color(color)
            .set_fill(color, 1)
        )
        marker.add_updater(
            lambda mob, dt: mob.next_to(dot, marker_direction, SMALL_BUFF)
        )

        return Group(dot, marker)

    def _make_label(
        self,
        label,
        post_label,
        label_font_size,
        color: ManimColor,
        number_label_scientific: bool,
        label_direction=DOWN,
        attach_label_to_marker: bool = False,
        decimal_places: int = 1,
    ) -> VGroup:

        # numeric label that follows the tracker
        basic_label = MathTex(label, font_size=label_font_size)
        if not number_label_scientific:
            number_label = DecimalNumber(
                10 ** self.tracker.get_value(),
                font_size=label_font_size,
                num_decimal_places=decimal_places,
            )
            number_label.add_updater(
                lambda mob: mob.set_value(self.tracker.get_value())
            )
        else:
            number_label = MathTex(
                rf"{10**self.tracker.get_value():.1e}", font_size=label_font_size
            )
        post_label = MathTex(post_label, font_size=label_font_size)
        vg = (
            VGroup(basic_label, number_label, post_label)
            .arrange(RIGHT, SMALL_BUFF * 1.4)
            .set_color(color)
        )
        vg.next_to(self.numberline, label_direction, MED_LARGE_BUFF, aligned_edge=DOWN)

        if attach_label_to_marker:
            vg.add_updater(
                lambda mob, dt: mob.next_to(
                    self.marker, label_direction, SMALL_BUFF * 1.3
                )
            )

        return vg


class FourierSeries(Scene):
    def construct(self):
        # --- object: summation sign ---
        tex = MathTex(r"\sum \limits_{n=0}^{\infty}").scale(2).to_edge(RIGHT)

        # Safe extraction of the summation glyph itself:
        sum_glyph = tex[0][1]
        self.add(tex)

        # --- axes for y(t) preview (optional) ---
        axes = Axes(
            x_range=[0, 1, 0.1],
            y_range=[-2, 2, 0.5],
            x_length=5,
            y_length=3,
            tips=False,
        ).to_edge(LEFT)
        self.add(axes)

        # --- sample the curve in SCENE space (consistent units!) ---
        N = 2048
        ts = np.linspace(0.0, 1.0, N, endpoint=False)

        z = np.zeros(N, dtype=np.complex128)
        plot_pts = []

        # build complex signal from the glyph outline
        for i, t in enumerate(ts):
            p = (
                sum_glyph.point_from_proportion(float(t)) - sum_glyph.get_center()
            )  # punkt w scenie
            z[i] = p[0] + 1j * p[1]  # complex signal in scene space
            plot_pts.append(axes.c2p(float(t), float(p[1])))  # preview: y(t) = p[1]

        plot = VMobject().set_points_smoothly(plot_pts)
        self.play(Create(plot), run_time=1.2)

        # --- FFT -> take n_terms strongest components (without DC) ---
        n_terms = 100
        coeffs = self.get_fourier_coeffs(z, n_terms=n_terms, remove_dc=True)

        # --- epicykle sterowane parametrem t in [0,1] ---
        t_tracker = ValueTracker(0.0)
        origin = ORIGIN  # LEFT * 4 + DOWN * 1.0
        scale = 2.0  # arrow length scale (tune as needed)

        arrows = VGroup(
            *[Arrow(ORIGIN, ORIGIN + RIGHT, buff=0, stroke_width=4) for _ in coeffs]
        )

        # update arrow chain from Fourier coefficients
        def update_chain(mob: VGroup) -> None:
            t = t_tracker.get_value()
            start = origin

            for arrow, (omega, c) in zip(mob, coeffs):
                v = scale * c * np.exp(1j * omega * t)  # wektor zespolony
                vec = np.array([v.real, v.imag, 0.0])
                arrow.put_start_and_end_on(start, start + vec)
                start = arrow.get_end()

        arrows.add_updater(update_chain)

        # trace the endpoint of the last arrow
        dot = always_redraw(
            lambda: Dot(arrows[-1].get_end(), radius=0.04, color=YELLOW)
        )

        self.add(arrows, dot)
        path = TracedPath(dot.get_center, stroke_width=3).set_color(YELLOW)
        self.add(path)
        self.play(t_tracker.animate.set_value(1.0), run_time=8, rate_func=linear)
        self.wait(0.5)

        arrows.clear_updaters()

    def get_fourier_coeffs(
        self,
        z: np.ndarray,
        n_terms: int,
        *,
        remove_dc: bool = True,
    ) -> List[Tuple[float, complex]]:
        """
        Returns a list of (omega_k, c_k) for the strongest complex FFT components.
        t is a parameter in [0,1], so omega_k = 2?k.
        """
        z = np.asarray(z, dtype=np.complex128)
        N = z.size

        if remove_dc:
            z = z - np.mean(z)

        # FFT and frequencies (including negative ones!)
        C = np.fft.fft(z) / N
        k = np.fft.fftfreq(N, d=1.0 / N)  # daje ...,-2,-1,0,1,2,...
        omega = 2.0 * np.pi * k

        # remove DC
        valid = k != 0
        idx = np.where(valid)[0]

        # choose the strongest by |C_k|
        idx_sorted = idx[np.argsort(np.abs(C[idx]))[::-1]]
        idx_top = idx_sorted[:n_terms]

        out = [(float(omega[i]), complex(C[i])) for i in idx_top]
        out.sort(key=lambda p: abs(p[0]))  # from low frequencies
        return out
