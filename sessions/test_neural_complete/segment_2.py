from manim import *

class EducationalScene(Scene):
    def construct(self):
        # PHASE 1: Title and Setup
        title = Text("Learning from Mistakes: Backpropagation & Gradient Descent", font_size=32, color=WHITE)
        title.to_edge(UP)
        self.play(Write(title), run_time=2)
        self.wait(1)

        # Create Network Structure
        input_node = Circle(radius=0.3, color=BLUE, fill_opacity=0.6).move_to(LEFT * 4.5)
        hidden_nodes = VGroup(
            Circle(radius=0.3, color=BLUE, fill_opacity=0.6),
            Circle(radius=0.3, color=BLUE, fill_opacity=0.6),
            Circle(radius=0.3, color=BLUE, fill_opacity=0.6)
        ).arrange(DOWN, buff=1.0).move_to(ORIGIN)
        output_node = Circle(radius=0.3, color=BLUE, fill_opacity=0.6).move_to(RIGHT * 4.5)
        
        connections_in = VGroup(*[Line(input_node.get_center(), h.get_center(), color=GRAY) for h in hidden_nodes])
        connections_out = VGroup(*[Line(h.get_center(), output_node.get_center(), color=GRAY) for h in hidden_nodes])
        
        weights_in = VGroup(*[Text("w", font_size=24, color=WHITE).move_to(c.get_center()) for c in connections_in])
        weights_out = VGroup(*[Text("w", font_size=24, color=WHITE).move_to(c.get_center()) for c in connections_out])

        network = VGroup(input_node, hidden_nodes, output_node, connections_in, connections_out, weights_in, weights_out)
        self.play(Create(network), run_time=2)

        # PHASE 2: Forward Propagation
        cat_input_label = Text("Cat", font_size=28).next_to(input_node, LEFT, buff=0.8)
        self.play(FadeIn(cat_input_label), run_time=1)

        forward_arrows_1 = VGroup(*[Arrow(input_node.get_center(), h.get_center(), color=YELLOW, buff=0.3) for h in hidden_nodes])
        self.play(Create(forward_arrows_1), run_time=1.5)
        
        forward_arrows_2 = VGroup(*[Arrow(h.get_center(), output_node.get_center(), color=YELLOW, buff=0.3) for h in hidden_nodes])
        self.play(Create(forward_arrows_2), run_time=1.5)

        explanation1 = Text("Weights modify the signal", font_size=28).next_to(network, DOWN, buff=1.0)
        self.play(Write(explanation1), run_time=2)

        prediction_text = Text("Dog?", font_size=28, color=RED).next_to(output_node, RIGHT, buff=0.8)
        self.play(Write(prediction_text), run_time=1.5)
        self.wait(0.5)

        self.play(
            FadeOut(forward_arrows_1), FadeOut(forward_arrows_2),
            FadeOut(cat_input_label), FadeOut(explanation1),
            run_time=2
        )

        # PHASE 3: Backpropagation
        explanation2 = Text("Error signal travels backward", font_size=28).next_to(network, DOWN, buff=1.0)
        self.play(Write(explanation2), run_time=2)

        backward_arrows_1 = VGroup(*[Arrow(output_node.get_center(), h.get_center(), color=RED, buff=0.3) for h in hidden_nodes])
        self.play(Create(backward_arrows_1), run_time=2)
        self.play(weights_out.animate.set_color(ORANGE))

        backward_arrows_2 = VGroup(*[Arrow(h.get_center(), input_node.get_center(), color=RED, buff=0.3) for h in hidden_nodes])
        self.play(Create(backward_arrows_2), run_time=2)
        self.play(weights_in.animate.set_color(ORANGE))
        self.wait(1)

        self.play(
            FadeOut(network), FadeOut(prediction_text),
            FadeOut(explanation2), FadeOut(backward_arrows_1), FadeOut(backward_arrows_2),
            run_time=2
        )
        
        # PHASE 4: Gradient Descent
        explanation3 = Text("Gradient Descent adjusts weights", font_size=28).to_edge(DOWN)
        
        hill_left = Line(LEFT * 3 + UP * 1.5, ORIGIN + DOWN * 1.5, color=BLUE_C, stroke_width=6)
        hill_right = Line(ORIGIN + DOWN * 1.5, RIGHT * 3 + UP * 1.5, color=BLUE_C, stroke_width=6)
        hill = VGroup(hill_left, hill_right)
        
        self.play(Create(hill), Write(explanation3), run_time=3)

        ball = Circle(radius=0.2, color=YELLOW, fill_opacity=1).move_to(hill_left.get_start())
        self.play(FadeIn(ball), run_time=1)
        self.play(ball.animate.move_to(hill_left.get_end()), run_time=3)

        explanation4 = Text("Finding the lowest error", font_size=28).to_edge(DOWN)
        self.play(Transform(explanation3, explanation4), run_time=2)
        self.wait(1)

        # PHASE 5: Summary and Conclusion
        self.play(
            FadeOut(hill), FadeOut(ball), FadeOut(explanation3),
            run_time=2
        )

        summary_text = Text("This is how the network learns from its mistakes.", font_size=28)
        self.play(Write(summary_text), run_time=2.5)
        self.wait(1.5)

        self.play(FadeOut(summary_text), FadeOut(title), run_time=2)
        
        self.wait(2)