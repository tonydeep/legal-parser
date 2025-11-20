// Vietnamese Legal Document Parser - TypeScript Implementation

export const DOC_TYPE_PATTERNS: Record<string, string> = {
  "^HIẾN PHÁP": "HIEN_PHAP",
  "^BỘ LUẬT": "BO_LUAT",
  "^LUẬT": "LUAT",
  "^PHÁP LỆNH": "PHAP_LENH",
  "^NGHỊ QUYẾT": "NGHI_QUYET",
  "^NGHỊ ĐỊNH": "NGHI_DINH",
  "^QUYẾT ĐỊNH": "QUYET_DINH",
  "^CHỈ THỊ": "CHI_THI",
  "^THÔNG TƯ LIÊN TỊCH": "THONG_TU_LIEN_TICH",
  "^THÔNG TƯ": "THONG_TU",
  "^THÔNG BÁO": "THONG_BAO",
  "^HƯỚNG DẪN": "HUONG_DAN",
  "^QUY CHẾ": "QUY_CHE",
  "^QUY ĐỊNH": "QUY_DINH",
  "^ĐIỀU LỆ": "DIEU_LE",
}

export const LEGISLATIVE_ACTIONS: Record<string, string> = {
  "ban hành": "BAN_HANH",
  "sửa đổi": "SUA_DOI",
  "bổ sung": "BO_SUNG",
  "thay thế": "THAY_THE",
  "bãi bỏ": "BAI_BO",
  "đình chỉ": "DINH_CHI",
  "hủy bỏ": "HUY_BO",
  "hết hiệu lực": "HET_HIEU_LUC",
}

export interface ParsedComponent {
  type: string
  level: number
  number: string
  title: string
  content: string
  children: ParsedComponent[]
}

export interface ParsedDocument {
  metadata: {
    loaiVanBan: string
    soHieu: string | null
    ngayBanHanh: string | null
    coQuanBanHanh: string | null
    tieuDe: string | null
    hanhDongLapPhap: string
  }
  structure: ParsedComponent[]
  crossReferences: string[]
  definitions: Record<string, string>
}

export function parseDocument(text: string): ParsedDocument {
  const lines = text.split("\n")

  // Detect document type
  let docType = "VAN_BAN"
  for (const [pattern, type] of Object.entries(DOC_TYPE_PATTERNS)) {
    if (new RegExp(pattern, "i").test(text)) {
      docType = type
      break
    }
  }

  // Extract document number
  const numberMatch = text.match(/Số:\s*([^\n]+)/i)
  const docNumber = numberMatch ? numberMatch[1].trim() : null

  // Extract issue date
  const dateMatch = text.match(/ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})/i)
  const issueDate = dateMatch
    ? `${dateMatch[3]}-${dateMatch[2].padStart(2, "0")}-${dateMatch[1].padStart(2, "0")}`
    : null

  // Detect legislative action
  let action = "BAN_HANH"
  const lowerText = text.toLowerCase()
  for (const [pattern, actionType] of Object.entries(LEGISLATIVE_ACTIONS)) {
    if (lowerText.includes(pattern)) {
      action = actionType
      break
    }
  }

  // Parse structure
  const structure: ParsedComponent[] = []
  const stack: ParsedComponent[] = []

  // Component patterns with levels
  const componentPatterns = [
    { regex: /^Phần\s+(thứ\s+)?([IVXLCDM]+|[0-9]+)[.:]\s*(.*)$/i, type: "PHAN", level: 1 },
    { regex: /^Chương\s+([IVXLCDM]+|[0-9]+)[.:]\s*(.*)$/i, type: "CHUONG", level: 2 },
    { regex: /^Mục\s+([0-9]+)[.:]\s*(.*)$/i, type: "MUC", level: 3 },
    { regex: /^Điều\s+([0-9]+)[.:]\s*(.*)$/i, type: "DIEU", level: 4 },
    { regex: /^([0-9]+)\.\s+(.*)$/i, type: "KHOAN", level: 5 },
    { regex: /^([a-z])\)\s+(.*)$/i, type: "DIEM", level: 6 },
  ]

  let currentContent: string[] = []

  for (const line of lines) {
    let matched = false

    for (const { regex, type, level } of componentPatterns) {
      const match = line.match(regex)
      if (match) {
        // Save previous content
        if (stack.length > 0) {
          stack[stack.length - 1].content = currentContent.join("\n").trim()
        }

        const component: ParsedComponent = {
          type,
          level,
          number: match[1] || "",
          title: match[match.length - 1] || "",
          content: "",
          children: [],
        }

        // Find parent
        while (stack.length > 0 && stack[stack.length - 1].level >= level) {
          stack.pop()
        }

        if (stack.length === 0) {
          structure.push(component)
        } else {
          stack[stack.length - 1].children.push(component)
        }

        stack.push(component)
        currentContent = []
        matched = true
        break
      }
    }

    if (!matched && line.trim()) {
      currentContent.push(line)
    }
  }

  // Save last content
  if (stack.length > 0) {
    stack[stack.length - 1].content = currentContent.join("\n").trim()
  }

  // Extract cross-references
  const crossRefRegex = /(?:Điều|Khoản|Điểm)\s+[\d]+(?:\s+(?:Luật|Nghị định|Thông tư)[^,;.]+)?/gi
  const crossReferences = [...new Set(text.match(crossRefRegex) || [])]

  return {
    metadata: {
      loaiVanBan: docType,
      soHieu: docNumber,
      ngayBanHanh: issueDate,
      coQuanBanHanh: null,
      tieuDe: null,
      hanhDongLapPhap: action,
    },
    structure,
    crossReferences,
    definitions: {},
  }
}

// URN Generator
export function generateURN(
  docType: string,
  authority: string,
  issueDate: string,
  number: string
): string {
  const normalizedType = docType.toLowerCase().replace(/_/g, "")
  const normalizedAuth = authority.toLowerCase().replace(/_/g, "")
  const normalizedNum = number
    .replace(/\//g, "-")
    .replace(/[^a-zA-Z0-9-]/g, "")

  return `urn:lex:vn:${normalizedAuth}:${normalizedType}:${issueDate};${normalizedNum}`
}

// Cypher Generator
export function generateCypher(parsed: ParsedDocument, urn: string): string {
  const statements: string[] = []
  const timestamp = new Date().toISOString()

  statements.push(`// Vietnamese Legal Document Import - Neo4j 5.x`)
  statements.push(`// Generated: ${timestamp}`)
  statements.push(`// Document Type: ${parsed.metadata.loaiVanBan}`)
  statements.push(``)

  // Create document node
  statements.push(`// Create VanBan (Document)`)
  statements.push(`MERGE (vb:VanBan {urn: '${urn}'})`)
  statements.push(`SET vb += {`)
  statements.push(`  loaiVanBan: '${parsed.metadata.loaiVanBan}',`)
  statements.push(`  soHieu: ${parsed.metadata.soHieu ? `'${parsed.metadata.soHieu}'` : "null"},`)
  statements.push(`  ngayBanHanh: ${parsed.metadata.ngayBanHanh ? `date('${parsed.metadata.ngayBanHanh}')` : "null"},`)
  statements.push(`  hanhDongLapPhap: '${parsed.metadata.hanhDongLapPhap}'`)
  statements.push(`};`)
  statements.push(``)

  // Create components recursively
  function createComponents(components: ParsedComponent[], parentVar: string, depth: number) {
    components.forEach((comp, idx) => {
      const varName = `c${depth}_${idx}`
      statements.push(`// Create ${comp.type} ${comp.number}`)
      statements.push(`MATCH (${parentVar})`)
      statements.push(`MERGE (${varName}:ThanhPhanVanBan {`)
      statements.push(`  urn: '${urn}#${comp.type.toLowerCase()}_${comp.number}'`)
      statements.push(`})`)
      statements.push(`SET ${varName} += {`)
      statements.push(`  loaiThanhPhan: '${comp.type}',`)
      statements.push(`  soThuTu: '${comp.number}',`)
      statements.push(`  tieuDe: '${comp.title.replace(/'/g, "\\'")}',`)
      statements.push(`  noiDung: '${comp.content.substring(0, 500).replace(/'/g, "\\'").replace(/\n/g, " ")}'`)
      statements.push(`};`)
      statements.push(`MERGE (${parentVar})-[:HAS_COMPONENT]->(${varName});`)
      statements.push(``)

      if (comp.children.length > 0) {
        createComponents(comp.children, varName, depth + 1)
      }
    })
  }

  if (parsed.structure.length > 0) {
    statements.push(`// Create Component Hierarchy`)
    createComponents(parsed.structure, "vb:VanBan {urn: '" + urn + "'}", 0)
  }

  return statements.join("\n")
}

// Count components
export function countComponents(structure: ParsedComponent[]): number {
  let count = 0
  for (const comp of structure) {
    count++
    count += countComponents(comp.children)
  }
  return count
}
