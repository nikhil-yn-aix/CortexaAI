from manim import *

class EducationalScene(Scene):
    def construct(self):
        # Set a black background
        self.camera.background_color = BLACK

        # PHASE 1: Title
        title = Text("Transformers Unveiled: From Black Box to Blueprint", font_size=32, color=WHITE)
        title.to_edge(UP)
        self.play(Write(title), run_time=2)
        self.wait(1)
        self.play(FadeOut(title), run_time=1)

        # CONCEPT 1: Black Box Revelation
        black_box = Rectangle(width=5, height=3, color=GRAY, fill_color=BLACK, fill_opacity=1)
        text1_part1 = Text("The 'black box' becomes transparent...", font_size=28).next_to(black_box, DOWN, buff=0.8)

        self.play(Create(black_box), run_time=1)
        self.play(Write(text1_part1), run_time=2.5)
        self.wait(0.5)

        # Create symmetrical data flow inside the box
        data_flow_left = VGroup(*[
            Arrow(LEFT*1.5 + UP*0.5, ORIGIN + UP*0.5, buff=0.1, color=BLUE_A),
            Circle(radius=0.1, color=BLUE_C, fill_opacity=0.8).move_to(LEFT*2 + UP*0.5)
        ]).shift(LEFT*0.5)
        data_flow_right = VGroup(*[
            Arrow(RIGHT*1.5 + UP*0.5, ORIGIN + UP*0.5, buff=0.1, color=GREEN_A),
            Circle(radius=0.1, color=GREEN_C, fill_opacity=0.8).move_to(RIGHT*2 + UP*0.5)
        ]).shift(RIGHT*0.5)
        
        transparent_box = black_box.copy().set_fill(opacity=0).set_stroke(color=BLUE, width=3)
        text1_part2 = Text("...revealing an elegant, symmetrical flow.", font_size=28).next_to(black_box, DOWN, buff=0.8)

        self.play(
            Transform(black_box, transparent_box),
            FadeIn(data_flow_left, data_flow_right),
            run_time=3
        )
        self.play(Transform(text1_part1, text1_part2), run_time=2.5)
        self.wait(0.5)

        # Clear screen for next concept
        self.play(
            FadeOut(black_box),
            FadeOut(data_flow_left),
            FadeOut(data_flow_right),
            FadeOut(text1_part1),
            run_time=2
        )

        # CONCEPT 2: The Symmetry Bridge
        ml_label = Text("Machine Learning", font_size=28).to_edge(LEFT, buff=1.5)
        physics_label = Text("Physics", font_size=28).to_edge(RIGHT, buff=1.5)

        self.play(FadeIn(ml_label), FadeIn(physics_label), run_time=2)

        symmetry_box = Rectangle(width=2.5, height=1, color=YELLOW, fill_color=YELLOW, fill_opacity=0.2)
        symmetry_text = Text("Symmetry", font_size=28).move_to(symmetry_box.get_center())
        symmetry_element = VGroup(symmetry_box, symmetry_text)
        
        line_left = Line(ml_label.get_right(), symmetry_box.get_left(), color=GRAY, buff=0.2)
        line_right = Line(physics_label.get_left(), symmetry_box.get_right(), color=GRAY, buff=0.2)
        
        bridge_text = Text("This knowledge bridges machine learning and physics...", font_size=28).to_edge(DOWN, buff=1)

        self.play(
            Create(line_left),
            Create(line_right),
            Create(symmetry_element),
            run_time=2.5
        )
        self.play(Write(bridge_text), run_time=3)
        self.wait(1.5)

        # Clear screen for next concept
        self.play(
            FadeOut(ml_label), FadeOut(physics_label),
            FadeOut(symmetry_element), FadeOut(line_left), FadeOut(line_right),
            FadeOut(bridge_text),
            run_time=1
        )

        # CONCEPT 3: Architectural Evolution
        simple_arch = VGroup(
            Square(side_length=0.8, color=RED_B),
            Square(side_length=0.8, color=RED_B),
            Square(side_length=0.8, color=RED_B)
        ).arrange(RIGHT, buff=0.2).move_to(ORIGIN)

        arch_text = Text("...leading to novel and more powerful AI architectures.", font_size=28).to_edge(DOWN, buff=1)

        self.play(Create(simple_arch), run_time=2)
        self.play(Write(arch_text), run_time=3)
        
        complex_arch = VGroup(
            VGroup(*[Square(side_length=0.8, color=PURPLE_B) for _ in range(3)]).arrange(DOWN, buff=0.2),
            VGroup(*[Square(side_length=0.8, color=PURPLE_B) for _ in range(3)]).arrange(DOWN, buff=0.2)
        ).arrange(RIGHT, buff=1.0).move_to(ORIGIN)

        self.play(Transform(simple_arch, complex_arch), run_time=3)
        self.wait(2)

        # Final Summary
        summary_text = Text("Unlocking New Possibilities", font_size=28, color=YELLOW).to_edge(DOWN, buff=1)
        self.play(Transform(arch_text, summary_text), run_time=2)

        # Clean conclusion
        self.wait(2)