from commons import *


class SimpleHarmonicOscilatorBase(Base):
    def construct(self):
        with self.new_section("Base Scene Setup"): 
            axes = Axes(
                x_range=[0,10],
                x_length=5,
                y_range=[0,10],
                y_length=5,
                
            ).add_coordinates()
            self.add(axes)
            pass


class SimpleHarmonicOscilator(SimpleHarmonicOscilatorBase):
    def construct(self):
        pass


def main():
    config = {
        "preview": True if VIDEO else False,
        "quality": "low_quality",
        "save_last_frame": True if not VIDEO else False,
        # "disable_caching": True,
    }
    with tempconfig(config):
        scene = SimpleHarmonicOscilator()
        scene.render()


if __name__ == "__main__":
    main()
