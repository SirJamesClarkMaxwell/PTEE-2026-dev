from manim import *

# basic shapes
class BasicShapes(Scene):
    def construct(self):
        circle = Circle()  # create a circle
        square = Square()  # create a square
        triangle = Triangle()  # create a triangle

        # set colors
        circle.set_fill(PINK, opacity=0.5)  # set the fill color and opacity
        square.set_fill(BLUE, opacity=0.5)
        triangle.set_fill(GREEN, opacity=0.5)

        # arrange shapes in a row
        shapes = VGroup(circle, square, triangle).arrange(RIGHT, buff=1)

        self.play(Create(shapes))  # animate the creation of the shapes
        self.wait(2)  # wait for 2 seconds before ending the scene

        # other basic shapes include: Ellipse, Rectangle,
        # RoundedRectangle, Annulus, Arc, Sector, Polygon, etc.
