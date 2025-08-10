from manim import *

class EducationalScene(Scene):
    def construct(self):
        # Title setup
        title = Text("The Transformer's Core: Self-Attention and Rescaling Symmetry", font_size=32, color=WHITE)
        title.to_edge(UP)
        self.play(Write(title), run_time=2)
        self.wait(1)

        # === 1. Input Sentence Setup ===
        words = ["The", "cat", "sat"]
        word_squares = VGroup()
        for word in words:
            square = Square(side_length=1.0, color=BLUE_B, fill_opacity=0.6)
            text = Text(word, font_size=28, color=WHITE)
            word_squares.add(VGroup(square, text))
        
        word_squares.arrange(RIGHT, buff=0.8).move_to(LEFT * 3)
        self.play(FadeIn(word_squares, shift=RIGHT), run_time=2)

        # === 2. Self-Attention Layer Visualization ===
        layer_box = Rectangle(width=7, height=4, color=GRAY).move_to(ORIGIN)
        layer_label = Text("Self-Attention Layer", font_size=28).next_to(layer_box, DOWN, buff=0.4)
        
        self.play(word_squares.animate.move_to(layer_box.get_center() + UP * 1.2), run_time=1)
        self.play(Create(layer_box), Write(layer_label), run_time=2)
        self.wait(0.5)

        lines = VGroup()
        for i in range(len(word_squares)):
            for j in range(len(word_squares)):
                if i != j:
                    line = Line(
                        word_squares[i].get_center(),
                        word_squares[j].get_center(),
                        color=YELLOW,
                        stroke_width=2
                    ).set_z_index(-1)
                    lines.add(line)
        
        self.play(Create(lines), run_time=5)
        self.wait(2)
        self.play(FadeOut(lines), run_time=1)

        # === 3. Internal Parameters & Rescaling ===
        weights = VGroup(*[Square(side_length=0.4, color=RED_C, fill_opacity=0.8) for _ in range(4)]).arrange(RIGHT, buff=0.2)
        biases = VGroup(*[Circle(radius=0.2, color=GREEN_C, fill_opacity=0.8) for _ in range(4)]).arrange(RIGHT, buff=0.2)
        params = VGroup(weights, biases).arrange(DOWN, buff=0.4).next_to(word_squares, DOWN, buff=0.8)
        
        weights_label = Text("Weights", font_size=24).next_to(weights, LEFT, buff=0.4)
        biases_label = Text("Biases", font_size=24).next_to(biases, LEFT, buff=0.4)
        param_labels = VGroup(weights_label, biases_label)

        self.play(FadeIn(params), FadeIn(param_labels), run_time=2)
        self.wait(1)

        output_pos = RIGHT * 4.5
        expected_output = Rectangle(width=1.5, height=1, color=PURPLE, fill_opacity=0.6).move_to(output_pos)
        expected_label = Text("Expected Output", font_size=24).next_to(expected_output, DOWN, buff=0.4)
        self.play(FadeIn(expected_output), Write(expected_label), run_time=1.5)
        
        # Rescaling animation
        scaled_params = params.copy().scale(1.5).set_color(ORANGE)
        self.play(Transform(params, scaled_params), run_time=4)
        self.wait(1)

        # === 4. Invariant Output ===
        actual_output = Rectangle(width=1.5, height=1, color=PURPLE, fill_opacity=0.6).move_to(output_pos)
        self.play(Create(actual_output), run_time=1.5)
        
        result_text = Text("Output is IDENTICAL", font_size=28, color=YELLOW).next_to(actual_output, UP, buff=0.8)
        self.play(Write(result_text), run_time=2)
        self.wait(3)

        # === 5. Cleanup and Summary ===
        all_elements = VGroup(
            title, word_squares, layer_box, layer_label, params, param_labels,
            expected_output, expected_label, actual_output, result_text
        )
        self.play(FadeOut(all_elements), run_time=2)
        
        summary_text = Text(
            "Rescaling Symmetry: Internal parameters can change,\nbut the function remains the same.",
            font_size=28
        ).move_to(ORIGIN)
        self.play(FadeIn(summary_text), run_time=2)
        self.wait(3)
        self.play(FadeOut(summary_text), run_time=1)
        
        # Clean conclusion
        self.wait(2)