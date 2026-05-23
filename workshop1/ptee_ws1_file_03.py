from manim import *

# basic shapes
class Transformations(Scene):
    def construct(self):
        circle = Circle()  # create a circle
        square = Square()  # create a square
        triangle = Triangle()  # create a triangle

        # set colors
        circle.set_fill(PINK, opacity=0.5)  # set the fill color and opacity
        square.set_fill(BLUE, opacity=0.5)
        triangle.set_fill(GREEN, opacity=0.5)

        self.play(Create(circle))  # animate the creation of the circle
        self.wait(2)  # wait for 2 seconds before ending the scene

        self.play(Transform(circle, square))  # animate the transformation of the circle into a square
        self.wait(2)  # wait for 2 seconds before ending the scene

        # now our circle variable actually refers to the square, so we can transform it again

        self.play(ReplacementTransform(circle, triangle))  # animate the transformation of the square into a triangle
        self.wait(2)  # wait for 2 seconds before ending the scene

        # but now the circle variable is no longer part of the scene
        # instead triangle has entered the scene

        self.play(triangle.animate.set_fill(RED, opacity=0.5))  # animate changing the triangle's fill color to red
        self.wait(2)  # wait for 2 seconds before ending the scene