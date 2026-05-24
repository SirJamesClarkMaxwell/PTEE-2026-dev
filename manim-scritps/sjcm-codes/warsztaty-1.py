from manim import *


class FirstScene(Scene):
    def construct(self):
        axes = Axes()
        self.add(axes)

class BoundingBoxExample(Scene):
    def construct(self):
        # create a Triangle object and set its fill color to green
        # with 70% opacity
        triangle = Triangle().set_fill(GREEN,opacity=0.7)

        # create a list of directions used to find boundary points
        directions = [RIGHT,UR,UP,UL,LEFT,DL,DOWN,DR]

        # create a list (group) of dots
        # boundry_points = VGroup(*[Dot(triangle.get_critical_point(direction)).set_color(YELLOW) for direction in directions])
        boundry_points = VGroup()

        # iterate through directions and create dots
        for direction in directions:
            # position -> dot position on screen as a triangle critical point in a chosen direction
            position = triangle.get_critical_point(direction)

            # create a dot for the given direction and set it to yellow
            dot = Dot(position).set_color(YELLOW)

            # add the dot to the dot group
            boundry_points.add(dot)


        text_directions = "RIGHT,UR,UP,UL,LEFT,DL,DOWN,DR".split(",")
        #boundry_text = VGroup(*[Text(text).to_edge(UP,buff=SMALL_BUFF) for text in text_directions])

        # create a list of text labels
        boundry_text = VGroup()
        for text in text_directions:
            # create a text object
            text_obj = Text(text)

            # move it to the top of the screen
            text_obj.to_edge(UP,buff = SMALL_BUFF)

            # add the text to the group
            boundry_text.add(text_obj)

        dot = Dot().set_color(YELLOW)

        self.play(FadeIn(triangle),FadeIn(dot))

        for point, (i,text) in zip(boundry_points,enumerate(boundry_text)):
            # create an empty list of animations executed in one loop iteration
            animations = []
            if i == 0:
                fade_in_animation = FadeIn(text)
                animations.append(fade_in_animation)
            else: 
                fade_transform_animation = FadeTransform(boundry_text[i-1],text)
                animations.append(fade_transform_animation)

            point_animation = dot.animate.move_to(point)
            animations.append(point_animation)

            self.play(*animations,run_time = 2)
        self.wait()



class PointsExample(Scene):
    def construct(self):
        triangle = Triangle().set_fill(GREEN,opacity=0.7)
        boundry_points = [ pos for pos in triangle.get_vertices()]
        dot = Dot(boundry_points[0]).set_color(YELLOW)

        self.play(FadeIn(triangle),FadeIn(dot))

        for i,point in enumerate(boundry_points):
            animations = []
            if i == 0:
                continue
            point_animation = dot.animate.move_to(point)
            animations.append(point_animation)

            self.play(*animations,run_time = 2)
        self.wait()
