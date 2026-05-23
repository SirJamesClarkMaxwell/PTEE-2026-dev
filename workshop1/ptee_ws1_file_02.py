from manim import *

# the Manim world
class Placements(Scene):
    def construct(self):

        plane = NumberPlane(  # create a number plane
        ).add_coordinates()  # add coordinate labels
        self.add(plane)  # add the number plane to the scene

        circle = Circle()  # create a circle
        circle.set_fill(PINK, opacity=0.5)  # set the fill color and opacity

        # new objects are always created at the scene's origin (0, 0, 0)
        self.play(Create(circle))  # animate the creation of the circle
        self.wait(2)  # wait for 2 seconds before ending the scene

        self.play(circle.animate.shift(LEFT * 2))  # animate the circle moving left
        self.wait(2)  # wait for 2 seconds before ending the scene

        self.play(circle.animate.shift([0,2,0]))  # animate the circle moving up
        self.wait(2)  # wait for 2 seconds before ending the scene

        self.play(circle.animate.move_to([-4,-2,0]))  # animate the circle moving to a specific point
        self.wait(2)  # wait for 2 seconds before ending the scene

        self.play(circle.animate.to_corner(UR, buff=0))  # animate the circle moving to the upper right corner
        self.wait(2)  # wait for 2 seconds before ending the scene

        # other possibilities include: to_edge()
        # directions include: UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR
