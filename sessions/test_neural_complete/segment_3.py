from manim import *

class EducationalScene(Scene):
    def construct(self):
        # PHASE 1: Title and Setup (0-5s)
        title = Text("Going Deep: How Neural Networks Learn Complexity", font_size=32, color=WHITE)
        title.to_edge(UP)
        self.play(Write(title), run_time=2)
        self.wait(1)

        intro_text = Text("To tackle complex problems, networks go 'deep'.", font_size=26)
        intro_text.move_to(ORIGIN)
        self.play(Write(intro_text), run_time=2)

        # PHASE 2: Deep Network Visualization (5-15s)
        self.play(FadeOut(intro_text), run_time=1)
        self.wait(0.5)

        # Create network layers
        input_layer = VGroup(*[Circle(radius=0.2, color=BLUE_B, fill_opacity=0.8) for _ in range(4)]).arrange(DOWN, buff=0.8)
        hidden_layer_1 = VGroup(*[Circle(radius=0.2, color=GREEN_B, fill_opacity=0.8) for _ in range(5)]).arrange(DOWN, buff=0.8)
        hidden_layer_2 = VGroup(*[Circle(radius=0.2, color=GREEN_B, fill_opacity=0.8) for _ in range(5)]).arrange(DOWN, buff=0.8)
        output_layer = VGroup(*[Circle(radius=0.2, color=RED_B, fill_opacity=0.8) for _ in range(3)]).arrange(DOWN, buff=0.8)
        
        layers = VGroup(input_layer, hidden_layer_1, hidden_layer_2, output_layer).arrange(RIGHT, buff=2)
        layers.move_to(ORIGIN)

        # Create connections
        connections = VGroup()
        for i in range(len(layers) - 1):
            for start_node in layers[i]:
                for end_node in layers[i+1]:
                    connections.add(Line(start_node.get_center(), end_node.get_center(), stroke_width=1, color=GRAY))
        
        self.play(Create(connections), Create(layers), run_time=2)

        deep_text = Text("Deep learning uses many hidden layers to learn patterns within patterns.", font_size=26)
        deep_text.next_to(layers, DOWN, buff=0.8)
        self.play(Write(deep_text), run_time=3)
        self.wait(5)

        # PHASE 3: Node Zoom & Activation Function (15-25s)
        target_node = hidden_layer_1[2]
        other_elements = VGroup(connections, input_layer, hidden_layer_2, output_layer, deep_text)
        other_nodes = VGroup(hidden_layer_1[0], hidden_layer_1[1], hidden_layer_1[3], hidden_layer_1[4])
        self.play(FadeOut(other_elements), FadeOut(other_nodes), run_time=2)
        
        zoomed_node = Circle(radius=1.2, color=GREEN_C, fill_opacity=0.4)
        zoomed_node.move_to(ORIGIN)
        self.play(Transform(target_node, zoomed_node), run_time=2)
        self.wait(0.5)

        # Create activation function viz
        axis_h = Line(LEFT, RIGHT, color=WHITE, stroke_width=2).scale(1.1)
        axis_v = Line(DOWN, UP, color=WHITE, stroke_width=2).scale(1.1)
        axes = VGroup(axis_h, axis_v).move_to(target_node.get_center())
        
        step_1 = Line(axis_h.get_start(), ORIGIN, color=YELLOW, stroke_width=4)
        step_2 = Line(ORIGIN, axis_h.get_end() + UP, color=YELLOW, stroke_width=4)
        activation_curve = VGroup(step_1, step_2).move_to(target_node.get_center())

        self.play(Create(axes), run_time=1.5)
        self.play(Create(activation_curve), run_time=1)
        
        activation_text = Text("Each node has an 'activation function' that acts like a switch.", font_size=26)
        activation_text.next_to(target_node, DOWN, buff=0.8)
        self.play(Write(activation_text), run_time=3)

        # PHASE 4: Non-linearity Explained (25-35s)
        self.play(FadeOut(target_node), FadeOut(axes), FadeOut(activation_curve), FadeOut(activation_text), run_time=2)
        self.wait(1)

        nonlinearity_text = Text("This introduces non-linearity, allowing the network to model complex data.", font_size=26)
        nonlinearity_text.to_edge(UP).shift(DOWN*1.5)
        self.play(Write(nonlinearity_text), run_time=2)

        # Linear vs Non-linear viz
        linear_line = Line(LEFT*5 + DOWN*1, LEFT*2 + DOWN*1, color=BLUE_A, stroke_width=4)
        linear_label = Text("Linear", font_size=24).next_to(linear_line, DOWN, buff=0.6)
        
        nonlinear_path = VGroup(
            Line(RIGHT*2 + DOWN*1.5, RIGHT*2.5 + DOWN*0.5),
            Line(RIGHT*2.5 + DOWN*0.5, RIGHT*3.5 + DOWN*2),
            Line(RIGHT*3.5 + DOWN*2, RIGHT*4.5 + DOWN*1),
            Line(RIGHT*4.5 + DOWN*1, RIGHT*5 + DOWN*1.5)
        ).set_color(ORANGE).set_stroke(width=4)
        nonlinear_label = Text("Complex", font_size=24).next_to(nonlinear_path, DOWN, buff=0.6)

        self.play(Create(linear_line), Write(linear_label), run_time=1.5)
        self.play(Create(nonlinear_path), Write(nonlinear_label), run_time=1.5)
        self.wait(2)

        # PHASE 5: Conclusion (35-45s)
        self.play(
            FadeOut(nonlinearity_text),
            FadeOut(linear_line),
            FadeOut(linear_label),
            FadeOut(nonlinear_path),
            FadeOut(nonlinear_label),
            FadeOut(title),
            run_time=2
        )

        summary_text = Text("Deep Networks + Non-linearity = Powerful Problem Solving", font_size=28)
        summary_text.move_to(ORIGIN)
        self.play(FadeIn(summary_text), run_time=2)
        self.wait(3)

        self.play(FadeOut(summary_text), run_time=2)
        
        # Final wait as required
        self.wait(2)