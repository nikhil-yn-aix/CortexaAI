from manim import *

class EducationalScene(Scene):
    def construct(self):
        # PHASE 1 & 2: SETUP AND TITLE
        title = Text("The Data Assembly Line: Inside a Neural Network Layer", font_size=32, color=WHITE)
        title.to_edge(UP)
        self.play(Write(title), run_time=2)
        self.wait(1)

        # Create Layer Function to avoid code repetition
        def create_layer(position):
            layer_rect = Rectangle(width=2.5, height=4, color=GRAY, fill_opacity=0.2)
            nodes = VGroup(
                Circle(radius=0.3, color=WHITE, fill_opacity=1),
                Circle(radius=0.3, color=WHITE, fill_opacity=1),
                Circle(radius=0.3, color=WHITE, fill_opacity=1)
            ).arrange(DOWN, buff=0.8)
            layer_group = VGroup(layer_rect, nodes).move_to(position)
            return layer_group

        # Create Layers
        layer1_group = create_layer(LEFT * 3)
        layer1_label = Text("Input Layer", font_size=28).next_to(layer1_group, DOWN, buff=0.8)
        self.play(Create(layer1_group), Write(layer1_label), run_time=2)

        # PHASE 2: DATA ENTRY
        data_orb = Circle(radius=0.25, color=BLUE, fill_opacity=1).move_to(LEFT * 6)
        self.play(Create(data_orb), run_time=2)

        # Animate data to first layer
        central_node_l1 = layer1_group[1][1] # Middle node of the first layer
        self.play(data_orb.animate.move_to(central_node_l1.get_center()), run_time=3)
        
        transform_label = Text("Transformation", font_size=28).next_to(layer1_group, DOWN, buff=0.8)
        self.play(FadeOut(layer1_label), FadeIn(transform_label), run_time=2)
        self.wait(3)

        # PHASE 2: TRANSFORMATION
        # Weight (color change) and Bias (flash)
        transformed_orb = data_orb.copy().set_color(PURPLE)
        bias_flash = Circle(radius=0.1, color=YELLOW, fill_opacity=1).move_to(central_node_l1.get_center())
        
        self.play(
            Transform(data_orb, transformed_orb),
            FadeIn(bias_flash, run_time=0.5),
            run_time=2
        )
        self.play(FadeOut(bias_flash, run_time=0.5))
        self.wait(0.5)

        self.play(FadeOut(transform_label), run_time=2)

        # PHASE 2: FEEDFORWARD
        # Move to next layer's position
        self.play(data_orb.animate.move_to(ORIGIN), run_time=2)

        layer2_group = create_layer(RIGHT * 3)
        layer2_label = Text("Hidden Layer", font_size=28).next_to(layer2_group, DOWN, buff=0.8)
        self.play(Create(layer2_group), Write(layer2_label), run_time=2)
        self.wait(2)

        # Animate data to second layer
        central_node_l2 = layer2_group[1][1]
        self.play(data_orb.animate.move_to(central_node_l2.get_center()), run_time=3)
        
        # Second transformation
        final_orb = data_orb.copy().set_color(ORANGE)
        bias_flash_2 = Circle(radius=0.1, color=YELLOW, fill_opacity=1).move_to(central_node_l2.get_center())

        self.play(
            Transform(data_orb, final_orb),
            FadeIn(bias_flash_2, run_time=0.5),
            run_time=2
        )
        self.play(FadeOut(bias_flash_2, run_time=0.5))

        # Move data out as final output
        self.play(data_orb.animate.move_to(RIGHT * 6), run_time=2)
        self.play(FadeOut(layer2_label), run_time=1.5)
        
        # PHASE 2: SUMMARY AND CONCLUSION
        self.play(FadeOut(layer1_group), FadeOut(layer2_group), FadeOut(data_orb), run_time=2)
        
        summary_text = Text("Data is processed sequentially through layers", font_size=28).move_to(ORIGIN)
        self.play(Write(summary_text), run_time=3)
        self.wait(3)
        
        # Final fade out
        self.play(FadeOut(summary_text), FadeOut(title), run_time=2)
        self.wait(2)