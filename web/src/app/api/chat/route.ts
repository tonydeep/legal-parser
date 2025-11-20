import { streamText } from "ai"
import { openrouter, AI_MODELS, LEGAL_ANALYSIS_PROMPT } from "@/lib/ai"

export async function POST(req: Request) {
  const { messages, model = "gpt-4o" } = await req.json()

  const modelId = AI_MODELS[model as keyof typeof AI_MODELS] || AI_MODELS["gpt-4o"]

  const result = streamText({
    model: openrouter(modelId),
    system: LEGAL_ANALYSIS_PROMPT,
    messages,
  })

  return result.toTextStreamResponse()
}
