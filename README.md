# Vietnamese Legal Parser - Web Demo

A beautiful web interface for parsing Vietnamese legal documents into Neo4j Structure-Aware Temporal Property Graphs.

## Features

✨ **Beautiful UI** with step-by-step workflow visualization
📤 **Multi-format Support**: Upload PDF, DOCX, HTML, or paste text
🔍 **Real-time Parsing** with JSON validation checkpoints
⚙️ **Cypher Generation** for Neo4j import
📥 **Download** generated Cypher scripts
🎯 **Interactive Results** with expandable structure trees

## Screenshots

### Main Interface
- Tab-based input (Paste Text / Upload File)
- Drag-and-drop file upload
- Workflow progress indicator (4 steps)

### Validation Checkpoints
- **Checkpoint 1**: Parse results with metadata, structure, definitions
- **Checkpoint 2**: Cypher generation summary with node/relationship counts

### Results Display
- Statistics cards with key metrics
- JSON metadata viewer
- Hierarchical structure tree
- Definitions list
- Downloadable Cypher script

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

Or manually:
```bash
pip install Flask pdfplumber python-docx beautifulsoup4 lxml --break-system-packages
```

### 2. Run the Server

```bash
python app.py
```

Server will start on: **http://localhost:5000**

## Usage

### Method 1: Paste Text

1. Click "📝 Paste Text" tab
2. Paste your Vietnamese legal document
3. Click "🔍 Parse Document"
4. Review parse results (Checkpoint 1)
5. Click "✅ Approve & Generate Cypher"
6. Download the .cypher file (Checkpoint 2)

### Method 2: Upload File

1. Click "📤 Upload File" tab
2. Drag & drop or click to browse
3. Select PDF/DOCX/HTML/TXT file (max 16MB)
4. Click "🔍 Parse Document"
5. Review and approve
6. Download generated Cypher

## API Endpoints

### `POST /api/parse`
Parse a document and return JSON summary.

**Request**:
```json
{
  "text": "NGHỊ ĐỊNH\n\nVỀ CÔNG TÁC VĂN THƯ\n..."
}
```
Or multipart form with file upload.

**Response**:
```json
{
  "success": true,
  "session_id": "session_20241109_123456",
  "summary": {
    "metadata": {...},
    "structure_summary": {...},
    "definitions": {...}
  }
}
```

### `POST /api/generate-cypher`
Generate Cypher script from parsed document.

**Request**:
```json
{
  "text": "NGHỊ ĐỊNH\n..."
}
```

**Response**:
```json
{
  "success": true,
  "filename": "import_20241109_123456.cypher",
  "download_url": "/api/download/import_20241109_123456.cypher",
  "summary": {...}
}
```

### `GET /api/download/<filename>`
Download generated Cypher file.

### `GET /api/health`
Health check endpoint.

## Project Structure

```
legal-parser-demo/
├── app.py                      # Flask backend
├── templates/
│   └── index.html             # Web UI
├── static/                    # (future: CSS/JS files)
├── uploads/                   # Uploaded files (temp)
├── outputs/                   # Generated Cypher files
├── document_parser.py         # Parser logic
├── cypher_generator.py        # Cypher generator
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Workflow Steps

### Step 1: Input
- User pastes text or uploads file
- File extraction for PDF/DOCX/HTML

### Step 2: Parse
- Extract document metadata
- Parse hierarchical structure
- Detect definitions
- Identify cross-references

### Step 3: Validate (Checkpoint 1)
- Display JSON summary
- Show statistics (components, definitions, etc.)
- Render structure tree
- User approval required

### Step 4: Generate (Checkpoint 2)
- Generate Cypher statements
- Create Neo4j import script
- Display generation summary
- Provide download link

## Supported Document Types

- 🏛️ **Hiến pháp** (HIEN_PHAP)
- 📜 **Luật** (LUAT)
- 📚 **Bộ luật** (BO_LUAT)
- 📋 **Nghị định** (NGHI_DINH)
- 📄 **Thông tư** (THONG_TU)
- 📌 **Quyết định** (QUYET_DINH)
- 📃 **Nghị quyết** (NGHI_QUYET)
- 📝 **Pháp lệnh** (PHAP_LENH)

## Structure Hierarchy

Recognizes 6 levels:
1. **Phần** (Part)
2. **Chương** (Chapter)
3. **Mục** (Section)
4. **Điều** (Article)
5. **Khoản** (Clause)
6. **Điểm** (Point)

## Generated Graph Schema

### Nodes
- **VanBan**: Document (Work level)
- **ThanhPhanVanBan**: Components with specialized labels (Phan, Chuong, Dieu, etc.)
- **PhienBanVanBan**: Temporal version
- **CTV**: Component Temporal Version (with content)
- **CoQuanBanHanh**: Issuing authority

### Relationships
- **HAS_COMPONENT**: Hierarchy
- **HAS_EXPRESSION**: Versioning
- **AGGREGATES**: Temporal aggregation
- **ISSUED_BY**: Authority link

## Example Usage

### Sample Document

```
NGHỊ ĐỊNH

VỀ CÔNG TÁC VĂN THƯ

Căn cứ Luật Tổ chức Chính phủ ngày 19 tháng 6 năm 2015;

Theo đề nghị của Bộ trưởng Bộ Nội vụ;

Chính phủ ban hành Nghị định về công tác văn thư.

Chương I
QUY ĐỊNH CHUNG

Điều 1. Phạm vi điều chỉnh

Nghị định này quy định về công tác văn thư.

Điều 2. Đối tượng áp dụng

1. Nghị định này áp dụng đối với cơ quan, tổ chức nhà nước.

2. Tổ chức chính trị căn cứ quy định của Nghị định này.
```

### Expected Output

**Parse Results**:
- Document Type: NGHI_DINH
- Components: 5 (1 Chương, 2 Điều, 2 Khoản)
- Definitions: 0
- Cross-references: 1 (Căn cứ)

**Cypher Output**:
- 1 VanBan node
- 5 ThanhPhanVanBan nodes
- 1 PhienBanVanBan node
- 5 CTV nodes
- 5 HAS_COMPONENT relationships
- 6 HAS_EXPRESSION relationships
- 5 AGGREGATES relationships

## Neo4j Import

After downloading the `.cypher` file:

```bash
# Method 1: Cypher Shell
cat import.cypher | cypher-shell -u neo4j -p password

# Method 2: Neo4j Browser
# Open http://localhost:7474
# Set parameter: :params {urn: 'urn:lex:vn:...'}
# Paste and run the script

# Method 3: Python Driver
from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
with open('import.cypher') as f:
    cypher = f.read()
with driver.session() as session:
    session.run(cypher, urn="urn:lex:vn:...")
```

## Troubleshooting

### Parser returns empty structure
- Check if document follows standard format
- Verify Chương/Điều keywords are present
- Try manual correction in JSON

### File upload fails
- Check file size (max 16MB)
- Verify file format (PDF/DOCX/HTML/TXT)
- Ensure dependencies installed (pdfplumber, python-docx)

### Cypher generation error
- Ensure parse step completed successfully
- Check for special characters in text
- Review parse JSON for accuracy

### Import into Neo4j fails
- Verify Neo4j is running
- Check URN parameter is set correctly
- Ensure constraints don't exist (or remove them)
- Review Cypher syntax for errors

## Limitations

- **Initial version only**: Creates BAN_DAU temporal version
- **No amendment processing**: Requires paired documents
- **Limited cross-references**: Only detects căn cứ
- **No internal references**: "Điều X Khoản Y" not linked

## Future Enhancements

- [ ] Amendment document processing
- [ ] Internal reference detection
- [ ] Batch processing multiple documents
- [ ] Graph visualization preview
- [ ] Export to JSON/XML
- [ ] OCR for scanned PDFs
- [ ] Multi-language support
- [ ] Advanced validation rules
- [ ] Comparison view between versions
- [ ] Integration with Neo4j directly

## Technical Stack

- **Backend**: Flask 3.0 (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Parser**: Custom Python implementation
- **Graph Model**: LRMoo (IFLA Library Reference Model)
- **Database Target**: Neo4j 4.x/5.x
- **File Processing**: pdfplumber, python-docx, BeautifulSoup

## License

Custom skill for Vietnamese legal document parsing.

## Credits

Based on the Vietnamese Legal Parser Skill implementing Structure-Aware Temporal Property Graph model following LRMoo ontology standards.

## Support

For issues or questions:
- Review the parser output carefully
- Check JSON validation summaries
- Verify input document format
- Test with sample documents first

---

**Version**: 1.0
**Last Updated**: 2024-11-09
**Author**: Claude AI Assistant
