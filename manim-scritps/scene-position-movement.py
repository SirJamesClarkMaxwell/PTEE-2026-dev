from manim import *
from manim_slides import Slide
from collections.abc import Iterable
from contextlib import contextmanager
from typing import Generator, List, Dict
import io
import numpy as np
import tokenize

ENABLE_SLIDES = False
VIDEO = True

BaseScene = Slide if ENABLE_SLIDES else Scene


class TransformMatchingCode(TransformMatchingTex):
    @staticmethod
    def get_mobject_parts(mobject: Mobject) -> list[Mobject]:
        if isinstance(mobject, (Group, VGroup)):
            parts = []
            for submobject in mobject.submobjects:
                parts.extend(TransformMatchingCode.get_mobject_parts(submobject))
            return parts
        if hasattr(mobject, "match_parts"):
            return mobject.match_parts
        return TransformMatchingTex.get_mobject_parts(mobject)

    @staticmethod
    def get_mobject_key(mobject: Mobject) -> str:
        return mobject.tex_string

class Base(BaseScene):
    default_scene_width = 8
    default_scene_height = 4.5
    default_scene_shift = UP * 0.35
    default_corner_radius = 0.2

    def wait_or_slide(self):
        self.next_slide() if ENABLE_SLIDES else self.wait()

    @contextmanager
    def new_section(
        self,
        name: str = "unnamed",
        section_type: str = DefaultSectionType.NORMAL,
        skip_animations: bool = False,
    ) -> Generator[None, None, None]:
        print(f"Entering section: {name}")
        self.next_section(name, section_type, skip_animations)
        yield
        print(f"Exiting section: {name}")

    def default_scene(self) -> RoundedRectangle:
        return RoundedRectangle(
            width=self.default_scene_width,
            height=self.default_scene_height,
            corner_radius=self.default_corner_radius,
            stroke_color=WHITE,
            fill_color=BLACK,
            fill_opacity=0.05,
        ).shift(self.default_scene_shift)

    def play_timeline(self, timeline: dict[float, Animation | Iterable[Animation]]):
        previous_t = 0

        for t, timeline_item in sorted(timeline.items()):
            to_wait = t - previous_t
            if to_wait > 0:
                self.wait(to_wait)

            after_play = None
            animations = timeline_item() if callable(timeline_item) else timeline_item
            if (
                isinstance(animations, tuple)
                and len(animations) == 2
                and callable(animations[1])
            ):
                animations, after_play = animations
            if isinstance(animations, Animation):
                animations = [animations]

            self.play(*animations)
            if after_play is not None:
                after_play()
            previous_t = t + max(animation.run_time for animation in animations)

    def build_timeline(
        self,
        steps: Iterable,
        animation_builder,
        start_time: float = 0,
        step_time: float = 2,
    ) -> dict[float, Animation | Iterable[Animation]]:
        return {
            start_time + index * step_time: lambda step=step: animation_builder(step)
            for index, step in enumerate(steps)
        }


class WhatIsAScene(Base):
    def construct(self) -> None:
        with self.new_section("Initialize scene objects", section_type=True):
            height = Variable(4, label="height: ")
            width = Variable(5, label="width: ")

            scene = RoundedRectangle(
                width=width.tracker.get_value(),
                height=height.tracker.get_value(),
                corner_radius=0.2,
            )

            def scene_updater():
                def updater(mob, dt):
                    scene.stretch_to_fit_width(width.tracker.get_value())
                    scene.stretch_to_fit_height(height.tracker.get_value())

                return updater

            scene.add_updater(scene_updater())
            scene_text = (
                Text("Scene = Canvas", font_size=40)
                .next_to(scene, UP, buff=SMALL_BUFF)
                .add_updater(lambda mob: mob.next_to(scene, UP, SMALL_BUFF))
            )

            def generate_arrows():
                shift_value = 0.5
                arrow_kwargs = {"buff": 0}

                def width_arrow():
                    offset = height.tracker.get_value() / 2 * shift_value
                    left, right = scene.get_critical_point(
                        LEFT
                    ), scene.get_critical_point(RIGHT)
                    left[1] -= offset
                    right[1] -= offset
                    return DashedVMobject(
                        DoubleArrow(
                            left,
                            right,
                            **arrow_kwargs,
                        )
                    )

                def height_arrow():
                    offset = width.tracker.get_value() / 2 * shift_value
                    down, up = scene.get_critical_point(DOWN), scene.get_critical_point(
                        UP
                    )
                    down[0] -= offset
                    up[0] -= offset
                    return DashedVMobject(
                        DoubleArrow(
                            down,
                            up,
                            **arrow_kwargs,
                        )
                    )

                return width_arrow, height_arrow

            arrows = VGroup(*(always_redraw(it) for it in generate_arrows()))
            height.add_updater(
                lambda mob: mob.next_to(arrows[1].get_center(), RIGHT, SMALL_BUFF)
            )
            width.add_updater(
                lambda mob: mob.next_to(arrows[0].get_center(), UP, SMALL_BUFF)
            )

        with self.new_section("Show canvas", skip_animations=True):
            self.play(Create(scene), Write(scene_text), lag_ratio=0.5)
            self.wait_or_slide()

        with self.new_section("Show and change dimensions", skip_animations=True):
            self.play(*[Create(it) for it in arrows], Write(width), Write(height))
            self.play(height.tracker.animate.set_value(6))
            self.wait_or_slide()
            self.play(width.tracker.animate.set_value(8.001))
            self.wait_or_slide()
            scene.clear_updaters()
            self.play(FadeOut(VGroup(arrows, width, height)))
            self.wait_or_slide()

        with self.new_section("Animate fill color", skip_animations=True):
            colors: List[ValueTracker] = [ValueTracker(0) for _ in range(3)]

            def build_color() -> ManimColor:
                rgb = [tracker.get_value() for tracker in colors]
                return ManimColor.from_rgb(rgb)

            def color_text() -> str:
                r, g, b = build_color().to_int_rgb()
                return f"r, g, b = {r:03d}, {g:03d}, {b:03d}"

            color_square = Square(0.3, fill_color=build_color(), fill_opacity=1)
            color_square.add_updater(lambda mob: mob.set_fill(build_color(), opacity=1))

            color_label = Text(color_text(), font="Consolas", font_size=28)
            color_label.add_updater(
                lambda mob: mob.become(
                    Text(color_text(), font="Consolas", font_size=28).move_to(mob)
                )
            )

            box = VGroup(color_square, color_label)
            box.arrange(RIGHT).next_to(scene, DOWN, SMALL_BUFF)

            self.play(Create(box[0]), Write(box[1]))
            scene.add_updater(lambda mob: mob.set_fill(build_color(), opacity=1))
            target_colors = [
                (1, 0, 0),
                (1, 1, 0),
                (0, 1, 0),
                (0, 1, 1),
                (0, 0, 1),
                (1, 0, 1),
                (1, 1, 1),
                (0, 0, 0),
            ]

            for target_color in target_colors:
                self.play(
                    *[
                        tracker.animate.set_value(value)
                        for tracker, value in zip(colors, target_color)
                    ],
                    run_time=1.5,
                    rate_func=linear,
                )

            self.wait_or_slide()

        with self.new_section("Scene control points"):
            pass


class SimplePositioning(Base):

    def command_label(self, command: str) -> Text:
        colors = {
            tokenize.NAME: WHITE,
            tokenize.NUMBER: RED,
            tokenize.OP: GREY_B,
        }
        direction_names = {"UP", "DOWN", "LEFT", "RIGHT", "UL", "UR", "DL", "DR"}
        object_names = {"dot", "scene", "plane", "animate"}
        method_names = {"move_to", "get_center", "get_critical_point", "c2p"}

        tokens = [
            token
            for token in tokenize.generate_tokens(io.StringIO(command).readline)
            if token.string
            and token.type not in (tokenize.ENCODING, tokenize.ENDMARKER, tokenize.NEWLINE)
        ]
        code = Text(command, font="Consolas", font_size=24)
        match_parts = VGroup()
        previous_token = None

        for token in tokens:
            start = token.start[1]
            end = token.end[1]
            color = colors.get(token.type, WHITE)
            if token.string in object_names:
                color = BLUE_B
            elif token.string in method_names:
                color = YELLOW_B
            elif token.string in direction_names:
                color = RED
            elif previous_token is not None and previous_token.string == ".":
                color = GREEN_B

            code[start:end].set_color(color)
            token_mobject = VGroup(*code[start:end])
            token_key = f"{token.type}:{token.string}:{start}"
            token_mobject.tex_string = token_key
            for char in token_mobject:
                char.tex_string = token_key
            match_parts.add(token_mobject)

            previous_token = token

        code.match_parts = match_parts
        return code

    def critical_point_command(self, point_name: str) -> str:
        if point_name == "ORIGIN":
            return "dot.animate.move_to(scene.get_center())"
        edge_commands = {
            "UP": "get_top()",
            "DOWN": "get_bottom()",
            "LEFT": "get_left()",
            "RIGHT": "get_right()",
        }
        if point_name in edge_commands:
            return f"dot.animate.move_to(scene.{edge_commands[point_name]})"
        return f"dot.animate.move_to(scene.get_corner({point_name}))"

    def coordinate_command(self, x: float, y: float) -> str:
        return f"dot.animate.move_to(plane.c2p({x:g}, {y:g}))"

    def critical_point_label(
        self, label: str, position: np.ndarray, direction: np.ndarray
    ) -> Text:
        text = Text(label, font="Consolas", font_size=18).next_to(
            position, direction, buff=SMALL_BUFF
        )
        text[0][-3:-1].set_color(RED)
        return text

    def update_command(self, command: Text, next_command_text: str, run_time: float = 1):
        next_command = self.command_label(next_command_text).move_to(command)
        return TransformMatchingCode(
            command,
            next_command,
            transform_mismatches=False,
            fade_transform_mismatches=False,
            run_time=run_time,
        ), next_command

    def construct(self) -> None:
        with self.new_section("Initialize positioning objects",skip_animations=False):
            scene_box = self.default_scene()
            title = Text("SimplePositioning", font_size=38).next_to(
                scene_box, UP, MED_SMALL_BUFF
            )

            critical_point_directions = {
                "ORIGIN": (DOWN, scene_box.get_center()),
                "UP": (UP, scene_box.get_top()),
                "RIGHT": (RIGHT, scene_box.get_right()),
                "DOWN": (DOWN, scene_box.get_bottom()),
                "LEFT": (LEFT, scene_box.get_left()),
                "UL": UL,
                "UR": UR,
                "DL": DL,
                "DR": DR,
            }
            critical_points_map: Dict[str, tuple[str, np.ndarray, str]] = {
                point_name: (
                    point_name,
                    point_data[1]
                    if isinstance(point_data, tuple)
                    else scene_box.get_corner(point_data),
                    self.critical_point_command(point_name),
                )
                for point_name, point_data in critical_point_directions.items()
            }

            point_dots = VGroup(
                *[
                    Dot(position, radius=0.045, color=GREY_B)
                    for _, position, _ in critical_points_map.values()
                ]
            )
            point_labels = VGroup(
                *[
                    self.critical_point_label(
                        label, position, critical_point_directions[point_name]
                        if not isinstance(critical_point_directions[point_name], tuple)
                        else critical_point_directions[point_name][0]
                    )
                    for point_name, (
                        label,
                        position,
                        _,
                    ) in critical_points_map.items()
                ]
            )

            moving_dot = Dot(
                critical_points_map["ORIGIN"][1], radius=0.09, color=RED
            )
            command = {
                "mobject": self.command_label(
                    critical_points_map["ORIGIN"][2]
                ).next_to(scene_box, DOWN, MED_LARGE_BUFF)
            }

        with self.new_section("Show critical points", skip_animations=False):
            self.play(Create(scene_box), Write(title))
            self.play(FadeIn(point_dots), Write(point_labels), FadeIn(moving_dot))
            self.play(Write(command["mobject"]))
            self.wait_or_slide()

        with self.new_section("Move through critical points", skip_animations=False):
            critical_point_steps = [
                "UR",
                "DR",
                "DL",
                "UL",
                "UP",
                "RIGHT",
                "DOWN",
                "LEFT",
                "ORIGIN",
            ]

            def build_critical_point_animation(point_name: str):
                _, position, command_text = critical_points_map[point_name]
                command_animation, next_command = self.update_command(
                    command["mobject"], command_text, run_time=1
                )
                return [
                    Transform(
                        moving_dot,
                        moving_dot.copy().move_to(position),
                        run_time=2,
                        rate_func=linear,
                    ),
                    command_animation,
                ], lambda: command.update({"mobject": next_command})

            self.play_timeline(
                self.build_timeline(
                    critical_point_steps,
                    build_critical_point_animation,
                    step_time=2,
                )
            )

        with self.new_section("Show coordinate system", skip_animations=False):
            plane = NumberPlane(
                x_length=self.default_scene_width,
                y_length=self.default_scene_height,
                background_line_style={
                    "stroke_color": BLUE_D,
                    "stroke_width": 1,
                    "stroke_opacity": 0.55,
                },
                axis_config={
                    "stroke_color": BLUE_B,
                    "stroke_width": 2,
                    "include_ticks": True,
                },
            )
            plane.shift(scene_box.get_center() - plane @ (0, 0, 0))
            coordinate_labels = VGroup(
                *[
                    Text(str(x), font="Consolas", font_size=16).next_to(
                        plane.c2p(x, 0), DOWN, buff=0.08
                    )
                    for x in range(-7, 8)
                    if x != 0
                ],
                *[
                    Text(str(y), font="Consolas", font_size=16).next_to(
                        plane.c2p(0, y), LEFT, buff=0.08
                    )
                    for y in range(-4, 5)
                    if y != 0
                ],
            )

            self.play(FadeIn(plane), Write(coordinate_labels))
            self.wait_or_slide()

        with self.new_section("Move to coordinates", skip_animations=False):
            coordinate_steps = {
                "origin": (0, 0),
                "upper right": (2, 1),
                "upper left": (-3, 1.5),
                "lower right": (3, -1),
                "lower left": (-1, -1.5),
            }
            coordinate_map: Dict[str, tuple[tuple[float, float], str]] = {
                label: (coordinates, self.coordinate_command(*coordinates))
                for label, coordinates in coordinate_steps.items()
            }

            def build_coordinate_animation(step):
                coordinates, command_text = step
                x, y = coordinates
                command_animation, next_command = self.update_command(
                    command["mobject"], command_text, run_time=0.6
                )
                return [
                    Transform(
                        moving_dot,
                        moving_dot.copy().move_to(plane.c2p(x, y)),
                        run_time=1.2,
                        rate_func=linear,
                    ),
                    command_animation,
                ], lambda: command.update({"mobject": next_command})

            self.play_timeline(
                self.build_timeline(
                    coordinate_map.values(),
                    build_coordinate_animation,
                    step_time=1.2,
                )
            )

            self.wait_or_slide()


def main():
    config = {
        "preview": True if VIDEO else False,
        "quality": "low_quality",
        "save_last_frame": True if not VIDEO else False,
        # "disable_caching": True,
    }
    with tempconfig(config):
        scene = SimplePositioning()
        scene.render()


if __name__ == "__main__":
    main()
