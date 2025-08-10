from manim import *

class EducationalScene(Scene):
    def construct(self):
        # PHASE 1: Title and Introduction
        title = Text("AI's Specialist Tools: CNNs and RNNs", font_size=32, color=WHITE)
        title.to_edge(UP)
        intro_text = Text("Different network architectures are built for specific tasks.", font_size=28, color=WHITE)
        intro_text.next_to(title, DOWN, buff=0.8)

        self.play(Write(title), run_time=2)
        self.wait(1)
        self.play(Write(intro_text), run_time=2)
        self.wait(2)

        self.play(FadeOut(title), FadeOut(intro_text), run_time=1)
        self.wait(0.5)

        # PHASE 2: Convolutional Neural Network (CNN)
        cnn_title = Text("Convolutional Neural Network (CNN)", font_size=28).to_edge(UP)
        cnn_explainer = Text("CNNs scan images with filters for recognition.", font_size=26).to_edge(DOWN)
        
        # Create image grid
        image_grid = VGroup(*[
            VGroup(*[Square(side_length=0.6, color=BLUE_B, fill_opacity=0.5) for _ in range(4)])
            .arrange(RIGHT, buff=0.1) for _ in range(4)
        ]).arrange(DOWN, buff=0.1).move_to(LEFT * 2.5)

        # Create filter
        filter_scan = Square(side_length=1.3, color=YELLOW, fill_opacity=0.4)
        filter_scan.move_to(image_grid[0][0].get_center() + DL*0.05)

        self.play(Write(cnn_title), run_time=1.5)
        self.play(Create(image_grid), run_time=1.5)
        self.wait(1)

        # Animate filter scanning
        self.play(Create(filter_scan))
        self.play(filter_scan.animate.shift(RIGHT * 0.7 * 2), run_time=1.5)
        self.play(filter_scan.animate.shift(DOWN * 0.7), run_time=1)
        self.wait(0.5)

        # Show feature detection
        feature_output = Circle(radius=0.4, color=GREEN_A, fill_opacity=0.6).move_to(RIGHT * 2.5)
        arrow_to_feature = Arrow(image_grid.get_right(), feature_output.get_left(), color=WHITE, buff=0.2)
        
        self.play(Create(arrow_to_feature), Create(feature_output), run_time=1.5)
        self.play(Write(cnn_explainer), run_time=1.5)
        self.wait(2)

        cnn_group = VGroup(cnn_title, image_grid, filter_scan, arrow_to_feature, feature_output, cnn_explainer)
        self.play(FadeOut(cnn_group), run_time=1)
        self.wait(0.5)

        # PHASE 3: Recurrent Neural Network (RNN)
        rnn_title = Text("Recurrent Neural Network (RNN)", font_size=28).to_edge(UP)
        rnn_explainer = Text("RNNs process sequences with memory for translation.", font_size=26).to_edge(DOWN)
        
        # Create RNN cell and memory loop
        rnn_cell = Circle(radius=0.7, color=PURPLE, fill_opacity=0.6).move_to(ORIGIN)
        memory_loop = Arrow(
            start=rnn_cell.get_bottom() + LEFT*0.3, 
            end=rnn_cell.get_left() + DOWN*0.3, 
            color=YELLOW, 
            buff=0.1
        ).scale(0.8)

        self.play(Write(rnn_title), run_time=1.5)
        self.play(Create(rnn_cell), Create(memory_loop), run_time=1.5)

        # Input sentence
        words_in = VGroup(Text("The"), Text("cat"), Text("sat")).arrange(DOWN, buff=0.8).move_to(LEFT * 4)
        self.play(FadeIn(words_in, shift=RIGHT), run_time=1.5)
        self.wait(1)

        # Animate processing
        for word in words_in:
            arrow_proc = Arrow(word.get_right(), rnn_cell.get_left(), buff=0.2, color=WHITE)
            self.play(Create(arrow_proc), run_time=0.5)
            self.play(FadeOut(arrow_proc), run_time=0.5)
        
        # Output translation
        words_out = Text("Le chat...", font_size=28).move_to(RIGHT * 4)
        arrow_to_out = Arrow(rnn_cell.get_right(), words_out.get_left(), buff=0.2, color=WHITE)
        self.play(Create(arrow_to_out), Write(words_out), run_time=1.5)
        self.play(Write(rnn_explainer), run_time=1.5)
        self.wait(2)

        rnn_group = VGroup(rnn_title, rnn_cell, memory_loop, words_in, words_out, arrow_to_out, rnn_explainer)
        self.play(FadeOut(rnn_group), run_time=1)
        self.wait(0.5)

        # PHASE 4: Conclusion
        conclusion_text = Text(
            "These specialized designs are the engines\nbehind modern AI applications.",
            font_size=28,
            color=WHITE
        )
        conclusion_text.move_to(ORIGIN)
        
        self.play(Write(conclusion_text), run_time=3)
        self.wait(3)

        self.play(FadeOut(conclusion_text), run_time=1)
        self.wait(2)