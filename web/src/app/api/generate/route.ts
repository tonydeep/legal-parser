import { NextResponse } from "next/server"
import { parseDocument, generateURN, generateCypher, countComponents } from "@/lib/parser"

export async function POST(req: Request) {
  try {
    const { text, type = "cypher" } = await req.json()

    if (!text || typeof text !== "string") {
      return NextResponse.json(
        { error: "Text content is required" },
        { status: 400 }
      )
    }

    const parsed = parseDocument(text)

    // Generate URN
    const urn = generateURN(
      parsed.metadata.loaiVanBan,
      parsed.metadata.coQuanBanHanh || "quochoi",
      parsed.metadata.ngayBanHanh || new Date().toISOString().split("T")[0],
      parsed.metadata.soHieu || "000"
    )

    if (type === "urn") {
      return NextResponse.json({
        success: true,
        urn,
        workId: `${parsed.metadata.loaiVanBan}-${parsed.metadata.ngayBanHanh?.split("-")[0] || "0000"}`,
      })
    }

    // Generate Cypher
    const cypher = generateCypher(parsed, urn)
    const componentCount = countComponents(parsed.structure)

    return NextResponse.json({
      success: true,
      cypher,
      urn,
      stats: {
        documentType: parsed.metadata.loaiVanBan,
        componentCount,
        crossReferences: parsed.crossReferences.length,
      },
    })
  } catch (error) {
    console.error("Generate error:", error)
    return NextResponse.json(
      { error: "Failed to generate output" },
      { status: 500 }
    )
  }
}
