import { createOpenAI } from "@ai-sdk/openai"

// OpenRouter provides access to 100+ AI models via OpenAI-compatible API
export const openrouter = createOpenAI({
  baseURL: "https://openrouter.ai/api/v1",
  apiKey: process.env.OPENROUTER_API_KEY,
})

// Available models through OpenRouter
export const AI_MODELS = {
  // High performance
  "gpt-4-turbo": "openai/gpt-4-turbo",
  "claude-3-opus": "anthropic/claude-3-opus",
  "claude-3-sonnet": "anthropic/claude-3-sonnet",

  // Balanced
  "gpt-4o": "openai/gpt-4o",
  "claude-3-haiku": "anthropic/claude-3-haiku",
  "gemini-pro": "google/gemini-pro",

  // Fast & economical
  "gpt-3.5-turbo": "openai/gpt-3.5-turbo",
  "mixtral-8x7b": "mistralai/mixtral-8x7b-instruct",
  "llama-3-70b": "meta-llama/llama-3-70b-instruct",

  // Vietnamese optimized
  "qwen-72b": "qwen/qwen-72b-chat",
} as const

export type AIModelKey = keyof typeof AI_MODELS

// System prompt for legal document analysis
export const LEGAL_ANALYSIS_PROMPT = `You are an expert Vietnamese legal document analyst. Your role is to:

1. Analyze Vietnamese legal documents (Luật, Nghị định, Thông tư, etc.)
2. Extract key information: document type, number, date, issuing authority
3. Identify the hierarchical structure (Phần, Chương, Mục, Điều, Khoản, Điểm, Tiểu mục)
4. Explain legal concepts in clear, accessible language
5. Identify cross-references and relationships between documents
6. Answer questions about Vietnamese legal framework

Always respond in the same language as the user's query (Vietnamese or English).
Be precise with legal terminology and cite specific articles when relevant.`
