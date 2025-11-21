# Vietnamese Legal Parser

A comprehensive web interface for parsing Vietnamese legal documents into Neo4j Structure-Aware Temporal Property Graphs with modern data visualization and AI assistance.

## 🚀 Quick Start

### Modern Next.js Interface (Recommended)

```bash
cd web
npm install
npm run dev
```

Visit **http://localhost:3000** to access the modern interface.

### Classic Flask Demo

```bash
pip install -r requirements.txt --break-system-packages
python app.py
```

Visit **http://localhost:5000** for the classic interface.

---

## ✨ Features

### 🎨 Modern Web Interface (Next.js)

- **Split-Panel Design**: Source document editor on left, real-time analysis on right
- **Professional Dashboard**: Version badges and feature indicators
- **6 Comprehensive Tabs**:
  - **Overview**: Metadata cards + interactive charts
  - **Structure**: Hierarchical document breakdown
  - **Relationships**: Legal cross-references visualization
  - **Actions**: Document lifecycle timeline
  - **JSON/Neo4j**: Structured data and Cypher export
  - **AI Assistant**: Future AI integration
- **Interactive Charts**:
  - Relationship Distribution (Donut chart)
  - Legislative Actions (Bar chart)
- **Real-time Analysis**: Instant document parsing with visual feedback

### 📊 Core Capabilities

🏛️ **15 Document Types** covering full Vietnamese legal hierarchy
📊 **7-Tier Structure** from Phần to Tiểu mục
⚖️ **8 Legislative Actions** (Ban hành, Sửa đổi, Bổ sung, etc.)
🔗 **5 Legal Relationships** (Căn cứ, Hướng dẫn thi hành, Quy định chi tiết, Kế thừa, Tham chiếu)
🔍 **Real-time Parsing** with JSON validation
⚙️ **Cypher Generation** for Neo4j 5.x import
📥 **Export Options**: JSON, Cypher scripts

---

## 📸 Interface Overview

### Modern Next.js Interface

The new interface features:

1. **Header Bar**
   - VN Legal Parser branding
   - Version badge (v2.0.0-enhanced)
   - Feature indicators: 15 Document Types, 7-Level Hierarchy, Neo4j 5.x Ready

2. **Source Document Panel** (Left)
   - Full-height text editor
   - Character and line count
   - One-click "Analyze" button

3. **Analysis Panel** (Right)
   - **Overview Tab**: 4 metadata cards + 2 interactive charts
   - **Structure Tab**: Visual hierarchy tree
   - **Relationships Tab**: Cross-reference breakdown
   - **Actions Tab**: Legislative action timeline
   - **JSON/Neo4j Tab**: Export options
   - **AI Assistant Tab**: Future integration

---

## 🛠️ Installation

### Next.js Web Interface

```bash
# Navigate to web directory
cd web

# Install dependencies
npm install

# Development mode
npm run dev

# Production build
npm run build
npm start
```

**Environment Variables** (optional):
```bash
cp .env.example .env
# Configure database, auth, AI settings in .env
```

### Python Parser (Backend/CLI)

```bash
# Install Python dependencies
pip install -r requirements.txt --break-system-packages
```

Or manually:
```bash
pip install Flask pdfplumber python-docx beautifulsoup4 lxml
```

---

## 📖 Usage

### Web Interface

1. **Open** http://localhost:3000 (Next.js) or http://localhost:5000 (Flask)
2. **Paste** or type Vietnamese legal document text in the left panel
3. **Click** "Analyze" button
4. **Review** parsed results in the Overview tab:
   - Document Type, Effective Date, Signer, Status
   - Relationship Distribution chart
   - Legislative Actions chart
5. **Explore** other tabs for detailed structure, relationships, actions
6. **Export** JSON or Cypher from the JSON/Neo4j tab

### API Endpoints (Next.js)

#### `POST /api/parse`
Parse a document and return structured JSON.

**Request**:
```json
{
  "text": "NGHỊ ĐỊNH\n\nVỀ CÔNG TÁC VĂN THƯ\n..."
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "metadata": {
      "loaiVanBan": "NGHI_DINH",
      "soHieu": "15/2020/NĐ-CP",
      "ngayBanHanh": "2020-02-03",
      "hanhDongLapPhap": "BAN_HANH"
    },
    "structure": [...],
    "crossReferences": [...],
    "definitions": {}
  },
  "stats": {
    "componentCount": 15,
    "crossReferences": 3,
    "definitionsCount": 0
  }
}
```

#### `POST /api/generate`
Generate Cypher script from parsed document.

**Request**:
```json
{
  "text": "NGHỊ ĐỊNH\n...",
  "type": "cypher"
}
```

**Response**:
```json
{
  "success": true,
  "cypher": "// Cypher statements...",
  "urn": "urn:lex:vn:...",
  "stats": {
    "nodeCount": 16,
    "relationshipCount": 20
  }
}
```

---

## 📁 Project Structure

```
legal-parser/
├── web/                           # Next.js Web Interface (NEW)
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx          # Main interface
│   │   │   ├── layout.tsx        # Root layout
│   │   │   └── api/              # API routes
│   │   │       ├── parse/        # Parse endpoint
│   │   │       ├── generate/     # Cypher generation
│   │   │       ├── chat/         # AI assistant
│   │   │       └── auth/         # Authentication
│   │   ├── components/ui/        # shadcn/ui components
│   │   └── lib/
│   │       ├── parser.ts         # TypeScript parser
│   │       ├── auth.ts           # Better Auth config
│   │       └── db/               # Database schema
│   ├── package.json
│   └── next.config.ts
├── app.py                         # Flask backend (Classic)
├── document_parser.py             # Python parser
├── cypher_generator.py            # Cypher generator (basic)
├── cypher_generator_enhanced.py   # Enhanced Cypher generator
├── urn_generator.py               # URN generator
├── query_templates.py             # Query templates
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🏛️ Supported Document Types (15 Types)

1. **Hiến pháp** (HIEN_PHAP) - Constitution
2. **Bộ luật** (BO_LUAT) - Legal Code
3. **Luật** (LUAT) - Law
4. **Nghị quyết Quốc hội** (NGHI_QUYET_QH) - National Assembly Resolution
5. **Pháp lệnh** (PHAP_LENH) - Ordinance
6. **Nghị quyết UBTVQH** (NGHI_QUYET_UBTVQH) - Standing Committee Resolution
7. **Nghị định** (NGHI_DINH) - Decree
8. **Thông tư** (THONG_TU) - Circular
9. **Quyết định Thủ tướng** (QUYET_DINH_TTG) - Prime Minister Decision
10. **Quyết định Bộ trưởng** (QUYET_DINH_BO_TRUONG) - Minister Decision
11. **Quyết định Chủ tịch** (QUYET_DINH_CHU_TICH) - Chairman Decision
12. **Quyết định** (QUYET_DINH) - General Decision
13. **Chỉ thị** (CHI_THI) - Directive
14. **Nghị quyết** (NGHI_QUYET) - General Resolution
15. **Thông tư liên tịch** (THONG_TU_LIEN_TICH) - Joint Circular

---

## 📊 Structure Hierarchy (7-Tier System)

Recognizes 7 hierarchical levels:

1. **Phần** (Part) - Level 1
2. **Chương** (Chapter) - Level 2
3. **Mục** (Section) - Level 3
4. **Điều** (Article) - Level 4
5. **Khoản** (Clause) - Level 5
6. **Điểm** (Point) - Level 6
7. **Tiểu mục** (Sub-section) - Level 7

---

## ⚖️ Legislative Actions (8 Types)

The parser detects and classifies:

1. **Ban hành** (BAN_HANH) - Issue/Promulgate
2. **Sửa đổi** (SUA_DOI) - Amend
3. **Bổ sung** (BO_SUNG) - Supplement
4. **Thay thế** (THAY_THE) - Replace
5. **Bãi bỏ** (BAI_BO) - Abolish
6. **Đình chỉ** (DINH_CHI) - Suspend
7. **Hủy bỏ** (HUY_BO) - Revoke
8. **Hết hiệu lực** (HET_HIEU_LUC) - Expire

---

## 🔗 Legal Relationships (5 Types)

1. **CAN_CU** - Legal basis
2. **HUONG_DAN_THI_HANH** - Implementation guidance
3. **QUY_DINH_CHI_TIET** - Detailed regulation
4. **KE_THUA** - Inheritance
5. **THAM_CHIEU** - General reference

---

## 🗄️ Generated Graph Schema (Neo4j 5.x)

### Nodes

- **VanBan**: Document (Work level) with legislative action metadata
- **ThanhPhanVanBan**: Components with specialized labels (Phan, Chuong, Muc, Dieu, Khoan, Diem, TieuMuc)
- **PhienBanVanBan**: Temporal version
- **CTV**: Component Temporal Version (with content)
- **CoQuanBanHanh**: Issuing authority
- **VanBanThamChieu**: Referenced documents

### Relationships

- **HAS_COMPONENT**: Hierarchical structure
- **HAS_EXPRESSION**: Temporal versioning
- **AGGREGATES**: Temporal aggregation
- **ISSUED_BY**: Authority link
- **CAN_CU**: Legal basis relationship
- **HUONG_DAN_THI_HANH**: Implementation guidance
- **QUY_DINH_CHI_TIET**: Detailed regulation
- **KE_THUA**: Inheritance relationship
- **THAM_CHIEU**: General reference

---

## 📝 Example Usage

### Sample Document

```
NGHỊ ĐỊNH 15/2020/NĐ-CP
QUY ĐỊNH XỬ PHẠT VI PHẠM HÀNH CHÍNH TRONG LĨNH VỰC BƯU CHÍNH, VIỄN THÔNG

Căn cứ Luật Tổ chức Chính phủ ngày 19 tháng 6 năm 2015;
Căn cứ Luật Xử lý vi phạm hành chính ngày 20 tháng 6 năm 2012;

Chính phủ ban hành Nghị định quy định xử phạt vi phạm hành chính...

Phần I
NHỮNG QUY ĐỊNH CHUNG

Chương I
PHẠM VI ĐIỀU CHỈNH VÀ ĐỐI TƯỢNG ÁP DỤNG

Điều 1. Phạm vi điều chỉnh

1. Nghị định này quy định về hành vi vi phạm hành chính...

a) Bưu chính;
b) Viễn thông;
c) Tần số vô tuyến điện;
d) Công nghệ thông tin và giao dịch điện tử.
```

### Expected Output

**Parse Results**:
- Document Type: NGHI_DINH
- Legal Level: 6
- Components: 5 (1 Phần, 1 Chương, 1 Điều, 1 Khoản, 4 Điểm)
- Cross-references: 2 (Căn cứ)
- Legislative Action: BAN_HANH

**Cypher Output**:
- 1 VanBan node
- 5 ThanhPhanVanBan nodes
- 5 HAS_COMPONENT relationships
- URN: `urn:lex:vn:chinhphu:nghidinh:2020-02-03;15-2020-nd-cp`

---

## 💾 Neo4j Import

After exporting the Cypher file:

```bash
# Method 1: Cypher Shell
cat import.cypher | cypher-shell -u neo4j -p password

# Method 2: Neo4j Browser
# Open http://localhost:7474
# Paste and run the script

# Method 3: Python Driver
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
with open('import.cypher') as f:
    cypher = f.read()

with driver.session() as session:
    session.run(cypher)
```

---

## 🔧 Technical Stack

### Modern Web Interface

- **Framework**: Next.js 15 (App Router)
- **UI Library**: React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **Components**: shadcn/ui (Radix UI)
- **Charts**: Recharts 3.x
- **Icons**: Lucide React
- **Authentication**: Better Auth
- **Database**: PostgreSQL (Drizzle ORM)
- **AI**: Vercel AI SDK + OpenRouter

### Parser & Backend

- **Parser**: Custom TypeScript/Python implementation
- **Graph Model**: LRMoo (IFLA Library Reference Model)
- **Database Target**: Neo4j 5.x (backward compatible with 4.x)
- **File Processing**: pdfplumber, python-docx, BeautifulSoup
- **Classic Backend**: Flask 3.0 (Python)

---

## 🚧 Troubleshooting

### Web Interface Issues

**Build fails**:
- Ensure Node.js 18+ is installed
- Clear `.next` folder: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`

**Charts not displaying**:
- Check recharts is installed: `npm list recharts`
- Verify browser console for errors

### Parser Issues

**Empty structure returned**:
- Verify document follows standard Vietnamese legal format
- Check for Chương/Điều/Khoản keywords
- Try with sample document first

**Wrong document type detected**:
- Document may not start with standard keyword
- Check document preamble for proper formatting

### Neo4j Import Issues

**Import fails**:
- Verify Neo4j 5.x is running
- Check Cypher syntax in generated file
- Ensure no conflicting constraints exist

---

## 🎯 Future Enhancements

- [x] Modern Next.js interface with charts
- [x] Split-panel design
- [x] Interactive data visualization
- [ ] AI-powered document analysis
- [ ] Amendment document processing
- [ ] Internal reference detection
- [ ] Batch processing multiple documents
- [ ] Graph visualization preview
- [ ] Real-time collaboration
- [ ] OCR for scanned PDFs
- [ ] Multi-language support
- [ ] Advanced validation rules
- [ ] Version comparison view
- [ ] Direct Neo4j integration

---

## 📄 License

Custom implementation for Vietnamese legal document parsing.

---

## 🙏 Credits

Based on the Vietnamese Legal Parser implementing Structure-Aware Temporal Property Graph model following LRMoo ontology standards.

---

## 📞 Support

For issues or questions:
- Open a GitHub issue
- Review the parser output carefully
- Check JSON validation results
- Test with sample documents first

---

## 📋 Changelog

### Version 3.0 (2025-11-21)
- ✅ Built modern Next.js 15 web interface
- ✅ Added split-panel design with real-time analysis
- ✅ Implemented interactive charts (donut, bar)
- ✅ Created 6-tab navigation system
- ✅ Added TypeScript parser implementation
- ✅ Integrated Recharts for data visualization
- ✅ Professional dashboard with metadata cards

### Version 2.0 (2025-11-17)
- ✅ Added 7th hierarchical level: Tiểu mục (Sub-section)
- ✅ Expanded from 8 to 15 document types covering full legal hierarchy
- ✅ Implemented 8 legislative actions detection
- ✅ Added 5 legal relationship types
- ✅ Enhanced Neo4j 5.x compatibility
- ✅ Improved cross-reference detection

### Version 1.0 (2024-11-09)
- Initial release with 6-tier hierarchy
- Basic 8 document types
- Simple Căn cứ reference detection
- Flask web demo

---

**Version**: 3.0
**Last Updated**: 2025-11-21
**Author**: Claude AI Assistant
