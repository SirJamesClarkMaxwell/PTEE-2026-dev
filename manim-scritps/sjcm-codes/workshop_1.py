from manim import *
from typing import List


class Example(Scene):
    def construct(self):
        # basic shapes for simple add/play demo
        circle: Circle = Circle()
        triangle: Triangle = Triangle(color=YELLOW)
        square: Square = Square()

        self.wait()
        self.add(circle)
        self.wait()
        self.play(Create(triangle), run_time=2)
        self.wait()
        self.play(FadeIn(square, shift=UP))
        self.wait()
        self.play(FadeOut(square), FadeOut(triangle), FadeOut(circle))
        self.wait()


class PositioningObjects(Scene):
    def construct(self):
        # move circle next to a square with different buffers
        circle: Circle = Circle(radius=2)
        square: Square = Square(color=YELLOW)
        self.add(circle, square)
        buffs: List = [SMALL_BUFF, MED_SMALL_BUFF, MED_LARGE_BUFF, LARGE_BUFF]
        self.wait()
        for buff in buffs:
            self.play(circle.animate.next_to(square, RIGHT, buff))
        self.wait()
