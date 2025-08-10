from manim import *

class EducationalScene(Scene):
    def construct(self):
        # Helper function to create the neural network layers
        def create_nn_layers(input_nodes, hidden_nodes, output_nodes):
            input_layer = VGroup(*[Circle(radius=0.25, color=BLUE_B, fill_opacity=0.8) for _ in range(input_nodes)]).arrange(DOWN, buff=0.6)
            hidden_layer = VGroup(*[Circle(radius=0.25, color=GREEN_B, fill_opacity=0.8) for _ in range(hidden_nodes)]).arrange(DOWN, buff=0.4)
            output_layer = VGroup(*[Circle(radius=0.25, color=YELLOW, fill_opacity=0.8) for _ in range(output_nodes)]).arrange(DOWN, buff=0.6)
            
            layers = VGroup(input_layer, hidden_layer, output_layer).arrange(RIGHT, buff=2.5)
            layers.move_to(ORIGIN)
            return layers

        # PHASE 1: Title and Brain Intro (0-5s)
        title = Text("The Digital Brain: What is a Neural Network?", font_size=32, color=WHITE)
        title.to_edge(UP)
        self.play(Write(title), run_time=2)
        self.wait(1)
        
        brain_shape = VGroup(
            Circle(radius=1, color=PINK).move_to(LEFT*0.5),
            Circle(radius=0.8, color=PINK).move_to(RIGHT*0.6 + UP*0.2),
            Circle(radius=0.6, color=PINK).move_to(ORIGIN + DOWN*0.4)
        ).scale(1.2)
        
        self.play(FadeOut(title), Create(brain_shape), run_time=2)

        # PHASE 2: Brain to Network Morph (5-15s)
        network_nodes = VGroup(*[Circle(radius=0.15, color=BLUE_C, fill_opacity=0.8) for _ in range(12)])
        network_nodes.arrange_in_grid(3, 4, buff=0.8).scale(1.5)
        
        self.play(Transform(brain_shape, network_nodes), run_time=3)

        text1 = Text("This is a neural network...", font_size=28).next_to(network_nodes, DOWN, buff=0.8)
        self.play(Write(text1), run_time=2.5)
        
        text2 = Text("a computational model inspired by our brain's structure.", font_size=28).next_to(text1, DOWN, buff=0.5)
        self.play(Write(text2), run_time=3)
        self.wait(1.5)

        # PHASE 3: Forming the Layered Structure (15-25s)
        self.play(FadeOut(brain_shape), FadeOut(text1), FadeOut(text2), run_time=2)
        
        nn = create_nn_layers(3, 5, 2)
        input_layer, hidden_layer, output_layer = nn
        
        self.play(Create(input_layer), Create(hidden_layer), Create(output_layer), run_time=4)

        connections = VGroup()
        for start_node in input_layer:
            for end_node in hidden_layer:
                connections.add(Line(start_node.get_center(), end_node.get_center(), stroke_width=1.5, color=GRAY))
        for start_node in hidden_layer:
            for end_node in output_layer:
                connections.add(Line(start_node.get_center(), end_node.get_center(), stroke_width=1.5, color=GRAY))
        
        self.play(Create(connections), run_time=4)

        # PHASE 4: Identifying the Layers (25-35s)
        input_label = Text("Input Layer", font_size=26).next_to(input_layer, DOWN, buff=0.8)
        hidden_label = Text("Hidden Layers", font_size=26).next_to(hidden_layer, DOWN, buff=0.8)
        output_label = Text("Output Layer", font_size=26).next_to(output_layer, DOWN, buff=0.8)
        
        self.play(Write(input_label), run_time=2)
        self.play(Write(hidden_label), run_time=3)
        self.play(Write(output_label), run_time=3)
        self.wait(2)

        # PHASE 5: Summary and Conclusion (35-45s)
        summary_text = Text("It consists of interconnected nodes organized in layers.", font_size=28)
        summary_text.next_to(nn, UP, buff=0.8)
        self.play(Write(summary_text), run_time=3)
        
        self.wait(1)
        
        all_elements = VGroup(nn, connections, input_label, hidden_label, output_label, summary_text)
        self.play(FadeOut(all_elements), run_time=2)

        self.wait(2)