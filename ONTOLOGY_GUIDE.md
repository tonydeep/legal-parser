# Vietnamese Legal Knowledge Graph - Complete Implementation Guide

## Overview

This repository implements a complete **Property Knowledge Graph** for Vietnamese legal documents following **LRMoo (Library Reference Model - object-oriented)** standards with **Component Temporal Versioning** and **event-centric modeling**.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPLETE SYSTEM ARCHITECTURE              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PARSING LAYER                                               │
│  ├─ document_parser.py      (15 types, 7-tier, 8 actions)  │
│  └─ urn_generator.py        (URN generation & validation)   │
│                                                              │
│  GENERATION LAYER                                            │
│  ├─ cypher_generator.py             (Basic generator)       │
│  └─ cypher_generator_enhanced.py    (Full ontology)         │
│                                                              │
│  SCHEMA LAYER                                                │
│  └─ schema_init.cypher      (Constraints & Indexes)         │
│                                                              │
│  QUERY LAYER                                                 │
│  └─ query_templates.py      (Production queries)            │
│                                                              │
│  DATABASE LAYER                                              │
│  └─ Neo4j 5.x              (Property Graph DB)              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. URN Generator (`urn_generator.py`)

**Purpose**: Generate and parse URNs following LexML Vietnam standards

**URN Format**:
```
urn:lex:vn:{jurisdiction}:{type}:{date};{number}[@version][~language][!component]
```

**Examples**:
```python
from urn_generator import URNGenerator

urn_gen = URNGenerator()

# Document URN
doc_urn = urn_gen.generate_document_urn(
    doc_type='HIEN_PHAP',
    authority='QUOC_HOI',
    issue_date='2013-11-28',
    number='71/QH13'
)
# Result: urn:lex:vn:quochoi:hienphap:2013-11-28;71-QH13

# Component URN
comp_urn = urn_gen.generate_component_urn(
    document_urn=doc_urn,
    component_type='DIEU',
    component_id='6'
)
# Result: urn:lex:vn:quochoi:hienphap:2013-11-28;71-QH13!dieu6

# CTV URN
ctv_urn = urn_gen.generate_ctv_urn(
    component_urn=comp_urn,
    effective_date='2020-01-01'
)
# Result: urn:lex:vn:quochoi:hienphap:2013-11-28;71-QH13!dieu6@2020-01-01
```

**Features**:
- Vietnamese character transliteration
- URL-safe encoding
- Parse and validate URNs
- Work ID generation

### 2. Schema Initialization (`schema_init.cypher`)

**Purpose**: Complete Neo4j 5.x schema setup

**Run**:
```bash
# Via cypher-shell
cat schema_init.cypher | cypher-shell -u neo4j -p password

# Via Neo4j Browser
# Copy and paste the entire file
```

**What it creates**:
- **Uniqueness constraints** (9 types)
- **Node key constraints** (2 types) - Enterprise
- **Existence constraints** (7 types) - Enterprise
- **Property type constraints** (6 types) - Neo4j 5.9+
- **Range indexes** (20+ indexes)
- **Composite indexes** (5 critical indexes)
- **Text indexes** (3 indexes)
- **Full-text indexes** (2 indexes)

**Critical Indexes**:
```cypher
// Point-in-time queries
CREATE INDEX ctv_temporal_composite
FOR (ctv:CTV) ON (ctv.ngayHieuLuc, ctv.ngayHetHieuLuc, ctv.trangThai);

// Hierarchy traversal
CREATE INDEX thanh_phan_hierarchy_composite
FOR (tp:ThanhPhanVanBan) ON (tp.capBac, tp.thuTuSapXep);
```

### 3. Enhanced Cypher Generator (`cypher_generator_enhanced.py`)

**Purpose**: Generate complete Cypher scripts with full ontology support

**Features**:
- ✅ URN-based persistent identifiers
- ✅ Event-centric modeling (SuKienLapPhap)
- ✅ Aggregation pattern for temporal versioning
- ✅ Specialized node labels (HienPhap, Luat, etc.)
- ✅ All 5 legal relationship types
- ✅ Legal hierarchy levels (capPhapLy: 1-15)
- ✅ Comprehensive metadata

**Usage**:
```python
from document_parser import VietnameseLegalParser
from cypher_generator_enhanced import CypherGeneratorEnhanced

# Parse document
parser = VietnameseLegalParser()
parsed = parser.parse_text(document_text)

# Generate Cypher
generator = CypherGeneratorEnhanced(parsed)
cypher_script = generator.generate_all(include_events=True)

# Save to file
with open('import.cypher', 'w', encoding='utf-8') as f:
    f.write(cypher_script)

# Get summary
summary = generator.to_json_summary()
print(summary)
```

**Output Structure**:
```
// Header with metadata
// Work Level: VanBan + specialized labels
// Authority: CoQuanBanHanh
// Component Hierarchy: 7-tier structure
// Expression Level: PhienBanVanBan (temporal version)
// CTVs with AGGREGATES pattern
// Legislative Events (if applicable)
// Legal Relationships (5 types)
// Summary statistics
```

### 4. Query Templates (`query_templates.py`)

**Purpose**: Production-ready Cypher queries for common use cases

**Available Queries**:

#### Point-in-Time Retrieval
```python
from query_templates import LegalQueryTemplates

templates = LegalQueryTemplates()

query, params = templates.point_in_time_article(
    work_id='HIENPHAP-2013',
    article_number='6',
    target_date='2020-01-01'
)
# Execute with neo4j driver
```

#### Document Reconstruction
```python
query, params = templates.reconstruct_document(
    work_id='HIENPHAP-2013',
    target_date='2022-06-15',
    max_depth=7
)
```

#### Version History
```python
query, params = templates.document_version_history(
    work_id='BO-LUAT-DAN-SU-2015',
    component_id='DIEU-3'
)
```

#### Changes in Period
```python
query, params = templates.changes_in_period(
    work_id='LUAT-DOANH-NGHIEP-2020',
    start_date='2020-01-01',
    end_date='2023-12-31'
)
```

#### Legal Basis Chain
```python
query, params = templates.legal_basis_chain(
    work_id='NGHI-DINH-01-2021',
    max_depth=5
)
```

#### Cross-Document Impact
```python
query, params = templates.cross_document_impact(
    amending_doc_number='01/2021/NĐ-CP',
    amending_doc_type='NGHI_DINH'
)
```

#### Full-Text Search
```python
query, params = templates.full_text_search(
    search_term='công tác văn thư',
    doc_type='THONG_TU',
    limit=20
)
```

## Complete Workflow

### Step 1: Setup Neo4j
```bash
# Install Neo4j 5.x
# Start Neo4j
# Initialize schema
cat schema_init.cypher | cypher-shell -u neo4j -p password
```

### Step 2: Parse Document
```python
from document_parser import VietnameseLegalParser

text = """
NGHỊ ĐỊNH
VỀ CÔNG TÁC VĂN THƯ
...
"""

parser = VietnameseLegalParser()
parsed = parser.parse_text(text)
```

### Step 3: Generate Cypher
```python
from cypher_generator_enhanced import CypherGeneratorEnhanced
from urn_generator import URNGenerator

urn_gen = URNGenerator()
generator = CypherGeneratorEnhanced(parsed, urn_gen)

# Generate script
cypher = generator.generate_all(include_events=True)

# Save
with open('import_nghi_dinh.cypher', 'w', encoding='utf-8') as f:
    f.write(cypher)
```

### Step 4: Import to Neo4j
```bash
# Method 1: Cypher-shell with URN parameter
cypher-shell -u neo4j -p password \
  --param "urn => 'urn:lex:vn:chinhphu:nghidinh:2021-01-05;01-2021-nd-cp'" \
  < import_nghi_dinh.cypher

# Method 2: Python driver
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

with open('import_nghi_dinh.cypher') as f:
    cypher = f.read()

with driver.session() as session:
    result = session.run(
        cypher,
        urn="urn:lex:vn:chinhphu:nghidinh:2021-01-05;01-2021-nd-cp"
    )
    print(result.single())
```

### Step 5: Query
```python
from query_templates import LegalQueryTemplates
from neo4j import GraphDatabase

templates = LegalQueryTemplates()
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

# Point-in-time query
query, params = templates.point_in_time_article(
    work_id='NGHI-DINH-2021-01',
    article_number='1',
    target_date='2021-03-01'
)

with driver.session() as session:
    result = session.run(query, **params)
    for record in result:
        print(f"Title: {record['tieuDe']}")
        print(f"Content: {record['noiDung']}")
```

## Graph Schema

### Node Types

| Label | Purpose | Properties |
|-------|---------|------------|
| `VanBan` | Legal Work (abstract) | urn, workId, tenGoi, loaiVanBan, soHieu, ngayBanHanh, capPhapLy |
| `ThanhPhanVanBan` | Component Work | urn, workId, loaiThanhPhan, soDinhDanh, tieuDe, capBac |
| `PhienBanVanBan` | Temporal Version | urn, expressionId, ngayHieuLuc, ngayHetHieuLuc, loaiPhienBan |
| `CTV` | Component Temporal Version | urn, ctvId, ngayHieuLuc, ngayHetHieuLuc, noiDung, trangThai |
| `CoQuanBanHanh` | Issuing Authority | coQuanId, tenDayDu, tenVietTat, capDo |
| `SuKienLapPhap` | Legislative Event | eventId, loaiSuKien, thoiDiem, moTa |

### Specialized Labels

- `HienPhap`, `BoLuat`, `Luat`, `NghiDinh`, `ThongTu`, `QuyetDinh`
- `Phan`, `Chuong`, `Muc`, `Dieu`, `Khoan`, `Diem`, `TieuMuc`

### Relationship Types

| Type | Purpose | Properties |
|------|---------|------------|
| `HAS_COMPONENT` | Hierarchy | thuTuSapXep |
| `HAS_EXPRESSION` | Work→Expression | loaiPhienBan, ngayHieuLuc |
| `AGGREGATES` | Aggregation pattern | ngayHieuLuc, thayDoi |
| `IS_DERIVATIVE_OF` | Version chain | loaiThayDoi, soThayDoi |
| `ISSUED_BY` | Authority link | ngayBanHanh, nguoiKy |
| `PRODUCED_BY` | Event causation | thoiDiem |
| `CAN_CU` | Legal basis | thuTu, trichDan |
| `HUONG_DAN_THI_HANH` | Implementation guidance | phamVi, noiDung |
| `QUY_DINH_CHI_TIET` | Detailed regulation | dieuKhoanDuocGiao |
| `KE_THUA` | Inheritance | |
| `THAM_CHIEU` | General reference | loaiThamChieu |

## Performance Tuning

### Memory Configuration (neo4j.conf)
```properties
# Heap Size
server.memory.heap.initial_size=8g
server.memory.heap.max_size=8g

# Page Cache
server.memory.pagecache.size=16g

# Query Memory
db.memory.transaction.total.max=2g
```

### Query Optimization

**Use Composite Indexes**:
```cypher
// Instead of separate filters
MATCH (ctv:CTV)
WHERE ctv.ngayHieuLuc <= date('2024-01-01')
  AND ctv.ngayHetHieuLuc >= date('2024-01-01')
  AND ctv.trangThai = 'HIEU_LUC'

// Composite index covers all three
CREATE INDEX ctv_temporal_composite
FOR (ctv:CTV) ON (ctv.ngayHieuLuc, ctv.ngayHetHieuLuc, ctv.trangThai);
```

**Use Parameters**:
```python
# Good - uses parameter
session.run(query, urn=document_urn)

# Bad - concatenates
session.run(f"MATCH (vb:VanBan {{urn: '{document_urn}'}})")
```

## Validation Queries

### Check Temporal Integrity
```cypher
MATCH (ctv:CTV)
WHERE ctv.ngayHieuLuc > ctv.ngayHetHieuLuc
RETURN count(ctv) as invalid_ranges;
// Should return 0
```

### Check Orphaned Components
```cypher
MATCH (tp:ThanhPhanVanBan)
WHERE NOT (tp)<-[:HAS_COMPONENT]-()
RETURN count(tp) as orphaned;
// Should return 0
```

### Check Missing URNs
```cypher
MATCH (n)
WHERE (n:VanBan OR n:CTV) AND n.urn IS NULL
RETURN count(n) as missing_urns;
// Should return 0
```

## Examples

See `test_demo.py` for comprehensive examples.

Run tests:
```bash
python test_demo.py
```

## References

### Standards
- LRMoo v1.0 (IFLA Library Reference Model)
- LexML URN Scheme
- OASIS LegalDocML

### Papers
- Hudson de Martim (2025). "Modeling the Diachronic Evolution of Legal Norms"
- Colombo et al. (2024). "Modelling Legislative Systems into Property Graphs"

### Similar Projects
- UK Lex Graph (820K+ nodes)
- Italian ILPG (400K+ nodes)
- Brazilian LexML

## License

Custom skill for Vietnamese legal document parsing.

## Version

**3.0** - Complete LRMoo Ontology Implementation
- Full URN support
- Event-centric modeling
- Enhanced Cypher generation
- Production query templates
- Neo4j 5.x schema

---

**For Questions**: Review this guide, check the ontology design document, or examine the test suite.
