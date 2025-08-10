import { NextRequest, NextResponse } from "next/server";
import PptxGenJS from "pptxgenjs";

export async function POST(req: NextRequest) {
  try {
    const { front, back } = await req.json();

    if (!front || !back) {
      return new NextResponse("Missing front or back content", { status: 400 });
    }

    const pptx = new PptxGenJS();

    // Title slide
    const title = pptx.addSlide();
    title.addText("CortexAI Flashcards", { x: 0.5, y: 0.6, fontSize: 28, bold: true, color: "363636" });
    title.addText("Adaptive Learning Deck", { x: 0.5, y: 1.2, fontSize: 16, color: "6b7280" });

    // Front slide
    const frontSlide = pptx.addSlide();
    frontSlide.addText("Front", { x: 0.5, y: 0.5, fontSize: 16, bold: true });
    frontSlide.addText(front, {
      x: 0.5,
      y: 1.0,
      w: 9,
      h: 2,
      fontSize: 22,
      bold: true,
      color: "111111",
    });

    // Back slide
    const backSlide = pptx.addSlide();
    backSlide.addText("Back", { x: 0.5, y: 0.5, fontSize: 16, bold: true });
    backSlide.addText(back, {
      x: 0.5,
      y: 1.0,
      w: 9,
      h: 4,
      fontSize: 18,
      color: "111111",
    });

    const pptxBuffer = await pptx.write("arraybuffer");

    return new NextResponse(pptxBuffer, {
      status: 200,
      headers: {
        "Content-Type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "Content-Disposition": "attachment; filename=cortexai-flashcards.pptx",
      },
    });
  } catch (error) {
    console.error(error);
    return new NextResponse("Internal Server Error", { status: 500 });
  }
}