"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  FileText,
  Calendar,
  User,
  Flag,
  Network,
  Activity,
  Code2,
  MessageSquare,
  BookOpen,
  RefreshCw
} from "lucide-react"
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts'

const SAMPLE_DOCUMENT = `NGHỊ ĐỊNH 15/2020/NĐ-CP
QUY ĐỊNH XỬ PHẠT VI PHẠM HÀNH CHÍNH TRONG LĨNH VỰC BƯU CHÍNH, VIỄN THÔNG

Chính phủ ban hành Nghị định số 15/2020/NĐ-CP.
Ngày 03 tháng 02 năm 2020

Căn cứ Luật Tổ chức Chính phủ ngày 19 tháng 6 năm 2015;
Căn cứ Luật Xử lý vi phạm hành chính ngày 20 tháng 6 năm 2012;
Theo đề nghị của Bộ trưởng Bộ Thông tin và Truyền thông;

Chính phủ ban hành Nghị định quy định xử phạt vi phạm hành chính trong lĩnh vực bưu chính, viễn thông, tần số vô tuyến điện, công nghệ thông tin và giao dịch điện tử.

Phần I
NHỮNG QUY ĐỊNH CHUNG

Chương I
PHẠM VI ĐIỀU CHỈNH VÀ ĐỐI TƯỢNG ÁP DỤNG

Điều 1. Phạm vi điều chỉnh

1. Nghị định này quy định về hành vi vi phạm hành chính, hình thức xử phạt, mức xử phạt, biện pháp khắc phục hậu quả, thẩm quyền lập biên bản và thẩm quyền xử phạt vi phạm hành chính trong các lĩnh vực:

a) Bưu chính;
b) Viễn thông;
c) Tần số vô tuyến điện;
d) Công nghệ thông tin và giao dịch điện tử.`

// Mock data for charts
const relationshipData = [
  { name: 'CAN_CU', value: 3, color: '#3b82f6' },
  { name: 'HUONG_DAN_THI_HANH', value: 2, color: '#10b981' },
  { name: 'THAM_CHIEU', value: 1, color: '#f59e0b' }
]

const actionsData = [
  { name: 'BAN_HANH', value: 3 },
  { name: 'SUA_DOI', value: 2 },
  { name: 'HET_HIEU_LUC', value: 1 },
  { name: 'BAI_BO', value: 1 }
]

export default function Home() {
  const [inputText, setInputText] = useState(SAMPLE_DOCUMENT)
  const [parseResult, setParseResult] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isAnalyzed, setIsAnalyzed] = useState(false)

  const analyzeDocument = async () => {
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
      setIsAnalyzed(true)
    } catch (error) {
      console.error("Parse error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  // Mock parsed data (replace with actual parseResult data)
  const mockData = {
    documentType: "NGHI_DINH",
    legalLevel: 6,
    effectiveDate: "2015-06-19",
    signedDate: "2015-06-19",
    signer: "THỦ TƯỚNG",
    signerEn: "Thủ tướng",
    status: "HIEU_LUC",
    statusEn: "Active"
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="border-b bg-gradient-to-r from-slate-900 to-slate-800 text-white">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-blue-500 p-2 rounded">
                <BookOpen className="h-6 w-6" />
              </div>
              <div>
                <h1 className="text-xl font-bold">VN Legal Parser</h1>
                <p className="text-xs text-slate-300">v2.0.0-enhanced</p>
              </div>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 bg-green-400 rounded-full"></div>
                <span>15 Document Types</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 bg-blue-400 rounded-full"></div>
                <span>7-Level Hierarchy</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 bg-purple-400 rounded-full"></div>
                <span>Neo4j 5.x Ready</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Left Panel - Source Document */}
          <div className="lg:col-span-2">
            <Card className="h-[calc(100vh-180px)]">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    <CardTitle className="text-base">Source Document</CardTitle>
                  </div>
                  <Button
                    size="sm"
                    onClick={analyzeDocument}
                    disabled={isLoading || !inputText.trim()}
                    className="gap-2"
                  >
                    {isLoading ? (
                      <>
                        <RefreshCw className="h-4 w-4 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Activity className="h-4 w-4" />
                        Analyze
                      </>
                    )}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <textarea
                  className="w-full h-[calc(100vh-280px)] p-3 text-sm font-mono border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Paste your Vietnamese legal document here..."
                />
                <div className="mt-3 text-xs text-slate-500">
                  {inputText.split('\n').length} lines • {inputText.length} characters
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Panel - Analysis Results */}
          <div className="lg:col-span-3">
            <Tabs defaultValue="overview" className="space-y-4">
              <TabsList className="grid w-full grid-cols-6 bg-white border">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="structure">Structure</TabsTrigger>
                <TabsTrigger value="relationships">Relationships</TabsTrigger>
                <TabsTrigger value="actions">Actions</TabsTrigger>
                <TabsTrigger value="json">JSON / Neo4j</TabsTrigger>
                <TabsTrigger value="ai">AI Assistant</TabsTrigger>
              </TabsList>

              {/* Overview Tab */}
              <TabsContent value="overview" className="space-y-4">
                {/* Top Row - Metadata Cards */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <Card>
                    <CardHeader className="pb-3">
                      <div className="flex items-center gap-2 text-blue-600">
                        <FileText className="h-4 w-4" />
                        <CardTitle className="text-sm font-medium">Document Type</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{mockData.documentType}</div>
                      <p className="text-xs text-slate-500 mt-1">Legal Level: {mockData.legalLevel}</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-3">
                      <div className="flex items-center gap-2 text-green-600">
                        <Calendar className="h-4 w-4" />
                        <CardTitle className="text-sm font-medium">Effective Date</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{mockData.effectiveDate}</div>
                      <p className="text-xs text-slate-500 mt-1">Signed: {mockData.signedDate}</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-3">
                      <div className="flex items-center gap-2 text-purple-600">
                        <User className="h-4 w-4" />
                        <CardTitle className="text-sm font-medium">Signer</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{mockData.signer}</div>
                      <p className="text-xs text-slate-500 mt-1">{mockData.signerEn}</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-3">
                      <div className="flex items-center gap-2 text-amber-600">
                        <Flag className="h-4 w-4" />
                        <CardTitle className="text-sm font-medium">Status</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{mockData.status}</div>
                      <div className="mt-1">
                        <span className="inline-block px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                          {mockData.statusEn}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Bottom Row - Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {/* Relationship Distribution */}
                  <Card>
                    <CardHeader>
                      <div className="flex items-center gap-2">
                        <Network className="h-4 w-4 text-blue-600" />
                        <CardTitle className="text-base">Relationship Distribution</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={relationshipData}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={100}
                            paddingAngle={5}
                            dataKey="value"
                          >
                            {relationshipData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                      <div className="flex flex-wrap gap-4 justify-center mt-4">
                        {relationshipData.map((item) => (
                          <div key={item.name} className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded" style={{ backgroundColor: item.color }}></div>
                            <span className="text-xs">{item.name}</span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Legislative Actions */}
                  <Card>
                    <CardHeader>
                      <div className="flex items-center gap-2">
                        <Activity className="h-4 w-4 text-green-600" />
                        <CardTitle className="text-base">Legislative Actions</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={actionsData}>
                          <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              {/* Structure Tab */}
              <TabsContent value="structure">
                <Card>
                  <CardHeader>
                    <CardTitle>Document Structure</CardTitle>
                    <CardDescription>Hierarchical breakdown of the legal document</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm">
                      <div className="border-l-2 border-blue-500 pl-4 py-2">
                        <div className="font-semibold">Phần I - NHỮNG QUY ĐỊNH CHUNG</div>
                        <div className="ml-4 mt-2 border-l-2 border-green-500 pl-4 py-2">
                          <div className="font-semibold">Chương I - PHẠM VI ĐIỀU CHỈNH VÀ ĐỐI TƯỢNG ÁP DỤNG</div>
                          <div className="ml-4 mt-2 space-y-1">
                            <div className="text-slate-600">Điều 1. Phạm vi điều chỉnh</div>
                            <div className="ml-4 text-xs text-slate-500">
                              <div>1. Nghị định này quy định...</div>
                              <div className="ml-4">
                                <div>a) Bưu chính;</div>
                                <div>b) Viễn thông;</div>
                                <div>c) Tần số vô tuyến điện;</div>
                                <div>d) Công nghệ thông tin...</div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Relationships Tab */}
              <TabsContent value="relationships">
                <Card>
                  <CardHeader>
                    <CardTitle>Legal Relationships</CardTitle>
                    <CardDescription>Cross-references and legal connections</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="border rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="w-3 h-3 bg-blue-500 rounded"></div>
                          <span className="font-semibold text-sm">CĂN CỨ (Legal Basis)</span>
                        </div>
                        <ul className="text-sm space-y-1 ml-5">
                          <li className="text-slate-600">• Luật Tổ chức Chính phủ ngày 19 tháng 6 năm 2015</li>
                          <li className="text-slate-600">• Luật Xử lý vi phạm hành chính ngày 20 tháng 6 năm 2012</li>
                          <li className="text-slate-600">• Đề nghị của Bộ trưởng Bộ Thông tin và Truyền thông</li>
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Actions Tab */}
              <TabsContent value="actions">
                <Card>
                  <CardHeader>
                    <CardTitle>Legislative Actions</CardTitle>
                    <CardDescription>Document lifecycle and amendments</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="border-l-4 border-green-500 pl-4 py-2">
                        <div className="font-semibold text-sm">BAN_HANH (Promulgation)</div>
                        <div className="text-xs text-slate-500 mt-1">Ngày 03 tháng 02 năm 2020</div>
                      </div>
                      <div className="border-l-4 border-blue-500 pl-4 py-2">
                        <div className="font-semibold text-sm">HIEU_LUC (Effective)</div>
                        <div className="text-xs text-slate-500 mt-1">From: 2015-06-19</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* JSON / Neo4j Tab */}
              <TabsContent value="json">
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>JSON / Neo4j Export</CardTitle>
                        <CardDescription>Structured data and Cypher queries</CardDescription>
                      </div>
                      <Button size="sm" variant="outline">
                        <Code2 className="h-4 w-4 mr-2" />
                        Copy Cypher
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-semibold mb-2">JSON Structure</h4>
                        <pre className="bg-slate-100 p-3 rounded text-xs overflow-auto max-h-60">
{JSON.stringify(parseResult || mockData, null, 2)}
                        </pre>
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold mb-2">Cypher Query</h4>
                        <pre className="bg-slate-100 p-3 rounded text-xs overflow-auto max-h-40">
{`CREATE (d:VanBan {
  loaiVanBan: "NGHI_DINH",
  capPhapLy: 6,
  ngayHieuLuc: "2015-06-19"
})`}
                        </pre>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* AI Assistant Tab */}
              <TabsContent value="ai">
                <Card>
                  <CardHeader>
                    <div className="flex items-center gap-2">
                      <MessageSquare className="h-4 w-4" />
                      <CardTitle>AI Legal Assistant</CardTitle>
                    </div>
                    <CardDescription>Ask questions about this document</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="bg-slate-100 rounded-lg p-4 min-h-[300px]">
                        <p className="text-sm text-slate-500 text-center mt-20">
                          AI Assistant coming soon...
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <input
                          type="text"
                          placeholder="Ask a question about this document..."
                          className="flex-1 px-3 py-2 border rounded-md text-sm"
                          disabled
                        />
                        <Button disabled>Send</Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </main>
    </div>
  )
}
