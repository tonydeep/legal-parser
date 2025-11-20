import { NextResponse } from "next/server"
import { parseDocument, countComponents } from "@/lib/parser"

export async function POST(req: Request) {
  try {
    const { text } = await req.json()

    if (!text || typeof text !== "string") {
      return NextResponse.json(
        { error: "Text content is required" },
        { status: 400 }
      )
    }

    const parsed = parseDocument(text)
    const componentCount = countComponents(parsed.structure)

    return NextResponse.json({
      success: true,
      data: parsed,
      stats: {
        componentCount,
        crossReferences: parsed.crossReferences.length,
        definitionsCount: Object.keys(parsed.definitions).length,
      },
    })
  } catch (error) {
    console.error("Parse error:", error)
    return NextResponse.json(
      { error: "Failed to parse document" },
      { status: 500 }
    )
  }
}
