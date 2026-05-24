from manim import *


class PlotsExample(Scene):
    def construct(self):
        # define axis ranges and create axes
        x_range = [-3 * PI, 3 * PI, PI / 2]
        y_range = [-1.5, 1.5, 0.5]
        axes = Axes(
            x_range=x_range, x_length=10, y_range=y_range, y_length=6, tips=False
        )

        # helper: build x-axis labels for multiples of pi/2
        def create_x_lable(factor, ax):
            if factor % 2 == 0:
                label = MathTex(rf"{factor}\pi")
            else:
                label = MathTex(rf"\frac{{{factor}\pi}}{2}")
            label.scale(0.75)
            position = ax.c2p((PI / 2) * factor, 0, 0)
            label.next_to(Dot(position), DOWN, buff=SMALL_BUFF)
            return label

        # generate x-axis and y-axis labels
        x_label = VGroup(*[create_x_lable(i, axes) for i in range(-6, 6) if i != 0])

        y_labels = VGroup(
            *[
                MathTex(rf"{i}")
                .scale(0.75)
                .next_to(Dot(axes.c2p(0, i, 0)), LEFT, buff=SMALL_BUFF)
                for i in np.arange(-1.5, 2, 0.5)
                if i != 0
            ]
        )

        # define functions and plot them
        def cos(x):
            return np.cos(x)

        sin_graph = axes.plot(lambda x: np.sin(x), x_range, color=BLUE)
        cos_graph = axes.plot(cos, x_range, color=RED)

        # add labels near the graph endpoints
        sin_graph_lable = MathTex(r"\sin(x)", color=BLUE).next_to(
            sin_graph.get_end(), RIGHT, SMALL_BUFF
        )
        cos_graph_lable = MathTex(r"\cos(x)", color=RED).next_to(
            cos_graph.get_end(), RIGHT, SMALL_BUFF
        )

        self.add(
            axes,
            sin_graph,
            cos_graph,
            sin_graph_lable,
            cos_graph_lable,
            x_label,
            y_labels,
        )


class SimpleUpdator(Scene):
    def construct(self):
        square = Square()
        text = Tex("On the Right").next_to(square, RIGHT, buff=SMALL_BUFF)

        # Method 1: add_updater - anonymous function
        # text.add_updater(lambda mob: mob.next_to(square,RIGHT,buff=SMALL_BUFF))

        # Method 2: add_updater - named function
        # def text_updater(sq):
        #     def updater(mob,dt):
        #         mob.next_to(sq,RIGHT,buff=SMALL_BUFF)
        #     return updater
        # text.add_updater(text_updater(square))

        # Method 3: always_redraw
        # text = always_redraw(lambda: Tex("On the Right").next_to(square,RIGHT,buff=SMALL_BUFF))

        # add a simple rotation updater
        self.add(square)

        def rotate_updater():
            def updater(mob, dt):
                mob.rotate(PI / 3)

            return updater

        square.add_updater(rotate_updater)

        # self.add(square,text)

        # for item in [RIGHT,UP,LEFT,DOWN]:
        #     self.play(square.animate.shift(2*item))
        self.wait()


class PlotUpdater(Scene):
    def construct(self):
        # axes + labels setup
        axes = Axes(x_range=[0, 10, 1], y_range=[0, 100, 10], tips=False)
        labels = axes.get_axis_labels("x", "f(x)")
        x_tracker = ValueTracker(0)

        # function and its plot
        def func(x):
            return 2 * (x - 5) ** 2

        graph = axes.plot(func, x_range=[0, 10], color=BLUE)

        # dot follows the graph using a tracker
        dot = Dot(color=YELLOW).move_to(axes.c2p(0, func(0)))

        # updater for the moving dot
        def dot_updater(ax, tracerk):
            def updater(mob, dt):
                mob.move_to(ax.c2p(tracerk.get_value(), func(tracerk.get_value())))

            return updater

        dot.add_updater(dot_updater(axes, x_tracker))

        self.play(Create(axes), Write(labels), Create(graph))
        self.add(dot)
        self.play(x_tracker.animate.set_value(10), run_time=10)
        self.wait()


class GraphAreaPlot(Scene):
    def construct(self):
        # axes for area between curves
        axes = Axes(
            x_range=[0, 4],
            y_range=[0, 5],
            x_axis_config={"numbers_to_include": [2, 3]},
            tips=False,
        )
        label = axes.get_axis_labels()

        # curves and filled regions
        def curve1(x):
            return 4 * x - x**2

        def curve2(x):
            return 0.8 * x**2 - 3 * x + 4

        curve_1 = axes.plot(curve1, x_range=[0, 4], color=BLUE)
        curve_2 = axes.plot(curve2, x_range=[0, 4], color=GREEN)

        rieman_rectagles = axes.get_riemann_rectangles(
            curve_1, x_range=[0, 0.6], dx=0.1, color=[RED, YELLOW]
        )
        area = axes.get_area(
            curve_2,
            x_range=[2, 3],
            bounded_graph=curve_1,
            color=[BLUE, GREEN],
            opacity=0.7,
        )

        self.add(axes, label, curve_1, curve_2, rieman_rectagles, area)


class RotatingUpdator(Scene):
    def construct(self):
        # compare updater with and without dt scaling
        t1 = Text("Updater bez parametru dt").scale(0.75).shift(UP).to_edge(LEFT)
        t2 = Text("Updater parametrem dt").scale(0.75).shift(DOWN).to_edge(LEFT)
        square1 = Square().scale(0.75).next_to(t1, RIGHT, buff=LARGE_BUFF)
        square2 = Square().scale(0.75).next_to(t2, RIGHT, buff=LARGE_BUFF)

        # rotation speed independent of dt
        def non_dt_rotate_updater():
            def updater(mob, dt):
                mob.rotate(PI / 3)

            return updater

        # rotation scaled by dt
        def dt_rotate_updater():
            def updater(mob, dt):
                mob.rotate((PI / 3) * dt)

            return updater

        self.add(square1, square2, t1, t2)

        square1.add_updater(non_dt_rotate_updater())
        square2.add_updater(dt_rotate_updater())

        self.wait(3)
