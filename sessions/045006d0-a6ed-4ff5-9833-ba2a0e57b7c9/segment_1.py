from manim import *

class EducationalScene(Scene):
    def construct(self):
        # Configuration
        self.camera.background_color = BLACK

        # PHASE 1: Title setup
        title = Text("Unboxing the Transformer: From Black Box to Building Blocks", font_size=32, color=WHITE)
        title.to_edge(UP)
        self.play(Write(title), run_time=2)
        self.wait(1)

        # Black Box Setup
        black_box = Rectangle(width=4, height=2.5, color=BLUE_C, fill_opacity=1)
        box_label = Text("Neural Network", font_size=24, color=WHITE).next_to(black_box, UP, buff=0.3)
        box_group = VGroup(black_box, box_label)
        self.play(Create(black_box), Write(box_label), run_time=2)

        # PHASE 2: Inputs and Outputs
        # Inputs
        input_text = Text("Hello", font_size=28).move_to(LEFT * 5 + UP * 0.5)
        input_shape = Square(side_length=0.8, color=GREEN, fill_opacity=0.6).move_to(LEFT * 5 + DOWN * 0.5)
        inputs = VGroup(input_text, input_shape)
        
        # Outputs
        output_text = Text("Bonjour", font_size=28).move_to(RIGHT * 5 + UP * 0.5)
        output_shape = Circle(radius=0.4, color=ORANGE, fill_opacity=0.6).move_to(RIGHT * 5 + DOWN * 0.5)
        outputs = VGroup(output_text, output_shape)

        # Animation of flow
        self.play(FadeIn(inputs, shift=LEFT*0.5), run_time=2)
        
        arrow_in = Arrow(start=LEFT * 5, end=black_box.get_left(), color=YELLOW, buff=0.2)
        self.play(Create(arrow_in), inputs.animate.next_to(arrow_in, LEFT, buff=0.2), run_time=2)
        self.play(inputs.animate.move_to(black_box.get_center()), run_time=2)
        
        arrow_out = Arrow(start=black_box.get_right(), end=RIGHT * 5, color=YELLOW, buff=0.2)
        self.play(FadeIn(outputs, shift=RIGHT*0.5), Create(arrow_out), run_time=2)
        
        # Cleanup
        self.play(FadeOut(inputs), FadeOut(outputs), FadeOut(arrow_in), FadeOut(arrow_out), run_time=1.5)

        # PHASE 3: Peeking Inside
        self.play(FadeOut(box_label), run_time=1)
        explanation1 = Text("While powerful, models are often 'black boxes'.", font_size=28).to_edge(DOWN, buff=1)
        self.play(Write(explanation1), run_time=3)

        transparent_box = Rectangle(width=4, height=2.5, color=BLUE_A, fill_opacity=0.2, stroke_color=BLUE_C)
        internal_lines = VGroup(
            Line(DL, UR, color=YELLOW, stroke_width=2),
            Line(UL, DR, color=YELLOW, stroke_width=2)
        ).scale(0.8).move_to(black_box.get_center())
        
        messy_box = VGroup(transparent_box, internal_lines)
        self.play(Transform(black_box, messy_box), run_time=2)
        self.wait(2)
        self.play(FadeOut(explanation1), run_time=1)

        # PHASE 4: Building Blocks
        explanation2 = Text("Let's see how they're built from layers.", font_size=28).to_edge(DOWN, buff=1)
        self.play(Write(explanation2), run_time=2)

        # Create the target layers
        num_layers = 5
        layers = VGroup(*[
            Rectangle(width=3, height=0.4, color=GREEN_B, fill_opacity=0.6, stroke_width=2)
            for _ in range(num_layers)
        ]).arrange(DOWN, buff=0.1).move_to(ORIGIN)
        
        self.play(Transform(black_box, layers), run_time=4)
        
        layers_label = Text("Layers", font_size=24, color=YELLOW).next_to(layers, RIGHT, buff=0.5)
        self.play(Write(layers_label), run_time=2)
        self.wait(2)

        # PHASE 5: Conclusion
        self.play(FadeOut(black_box), FadeOut(layers_label), run_time=1)
        self.play(FadeOut(explanation2), run_time=1)

        summary_text = Text("Understanding the basic structure is the first step.", font_size=28)
        self.play(Write(summary_text), run_time=3)
        self.wait(1)
        self.play(FadeOut(summary_text, title), run_time=1)
        
        # Final wait as per requirement
        self.wait(2)