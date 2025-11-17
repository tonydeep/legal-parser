// ============================================================================
// Vietnamese Legal Knowledge Graph - Neo4j 5.x Schema Initialization
// ============================================================================
// This script creates the complete schema for the Vietnamese Legal Document
// Property Knowledge Graph following LRMoo ontology standards.
//
// Compatible with: Neo4j 5.x (requires Enterprise for some constraints)
// Execution: Run via cypher-shell or Neo4j Browser
// ============================================================================

// ============================================================================
// SECTION 1: CLEANUP (Optional - for development only)
// ============================================================================
// Uncomment below to drop all constraints and indexes (WARNING: Destructive!)

// CALL apoc.schema.assert({}, {});  // Requires APOC plugin


// ============================================================================
// SECTION 2: UNIQUENESS CONSTRAINTS
// ============================================================================

// Work Level - VanBan (Legal Document)
CREATE CONSTRAINT unique_van_ban_urn IF NOT EXISTS
FOR (vb:VanBan) REQUIRE vb.urn IS UNIQUE;

// Work Level - ThanhPhanVanBan (Component)
CREATE CONSTRAINT unique_thanh_phan_urn IF NOT EXISTS
FOR (tp:ThanhPhanVanBan) REQUIRE tp.urn IS UNIQUE;

// Expression Level - PhienBanVanBan (Temporal Version)
CREATE CONSTRAINT unique_phien_ban_urn IF NOT EXISTS
FOR (tv:PhienBanVanBan) REQUIRE tv.urn IS UNIQUE;

// Expression Level - CTV (Component Temporal Version)
CREATE CONSTRAINT unique_ctv_urn IF NOT EXISTS
FOR (ctv:CTV) REQUIRE ctv.urn IS UNIQUE;

// Expression Level - CLV (Component Language Version)
CREATE CONSTRAINT unique_clv_urn IF NOT EXISTS
FOR (clv:CLV) REQUIRE clv.urn IS UNIQUE;

// Authority - CoQuanBanHanh
CREATE CONSTRAINT unique_co_quan_id IF NOT EXISTS
FOR (cq:CoQuanBanHanh) REQUIRE cq.coQuanId IS UNIQUE;

// Event - SuKienLapPhap
CREATE CONSTRAINT unique_su_kien_id IF NOT EXISTS
FOR (sk:SuKienLapPhap) REQUIRE sk.eventId IS UNIQUE;

// Classification - ChuDePhaply
CREATE CONSTRAINT unique_chu_de_id IF NOT EXISTS
FOR (cd:ChuDePhaply) REQUIRE cd.chuDeId IS UNIQUE;

// Classification - LinhVucPhapLuat
CREATE CONSTRAINT unique_linh_vuc_id IF NOT EXISTS
FOR (lv:LinhVucPhapLuat) REQUIRE lv.linhVucId IS UNIQUE;


// ============================================================================
// SECTION 3: NODE KEY CONSTRAINTS (Enterprise Edition)
// ============================================================================
// These ensure combination of properties uniquely identifies nodes

// VanBan identity by type + number + date
CREATE CONSTRAINT van_ban_identity IF NOT EXISTS
FOR (vb:VanBan)
REQUIRE (vb.loaiVanBan, vb.soHieu, vb.ngayBanHanh) IS NODE KEY;

// CTV identity by component + date
CREATE CONSTRAINT ctv_identity IF NOT EXISTS
FOR (ctv:CTV)
REQUIRE (ctv.ctvId, ctv.ngayHieuLuc) IS NODE KEY;


// ============================================================================
// SECTION 4: EXISTENCE CONSTRAINTS (Enterprise Edition)
// ============================================================================
// Ensure critical properties are always present

// VanBan required fields
CREATE CONSTRAINT van_ban_loai_exists IF NOT EXISTS
FOR (vb:VanBan) REQUIRE vb.loaiVanBan IS NOT NULL;

CREATE CONSTRAINT van_ban_work_id_exists IF NOT EXISTS
FOR (vb:VanBan) REQUIRE vb.workId IS NOT NULL;

// PhienBanVanBan required fields
CREATE CONSTRAINT phien_ban_ngay_hieu_luc_exists IF NOT EXISTS
FOR (tv:PhienBanVanBan) REQUIRE tv.ngayHieuLuc IS NOT NULL;

CREATE CONSTRAINT phien_ban_ngay_het_hieu_luc_exists IF NOT EXISTS
FOR (tv:PhienBanVanBan) REQUIRE tv.ngayHetHieuLuc IS NOT NULL;

// CTV required fields
CREATE CONSTRAINT ctv_ngay_hieu_luc_exists IF NOT EXISTS
FOR (ctv:CTV) REQUIRE ctv.ngayHieuLuc IS NOT NULL;

CREATE CONSTRAINT ctv_ngay_het_hieu_luc_exists IF NOT EXISTS
FOR (ctv:CTV) REQUIRE ctv.ngayHetHieuLuc IS NOT NULL;

CREATE CONSTRAINT ctv_trang_thai_exists IF NOT EXISTS
FOR (ctv:CTV) REQUIRE ctv.trangThai IS NOT NULL;


// ============================================================================
// SECTION 5: PROPERTY TYPE CONSTRAINTS (Neo4j 5.9+)
// ============================================================================
// Enforce data types for properties

// Date type constraints
CREATE CONSTRAINT van_ban_ngay_ban_hanh_type IF NOT EXISTS
FOR (vb:VanBan) REQUIRE vb.ngayBanHanh IS :: DATE;

CREATE CONSTRAINT van_ban_ngay_hieu_luc_type IF NOT EXISTS
FOR (vb:VanBan) REQUIRE vb.ngayHieuLuc IS :: DATE;

CREATE CONSTRAINT phien_ban_dates_type IF NOT EXISTS
FOR (tv:PhienBanVanBan) REQUIRE tv.ngayHieuLuc IS :: DATE;

CREATE CONSTRAINT ctv_dates_type IF NOT EXISTS
FOR (ctv:CTV) REQUIRE ctv.ngayHieuLuc IS :: DATE;

// Integer type constraints
CREATE CONSTRAINT thanh_phan_cap_bac_type IF NOT EXISTS
FOR (tp:ThanhPhanVanBan) REQUIRE tp.capBac IS :: INTEGER;

CREATE CONSTRAINT thanh_phan_thu_tu_type IF NOT EXISTS
FOR (tp:ThanhPhanVanBan) REQUIRE tp.thuTuSapXep IS :: INTEGER;


// ============================================================================
// SECTION 6: RANGE INDEXES
// ============================================================================
// For efficient filtering and range queries

// VanBan indexes
CREATE INDEX van_ban_work_id IF NOT EXISTS
FOR (vb:VanBan) ON (vb.workId);

CREATE INDEX van_ban_so_hieu IF NOT EXISTS
FOR (vb:VanBan) ON (vb.soHieu);

CREATE INDEX van_ban_loai_van_ban IF NOT EXISTS
FOR (vb:VanBan) ON (vb.loaiVanBan);

CREATE INDEX van_ban_ngay_ban_hanh IF NOT EXISTS
FOR (vb:VanBan) ON (vb.ngayBanHanh);

CREATE INDEX van_ban_trang_thai IF NOT EXISTS
FOR (vb:VanBan) ON (vb.trangThai);

// ThanhPhanVanBan indexes
CREATE INDEX thanh_phan_work_id IF NOT EXISTS
FOR (tp:ThanhPhanVanBan) ON (tp.workId);

CREATE INDEX thanh_phan_loai IF NOT EXISTS
FOR (tp:ThanhPhanVanBan) ON (tp.loaiThanhPhan);

CREATE INDEX thanh_phan_cap_bac IF NOT EXISTS
FOR (tp:ThanhPhanVanBan) ON (tp.capBac);

// PhienBanVanBan indexes
CREATE INDEX phien_ban_expression_id IF NOT EXISTS
FOR (tv:PhienBanVanBan) ON (tv.expressionId);

CREATE INDEX phien_ban_ngay_hieu_luc IF NOT EXISTS
FOR (tv:PhienBanVanBan) ON (tv.ngayHieuLuc);

CREATE INDEX phien_ban_loai IF NOT EXISTS
FOR (tv:PhienBanVanBan) ON (tv.loaiPhienBan);

// CTV indexes - Critical for temporal queries
CREATE INDEX ctv_ctv_id IF NOT EXISTS
FOR (ctv:CTV) ON (ctv.ctvId);

CREATE INDEX ctv_ngay_hieu_luc IF NOT EXISTS
FOR (ctv:CTV) ON (ctv.ngayHieuLuc);

CREATE INDEX ctv_ngay_het_hieu_luc IF NOT EXISTS
FOR (ctv:CTV) ON (ctv.ngayHetHieuLuc);

CREATE INDEX ctv_trang_thai IF NOT EXISTS
FOR (ctv:CTV) ON (ctv.trangThai);

CREATE INDEX ctv_loai_thay_doi IF NOT EXISTS
FOR (ctv:CTV) ON (ctv.loaiThayDoi);

// SuKienLapPhap indexes
CREATE INDEX su_kien_loai IF NOT EXISTS
FOR (sk:SuKienLapPhap) ON (sk.loaiSuKien);

CREATE INDEX su_kien_thoi_diem IF NOT EXISTS
FOR (sk:SuKienLapPhap) ON (sk.thoiDiem);

// CoQuanBanHanh indexes
CREATE INDEX co_quan_ten_viet_tat IF NOT EXISTS
FOR (cq:CoQuanBanHanh) ON (cq.tenVietTat);


// ============================================================================
// SECTION 7: COMPOSITE INDEXES
// ============================================================================
// For multi-property queries (more efficient than single indexes)

// VanBan composite: type + date
CREATE INDEX van_ban_type_date_composite IF NOT EXISTS
FOR (vb:VanBan) ON (vb.loaiVanBan, vb.ngayBanHanh);

// VanBan composite: type + status
CREATE INDEX van_ban_type_status_composite IF NOT EXISTS
FOR (vb:VanBan) ON (vb.loaiVanBan, vb.trangThai);

// CTV composite: temporal validity (CRITICAL for point-in-time queries)
CREATE INDEX ctv_temporal_composite IF NOT EXISTS
FOR (ctv:CTV) ON (ctv.ngayHieuLuc, ctv.ngayHetHieuLuc, ctv.trangThai);

// ThanhPhanVanBan composite: hierarchy
CREATE INDEX thanh_phan_hierarchy_composite IF NOT EXISTS
FOR (tp:ThanhPhanVanBan) ON (tp.capBac, tp.thuTuSapXep);

// PhienBanVanBan composite: version lookup
CREATE INDEX phien_ban_version_composite IF NOT EXISTS
FOR (tv:PhienBanVanBan) ON (tv.loaiPhienBan, tv.ngayHieuLuc);


// ============================================================================
// SECTION 8: TEXT INDEXES
// ============================================================================
// For case-insensitive string matching

CREATE TEXT INDEX van_ban_ten_goi IF NOT EXISTS
FOR (vb:VanBan) ON (vb.tenGoi);

CREATE TEXT INDEX thanh_phan_tieu_de IF NOT EXISTS
FOR (tp:ThanhPhanVanBan) ON (tp.tieuDe);

CREATE TEXT INDEX co_quan_ten_day_du IF NOT EXISTS
FOR (cq:CoQuanBanHanh) ON (cq.tenDayDu);


// ============================================================================
// SECTION 9: FULL-TEXT SEARCH INDEXES
// ============================================================================
// For Vietnamese legal content search

// Content search across multiple node types
CREATE FULLTEXT INDEX noi_dung_van_ban IF NOT EXISTS
FOR (n:VanBan|ThanhPhanVanBan|CTV|CLV)
ON EACH [n.tenGoi, n.tieuDe, n.noiDung, n.noiDungDayDu]
OPTIONS {
  analyzer: "standard-no-stop-words",
  eventually_consistent: true
};

// Definition search
CREATE FULLTEXT INDEX dinh_nghia_search IF NOT EXISTS
FOR (n:VanBan|ThanhPhanVanBan)
ON EACH [n.tenGoi, n.tieuDe]
OPTIONS {
  analyzer: "keyword",
  eventually_consistent: false
};


// ============================================================================
// SECTION 10: POINT INDEX (for future geospatial features)
// ============================================================================
// If authority locations are added later

// CREATE POINT INDEX co_quan_location IF NOT EXISTS
// FOR (cq:CoQuanBanHanh) ON (cq.viTri);


// ============================================================================
// SECTION 11: VERIFICATION QUERIES
// ============================================================================
// Run these to verify schema creation

// List all constraints
// SHOW CONSTRAINTS;

// List all indexes
// CALL db.indexes() YIELD name, state, type, populationProgress
// RETURN name, state, type, populationProgress
// ORDER BY name;

// Check index usage statistics
// CALL db.stats.retrieve('GRAPH COUNTS');


// ============================================================================
// SECTION 12: PERFORMANCE TUNING RECOMMENDATIONS
// ============================================================================

/*
 * For production deployment, configure Neo4j memory settings:
 *
 * In neo4j.conf:
 *
 * # Heap Size
 * server.memory.heap.initial_size=8g
 * server.memory.heap.max_size=8g
 *
 * # Page Cache (for data storage)
 * server.memory.pagecache.size=16g
 *
 * # Transaction State
 * db.tx_state.memory_allocation=ON_HEAP
 *
 * # Query Memory
 * db.memory.transaction.total.max=2g
 *
 * # For large imports
 * dbms.memory.transaction.total.max=4g
 */


// ============================================================================
// SECTION 13: SAMPLE DATA VALIDATION QUERIES
// ============================================================================

/*
 * After importing data, validate with these queries:
 *
 * // Check temporal integrity
 * MATCH (ctv:CTV)
 * WHERE ctv.ngayHieuLuc > ctv.ngayHetHieuLuc
 * RETURN count(ctv) as invalid_temporal_ranges;
 *
 * // Check orphaned components
 * MATCH (tp:ThanhPhanVanBan)
 * WHERE NOT (tp)<-[:HAS_COMPONENT]-()
 * RETURN count(tp) as orphaned_components;
 *
 * // Check CTVs without aggregation
 * MATCH (ctv:CTV)
 * WHERE NOT (:PhienBanVanBan)-[:AGGREGATES]->(ctv)
 * RETURN count(ctv) as unaggregated_ctvs;
 *
 * // Check for missing URNs
 * MATCH (n)
 * WHERE n:VanBan OR n:ThanhPhanVanBan OR n:CTV OR n:PhienBanVanBan
 *   AND n.urn IS NULL
 * RETURN labels(n) as nodeType, count(n) as missing_urn_count;
 */


// ============================================================================
// SCHEMA INITIALIZATION COMPLETE
// ============================================================================

// Return confirmation message
RETURN "Vietnamese Legal Knowledge Graph schema initialized successfully!" as status,
       "Neo4j 5.x compatible" as version,
       "Run SHOW CONSTRAINTS and CALL db.indexes() to verify" as next_step;
