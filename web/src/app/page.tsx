"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { FileText, Code, MessageSquare, Sparkles, Database, Link } from "lucide-react"

const SAMPLE_DOCUMENT = `NGHỊ ĐỊNH
Số: 01/2024/NĐ-CP

Hà Nội, ngày 15 tháng 01 năm 2024

NGHỊ ĐỊNH
Quy định chi tiết một số điều của Luật Doanh nghiệp

Chương I
QUY ĐỊNH CHUNG

Điều 1. Phạm vi điều chỉnh
Nghị định này quy định chi tiết một số điều của Luật Doanh nghiệp về:
1. Đăng ký doanh nghiệp
2. Quản lý nhà nước về đăng ký doanh nghiệp

Điều 2. Đối tượng áp dụng
1. Cơ quan nhà nước
2. Tổ chức, cá nhân có liên quan đến việc đăng ký doanh nghiệp

Chương II
ĐĂNG KÝ DOANH NGHIỆP

Điều 3. Hồ sơ đăng ký doanh nghiệp
1. Giấy đề nghị đăng ký doanh nghiệp
a) Tên doanh nghiệp
b) Địa chỉ trụ sở chính
2. Điều lệ công ty`

export default function Home() {
  const [inputText, setInputText] = useState("")
  const [parseResult, setParseResult] = useState<any>(null)
  const [cypherResult, setCypherResult] = useState("")
  const [urnResult, setUrnResult] = useState<any>(null)
  const [chatMessages, setChatMessages] = useState<Array<{ role: string; content: string }>>([])
  const [chatInput, setChatInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const loadSample = () => {
    setInputText(SAMPLE_DOCUMENT)
  }

  const parseDocument = async () => {
    if (!inputText.trim()) return
    setIsLoading(true)
    try {
      const res = await fetch("/api/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: inputText }),
      })
      const data = await res.json()
      setParseResult(data)
    } catch (error) {
      console.error("Parse error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const generateCypher = async () => {
    if (!inputText.trim()) return
    setIsLoading(true)
    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: inputText, type: "cypher" }),
      })
      const data = await res.json()
      setCypherResult(data.cypher)
      setUrnResult({ urn: data.urn, stats: data.stats })
    } catch (error) {
      console.error("Generate error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const sendChatMessage = async () => {
    if (!chatInput.trim()) return
    const newMessage = { role: "user", content: chatInput }
    setChatMessages((prev) => [...prev, newMessage])
    setChatInput("")
    setIsLoading(true)

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [...chatMessages, newMessage],
          model: "gpt-4o",
        }),
      })

      const reader = res.body?.getReader()
      const decoder = new TextDecoder()
      let assistantMessage = ""

      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          assistantMessage += decoder.decode(value)
        }
      }

      setChatMessages((prev) => [...prev, { role: "assistant", content: assistantMessage }])
    } catch (error) {
      console.error("Chat error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-gradient-to-r from-primary/10 via-primary/5 to-background">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Vietnamese Legal Parser</h1>
              <p className="text-sm text-muted-foreground">
                Parse legal documents into Neo4j Knowledge Graphs with AI assistance
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                Sign In
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <Tabs defaultValue="parse" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 md:grid-cols-4 lg:w-auto lg:inline-grid">
            <TabsTrigger value="parse" className="gap-2">
              <FileText className="h-4 w-4" />
              <span className="hidden sm:inline">Parse</span>
            </TabsTrigger>
            <TabsTrigger value="generate" className="gap-2">
              <Code className="h-4 w-4" />
              <span className="hidden sm:inline">Generate</span>
            </TabsTrigger>
            <TabsTrigger value="chat" className="gap-2">
              <MessageSquare className="h-4 w-4" />
              <span className="hidden sm:inline">AI Chat</span>
            </TabsTrigger>
            <TabsTrigger value="about" className="gap-2">
              <Sparkles className="h-4 w-4" />
              <span className="hidden sm:inline">About</span>
            </TabsTrigger>
          </TabsList>

          {/* Parse Tab */}
          <TabsContent value="parse" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Input Document</CardTitle>
                  <CardDescription>Paste Vietnamese legal document text</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Textarea
                    placeholder="Paste your legal document here..."
                    className="min-h-[300px] font-mono text-sm"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                  />
                  <div className="flex gap-2">
                    <Button onClick={loadSample} variant="outline" size="sm">
                      Load Sample
                    </Button>
                    <Button onClick={parseDocument} disabled={isLoading || !inputText.trim()}>
                      {isLoading ? "Parsing..." : "Parse Document"}
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Parse Result</CardTitle>
                  <CardDescription>Extracted structure and metadata</CardDescription>
                </CardHeader>
                <CardContent>
                  {parseResult ? (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div className="rounded bg-muted p-2">
                          <span className="font-medium">Type:</span>{" "}
                          {parseResult.data?.metadata?.loaiVanBan}
                        </div>
                        <div className="rounded bg-muted p-2">
                          <span className="font-medium">Components:</span>{" "}
                          {parseResult.stats?.componentCount}
                        </div>
                      </div>
                      <pre className="max-h-[250px] overflow-auto rounded bg-muted p-3 text-xs">
                        {JSON.stringify(parseResult, null, 2)}
                      </pre>
                    </div>
                  ) : (
                    <div className="flex h-[300px] items-center justify-center text-muted-foreground">
                      Parse a document to see results
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Generate Tab */}
          <TabsContent value="generate" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Document Input</CardTitle>
                  <CardDescription>Enter document to generate Cypher queries</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Textarea
                    placeholder="Paste your legal document here..."
                    className="min-h-[200px] font-mono text-sm"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                  />
                  <div className="flex gap-2">
                    <Button onClick={loadSample} variant="outline" size="sm">
                      Load Sample
                    </Button>
                    <Button onClick={generateCypher} disabled={isLoading || !inputText.trim()}>
                      <Database className="mr-2 h-4 w-4" />
                      Generate Cypher
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Generated Output</CardTitle>
                  <CardDescription>Neo4j Cypher statements and URN</CardDescription>
                </CardHeader>
                <CardContent>
                  {cypherResult ? (
                    <div className="space-y-4">
                      {urnResult && (
                        <div className="rounded bg-muted p-3">
                          <div className="flex items-center gap-2 text-sm">
                            <Link className="h-4 w-4" />
                            <span className="font-mono text-xs break-all">{urnResult.urn}</span>
                          </div>
                        </div>
                      )}
                      <div className="relative">
                        <pre className="max-h-[200px] overflow-auto rounded bg-muted p-3 text-xs">
                          {cypherResult}
                        </pre>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="absolute right-2 top-2"
                          onClick={() => copyToClipboard(cypherResult)}
                        >
                          Copy
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex h-[250px] items-center justify-center text-muted-foreground">
                      Generate Cypher to see output
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Chat Tab */}
          <TabsContent value="chat">
            <Card>
              <CardHeader>
                <CardTitle>AI Legal Assistant</CardTitle>
                <CardDescription>
                  Ask questions about Vietnamese legal documents (Powered by OpenRouter)
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="min-h-[300px] max-h-[400px] overflow-auto rounded border p-4 space-y-4">
                  {chatMessages.length === 0 ? (
                    <div className="flex h-full items-center justify-center text-muted-foreground">
                      Start a conversation about Vietnamese legal documents
                    </div>
                  ) : (
                    chatMessages.map((msg, idx) => (
                      <div
                        key={idx}
                        className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                      >
                        <div
                          className={`max-w-[80%] rounded-lg p-3 ${
                            msg.role === "user"
                              ? "bg-primary text-primary-foreground"
                              : "bg-muted"
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                        </div>
                      </div>
                    ))
                  )}
                </div>
                <div className="flex gap-2">
                  <Input
                    placeholder="Ask about Vietnamese legal documents..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && sendChatMessage()}
                  />
                  <Button onClick={sendChatMessage} disabled={isLoading || !chatInput.trim()}>
                    Send
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* About Tab */}
          <TabsContent value="about">
            <Card>
              <CardHeader>
                <CardTitle>About Vietnamese Legal Parser</CardTitle>
                <CardDescription>Modern stack for legal document analysis</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  <div className="rounded-lg border p-4">
                    <h3 className="font-semibold">Authentication</h3>
                    <p className="text-sm text-muted-foreground">
                      Better Auth with Google OAuth integration
                    </p>
                  </div>
                  <div className="rounded-lg border p-4">
                    <h3 className="font-semibold">Database</h3>
                    <p className="text-sm text-muted-foreground">
                      Drizzle ORM with PostgreSQL
                    </p>
                  </div>
                  <div className="rounded-lg border p-4">
                    <h3 className="font-semibold">AI Integration</h3>
                    <p className="text-sm text-muted-foreground">
                      Vercel AI SDK with OpenRouter (100+ models)
                    </p>
                  </div>
                  <div className="rounded-lg border p-4">
                    <h3 className="font-semibold">UI Components</h3>
                    <p className="text-sm text-muted-foreground">
                      shadcn/ui with Tailwind CSS
                    </p>
                  </div>
                  <div className="rounded-lg border p-4">
                    <h3 className="font-semibold">Framework</h3>
                    <p className="text-sm text-muted-foreground">
                      Next.js 15, React 19, TypeScript
                    </p>
                  </div>
                  <div className="rounded-lg border p-4">
                    <h3 className="font-semibold">Design</h3>
                    <p className="text-sm text-muted-foreground">
                      Mobile-first responsive approach
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t mt-8">
        <div className="container mx-auto px-4 py-4 text-center text-sm text-muted-foreground">
          Vietnamese Legal Parser - Built with Next.js 15 & shadcn/ui
        </div>
      </footer>
    </div>
  )
}
