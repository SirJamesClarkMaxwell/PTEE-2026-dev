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
