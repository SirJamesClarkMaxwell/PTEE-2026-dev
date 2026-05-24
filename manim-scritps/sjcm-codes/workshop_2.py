from manim import *


class ForLoopExample(Scene):
    def construct(self):
        # create a row of squares using loops
        length: float = 2.0
        buff = SMALL_BUFF
        group: VGroup = VGroup()
        for i in range(7):
            group.add(Square(length))

        group[0].to_edge(LEFT)

        for i in range(1, len(group)):
            group[i].next_to(group[i - 1], RIGHT, buff)

        self.add(group)


class ForLoopExample2(Scene):
    def construct(self):
        # build several rows of different shapes
        length: float = 1.0
        buff = SMALL_BUFF

        # squares, triangles, circles, and stars arranged in rows
        square_group: VGroup = VGroup(*[Square(length) for _ in range(10)])
        square_group.arrange(RIGHT, buff).to_edge(LEFT).to_edge(UP).set_color(YELLOW)

        triangle_group: VGroup = VGroup(*[Triangle() for _ in range(10)])
        triangle_group.arrange(RIGHT, buff).set_color(RED)
        triangle_group.scale_to_fit_width(square_group.get_width()).next_to(
            square_group, DOWN, SMALL_BUFF
        )

        circle_group: VGroup = VGroup(*[Circle() for _ in range(10)])
        circle_group.arrange(RIGHT, buff).set_color(BLUE)
        circle_group.scale_to_fit_width(triangle_group.get_width()).next_to(
            triangle_group, DOWN, SMALL_BUFF
        )

        star_group: VGroup = VGroup(*[Star(n=5) for _ in range(10)])
        star_group.arrange(RIGHT, buff).set_color(PURPLE)
        star_group.scale_to_fit_width(circle_group.get_width()).next_to(
            circle_group, DOWN, SMALL_BUFF
        )

        self.add(square_group, triangle_group, circle_group, star_group)


class SimpleFunctionExample(Scene):
    def construct(self):
        # generate rows via a helper function
        square: Square = Square(color=YELLOW)
        triangle: Triangle = Triangle(color=RED)
        circle: Circle = Circle(color=BLUE)
        star: Star = Star(n=5, color=PURPLE)

        objects_in_row: int = 10

        square_group: VGroup = self.spawn_vgroup(square, objects_in_row, SMALL_BUFF, 10)
        triangle_group: VGroup = self.spawn_vgroup(
            triangle, objects_in_row, SMALL_BUFF, 10
        )
        circle_group: VGroup = self.spawn_vgroup(circle, objects_in_row, SMALL_BUFF, 10)
        star_group: VGroup = self.spawn_vgroup(star, objects_in_row, SMALL_BUFF, 10)

        general_group: VGroup = VGroup(
            square_group, triangle_group, circle_group, star_group
        )
        general_group.arrange(DOWN, SMALL_BUFF).to_corner(UL, buff=MED_LARGE_BUFF)

        self.add(general_group)

    def spawn_vgroup(
        self, vmobject_to_copy: VMobject, num_objects: int, buff: float, width: float
    ) -> VGroup:
        # duplicate an object and arrange copies in a row
        local_group: VGroup = VGroup(
            *[vmobject_to_copy.copy() for _ in range(num_objects)]
        )
        local_group.arrange(RIGHT, buff).scale_to_fit_width(width)
        return local_group


class Homework1(Scene):
    def construct(self):
        # build a grid of repeated vgroups
        square: Square = Square(color=YELLOW)
        triangle: Triangle = Triangle(color=RED)
        circle: Circle = Circle(color=BLUE)
        star: Star = Star(color=PURPLE)

        objects_in_row: int = 10

        vgroup: VGroup = VGroup(square, triangle, circle, star)
        vgroup.arrange(DOWN).scale_to_fit_height(4.0).to_corner(UL, MED_LARGE_BUFF)

        general_group: VGroup = VGroup(vgroup)
        for _ in range(objects_in_row):
            # general_group.add(vgroup.copy())
            # general_group[-1].next_to(general_group[-2],RIGHT)

            # copy_group = vgroup.copy()
            # copy_group.next_to(general_group[-1],RIGHT)
            # general_group.add(copy_group)

            general_group.add(vgroup.copy().next_to(general_group[-1], RIGHT))

        self.add(general_group)


class Homework2(Scene):
    def construct(self):
        # same layout built with a different grouping approach
        square: Square = Square(color=YELLOW)
        triangle: Triangle = Triangle(color=RED)
        circle: Circle = Circle(color=BLUE)
        star: Star = Star(color=PURPLE)

        objects_in_row: int = 10

        vgroup: VGroup = VGroup(square, triangle, circle, star)
        vgroup.arrange(DOWN).scale_to_fit_height(4.0)

        general_group: VGroup = VGroup(vgroup.copy() for _ in range(objects_in_row))
        general_group.arrange(RIGHT).scale_to_fit_width(10).to_corner(
            UL, MED_LARGE_BUFF
        )

        self.add(general_group)
