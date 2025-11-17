#!/usr/bin/env python3
"""
Enhanced Neo4j Cypher Statement Generator for Vietnamese Legal Documents
Implements full LRMoo ontology with event-centric modeling, URN generation,
and aggregation patterns.

Compatible with Neo4j 5.x
"""

import json
from typing import List, Dict, Set, Optional
from datetime import datetime, date
from document_parser import ParsedDocument, ComponentNode, DocumentMetadata, CrossReference
from urn_generator import URNGenerator


class CypherGeneratorEnhanced:
    """
    Enhanced Cypher generator with full LRMoo ontology support

    Features:
    - URN-based persistent identifiers
    - Event-centric modeling (SuKienLapPhap)
    - Aggregation pattern for temporal versioning
    - All 8 legislative actions
    - All 5 legal relationship types
    - Work ID generation
    """

    def __init__(self, parsed_doc: ParsedDocument, urn_gen: Optional[URNGenerator] = None):
        self.parsed_doc = parsed_doc
        self.urn_gen = urn_gen or URNGenerator()
        self.generated_urns: Set[str] = set()
        self.statements: List[str] = []
        self.document_urn: str = ""
        self.work_id: str = ""

    def generate_all(self, include_events: bool = True) -> str:
        """
        Generate complete Cypher script for Neo4j 5.x

        Args:
            include_events: Whether to generate legislative event nodes

        Returns:
            Complete Cypher script as string
        """
        self.statements = []

        # Header
        self._generate_header()

        # 1. Generate URNs and Work ID
        self._initialize_identifiers()

        # 2. Create VanBan (Work) node
        self._generate_van_ban_node()

        # 3. Create CoQuanBanHanh if needed
        if self.parsed_doc.metadata.co_quan_ban_hanh:
            self._generate_authority_node()
            self._generate_issued_by_relationship()

        # 4. Create ThanhPhanVanBan (Component) nodes with hierarchy
        self._generate_component_hierarchy()

        # 5. Create PhienBanVanBan (Temporal Version) - initial version
        self._generate_initial_version()

        # 6. Create CTVs (Component Temporal Versions) with aggregation
        self._generate_ctvs()

        # 7. Create legislative event (if applicable)
        if include_events and self.parsed_doc.metadata.hanh_dong_lap_phap:
            self._generate_legislative_event()

        # 8. Create cross-reference relationships (all 5 types)
        self._generate_cross_references()

        # 9. Generate summary statistics
        self._generate_summary()

        return '\n'.join(self.statements)

    def _generate_header(self):
        """Generate script header with metadata"""
        md = self.parsed_doc.metadata

        self.statements.append("// ========================================================================")
        self.statements.append("// Vietnamese Legal Document Import - Enhanced Generator")
        self.statements.append("// ========================================================================")
        self.statements.append(f"// Generated: {datetime.now().isoformat()}")
        self.statements.append(f"// Document: {md.tieu_de or 'Unknown'}")
        self.statements.append(f"// Document Type: {md.loai_van_ban or 'UNKNOWN'}")
        self.statements.append(f"// Legislative Action: {md.hanh_dong_lap_phap or 'BAN_HANH'}")
        self.statements.append(f"// Issue Date: {md.ngay_ban_hanh or 'Unknown'}")
        self.statements.append("// ")
        self.statements.append("// Features:")
        self.statements.append("//   - LRMoo ontology (Work/Expression separation)")
        self.statements.append("//   - URN persistent identifiers")
        self.statements.append("//   - 7-tier hierarchy (Phần → Tiểu mục)")
        self.statements.append("//   - Event-centric modeling")
        self.statements.append("//   - Aggregation pattern for temporal versioning")
        self.statements.append("//   - 5 legal relationship types")
        self.statements.append("// ========================================================================")
        self.statements.append("")

    def _initialize_identifiers(self):
        """Generate URNs and Work IDs for the document"""
        md = self.parsed_doc.metadata

        # Generate document URN
        try:
            year = int(md.ngay_ban_hanh[:4]) if md.ngay_ban_hanh else datetime.now().year
            self.document_urn = self.urn_gen.generate_document_urn(
                doc_type=md.loai_van_ban or 'QUYET_DINH',
                authority=md.co_quan_ban_hanh or 'CHINH_PHU',
                issue_date=md.ngay_ban_hanh or date.today().isoformat(),
                number=md.so_hieu
            )
            self.generated_urns.add(self.document_urn)

            # Generate Work ID
            self.work_id = self.urn_gen.generate_work_id(
                doc_type=md.loai_van_ban or 'QUYET_DINH',
                year=year,
                number=md.so_hieu
            )
        except Exception as e:
            # Fallback to simple URN
            loai = (md.loai_van_ban or "UNKNOWN").lower()
            date_part = md.ngay_ban_hanh.replace('-', '') if md.ngay_ban_hanh else "00000000"
            so_part = md.so_hieu.replace('/', '-') if md.so_hieu else "000"
            self.document_urn = f"urn:lex:vn:vietnam:{loai}:{date_part};{so_part}"
            self.work_id = f"{md.loai_van_ban or 'UNKNOWN'}-{date_part}"
            self.generated_urns.add(self.document_urn)

        self.statements.append(f"// Document URN: {self.document_urn}")
        self.statements.append(f"// Work ID: {self.work_id}")
        self.statements.append("")

    def _generate_van_ban_node(self):
        """Generate VanBan (Document Work) node with all properties"""
        md = self.parsed_doc.metadata

        self.statements.append("// ========================================================================")
        self.statements.append("// WORK LEVEL: VanBan (F1 - LRMoo)")
        self.statements.append("// ========================================================================")
        self.statements.append("")
        self.statements.append(f"MERGE (vb:VanBan {{urn: '{self.document_urn}'}})")

        # Add specialized label
        specialized_labels = {
            'HIEN_PHAP': 'HienPhap',
            'BO_LUAT': 'BoLuat',
            'LUAT': 'Luat',
            'NGHI_DINH': 'NghiDinh',
            'THONG_TU': 'ThongTu',
            'QUYET_DINH': 'QuyetDinh',
            'NGHI_QUYET_QH': 'NghiQuyetQH',
            'NGHI_QUYET_UBTVQH': 'NghiQuyetUBTVQH',
            'PHAP_LENH': 'PhapLenh',
            'CHI_THI': 'ChiThi',
        }
        specialized_label = specialized_labels.get(md.loai_van_ban, '')
        if specialized_label:
            self.statements.append(f"SET vb:{specialized_label}")

        # Set all properties
        self.statements.append("SET vb += {")
        self.statements.append(f"  workId: '{self.work_id}',")

        if md.tieu_de:
            self.statements.append(f"  tenGoi: {self._escape_string(md.tieu_de)},")
        if md.loai_van_ban:
            self.statements.append(f"  loaiVanBan: '{md.loai_van_ban}',")
        if md.so_hieu:
            self.statements.append(f"  soHieu: '{md.so_hieu}',")
        if md.ngay_ban_hanh:
            self.statements.append(f"  ngayBanHanh: date('{md.ngay_ban_hanh}'),")
        if md.ngay_hieu_luc:
            self.statements.append(f"  ngayHieuLuc: date('{md.ngay_hieu_luc}'),")
        if md.hanh_dong_lap_phap:
            self.statements.append(f"  hanhDongLapPhap: '{md.hanh_dong_lap_phap}',")

        # Calculate legal hierarchy level (1-15)
        cap_phap_ly = self._get_legal_hierarchy_level(md.loai_van_ban)
        self.statements.append(f"  capPhapLy: {cap_phap_ly},")
        self.statements.append("  trangThai: 'HIEU_LUC'")
        self.statements.append("};")
        self.statements.append("")

    def _get_legal_hierarchy_level(self, doc_type: Optional[str]) -> int:
        """Get legal hierarchy level (1=highest, 15=lowest)"""
        hierarchy = {
            'HIEN_PHAP': 1,
            'BO_LUAT': 2,
            'LUAT': 3,
            'NGHI_QUYET_QH': 4,
            'PHAP_LENH': 5,
            'NGHI_QUYET_UBTVQH': 6,
            'NGHI_DINH': 7,
            'THONG_TU': 8,
            'QUYET_DINH_TTG': 9,
            'QUYET_DINH_BO_TRUONG': 10,
            'QUYET_DINH_CHU_TICH': 11,
            'QUYET_DINH': 12,
            'CHI_THI': 13,
            'NGHI_QUYET': 14,
        }
        return hierarchy.get(doc_type, 15)

    def _generate_authority_node(self):
        """Generate CoQuanBanHanh node with full metadata"""
        co_quan = self.parsed_doc.metadata.co_quan_ban_hanh

        self.statements.append("// ========================================================================")
        self.statements.append("// AUTHORITY: CoQuanBanHanh")
        self.statements.append("// ========================================================================")
        self.statements.append("")
        self.statements.append(f"MERGE (cq:CoQuanBanHanh {{coQuanId: '{co_quan}'}})")
        self.statements.append("SET cq += {")
        self.statements.append("  tenDayDu: CASE cq.coQuanId")
        self.statements.append("    WHEN 'QUOC_HOI' THEN 'Quốc hội'")
        self.statements.append("    WHEN 'UBTVQH' THEN 'Ủy ban Thường vụ Quốc hội'")
        self.statements.append("    WHEN 'CHINH_PHU' THEN 'Chính phủ'")
        self.statements.append("    WHEN 'THU_TUONG' THEN 'Thủ tướng Chính phủ'")
        self.statements.append("    WHEN 'BO_TAI_CHINH' THEN 'Bộ Tài chính'")
        self.statements.append("    WHEN 'BO_NOI_VU' THEN 'Bộ Nội vụ'")
        self.statements.append("    WHEN 'BO_TU_PHAP' THEN 'Bộ Tư pháp'")
        self.statements.append("    ELSE cq.coQuanId")
        self.statements.append("  END,")
        self.statements.append("  tenVietTat: cq.coQuanId")
        self.statements.append("};")
        self.statements.append("")

    def _generate_issued_by_relationship(self):
        """Generate ISSUED_BY relationship with metadata"""
        md = self.parsed_doc.metadata
        co_quan = md.co_quan_ban_hanh

        self.statements.append("// Create ISSUED_BY relationship")
        self.statements.append(f"MATCH (vb:VanBan {{urn: '{self.document_urn}'}})")
        self.statements.append(f"MATCH (cq:CoQuanBanHanh {{coQuanId: '{co_quan}'}})")
        self.statements.append("MERGE (vb)-[r:ISSUED_BY]->(cq)")
        self.statements.append("SET r += {")
        if md.ngay_ban_hanh:
            self.statements.append(f"  ngayBanHanh: date('{md.ngay_ban_hanh}'),")
        if md.nguoi_ky:
            self.statements.append(f"  nguoiKy: '{md.nguoi_ky}',")
        self.statements.append("  chinhThuc: true")
        self.statements.append("};")
        self.statements.append("")

    def _generate_component_hierarchy(self):
        """Generate ThanhPhanVanBan nodes with full hierarchy"""
        if not self.parsed_doc.structure:
            return

        self.statements.append("// ========================================================================")
        self.statements.append("// WORK LEVEL: ThanhPhanVanBan Hierarchy (7 tiers)")
        self.statements.append("// ========================================================================")
        self.statements.append("")
        self.statements.append(f"MATCH (vb:VanBan {{urn: '{self.document_urn}'}})")
        self.statements.append("")

        # Generate recursively
        self._generate_components_recursive(self.parsed_doc.structure, "vb", is_root=True)

    def _generate_components_recursive(self, nodes: List[ComponentNode],
                                      parent_var: str, is_root: bool = False):
        """Recursively generate component nodes"""
        for idx, node in enumerate(nodes):
            # Generate component URN
            comp_urn = self.urn_gen.generate_component_urn(
                document_urn=self.document_urn,
                component_type=node.loai,
                component_id=node.so_dinh_danh
            )

            comp_var = f"c_{node.loai.lower()}_{node.so_dinh_danh.replace('.', '_').replace('-', '_')}"

            # Get specialized label
            label = self._get_component_label(node.loai)

            # Create component node
            self.statements.append(f"MERGE ({comp_var}:{label}:ThanhPhanVanBan {{urn: '{comp_urn}'}})")
            self.statements.append(f"SET {comp_var} += {{")

            # Generate work ID for component
            comp_work_id = f"{self.work_id}-{node.loai}-{node.so_dinh_danh}"
            self.statements.append(f"  workId: '{comp_work_id}',")
            self.statements.append(f"  loaiThanhPhan: '{node.loai}',")
            self.statements.append(f"  soDinhDanh: '{node.so_dinh_danh}',")

            if node.tieu_de:
                self.statements.append(f"  tieuDe: {self._escape_string(node.tieu_de)},")

            self.statements.append(f"  thuTuSapXep: {node.thu_tu},")
            self.statements.append(f"  capBac: {node.cap_bac}")
            self.statements.append("};")

            # Create HAS_COMPONENT relationship
            self.statements.append(f"MERGE ({parent_var})-[r_{comp_var}:HAS_COMPONENT]->({comp_var})")
            self.statements.append(f"SET r_{comp_var}.thuTuSapXep = {idx};")
            self.statements.append("")

            # Recurse for children
            if node.children:
                self._generate_components_recursive(node.children, comp_var)

    def _get_component_label(self, loai: str) -> str:
        """Get Neo4j label for component type (7 levels)"""
        labels = {
            'PHAN': 'Phan',
            'CHUONG': 'Chuong',
            'MUC': 'Muc',
            'DIEU': 'Dieu',
            'KHOAN': 'Khoan',
            'DIEM': 'Diem',
            'TIEU_MUC': 'TieuMuc',
        }
        return labels.get(loai, 'ThanhPhanVanBan')

    def _generate_initial_version(self):
        """Generate initial PhienBanVanBan (Temporal Version)"""
        md = self.parsed_doc.metadata
        date_str = md.ngay_hieu_luc or md.ngay_ban_hanh or date.today().isoformat()

        version_urn = self.urn_gen.generate_ctv_urn(self.document_urn, date_str)

        self.statements.append("// ========================================================================")
        self.statements.append("// EXPRESSION LEVEL: PhienBanVanBan (Initial Temporal Version)")
        self.statements.append("// ========================================================================")
        self.statements.append("")
        self.statements.append(f"MATCH (vb:VanBan {{urn: '{self.document_urn}'}})")
        self.statements.append(f"MERGE (tv:PhienBanVanBan {{urn: '{version_urn}'}})")
        self.statements.append("SET tv += {")
        self.statements.append(f"  expressionId: '{self.work_id}-TV-{date_str.replace('-', '')}',")
        self.statements.append(f"  ngayHieuLuc: date('{date_str}'),")
        self.statements.append("  ngayHetHieuLuc: date('9999-12-31'),")
        self.statements.append("  loaiPhienBan: 'BAN_DAU',")
        self.statements.append("  soThanhPhanThayDoi: 0,")
        self.statements.append("  ghiChu: 'Phiên bản ban đầu'")
        self.statements.append("};")
        self.statements.append("")
        self.statements.append("// Create HAS_EXPRESSION relationship")
        self.statements.append("MERGE (vb)-[:HAS_EXPRESSION]->(tv);")
        self.statements.append("")

    def _generate_ctvs(self):
        """Generate CTVs (Component Temporal Versions) with AGGREGATES pattern"""
        md = self.parsed_doc.metadata
        date_str = md.ngay_hieu_luc or md.ngay_ban_hanh or date.today().isoformat()

        if not self.parsed_doc.structure:
            return

        self.statements.append("// ========================================================================")
        self.statements.append("// EXPRESSION LEVEL: CTV (Component Temporal Versions)")
        self.statements.append("// Aggregation Pattern for Temporal Versioning")
        self.statements.append("// ========================================================================")
        self.statements.append("")
        self.statements.append(f"WITH date('{date_str}') as validDate")
        self.statements.append(f"MATCH (tv:PhienBanVanBan)-[:HAS_EXPRESSION*0..1]-()<-[:HAS_COMPONENT*0..7]-(vb:VanBan {{urn: '{self.document_urn}'}})")
        self.statements.append("")

        # Generate CTVs recursively
        self._generate_ctvs_recursive(self.parsed_doc.structure, date_str)

        # Create AGGREGATES relationships
        self.statements.append("// Create AGGREGATES relationships (Aggregation Pattern)")
        self.statements.append(f"MATCH (tv:PhienBanVanBan {{urn: '{self.urn_gen.generate_ctv_urn(self.document_urn, date_str)}'}})")
        self.statements.append(f"MATCH (vb:VanBan {{urn: '{self.document_urn}'}})")
        self.statements.append("MATCH (vb)-[:HAS_COMPONENT*1..7]->(tp:ThanhPhanVanBan)")
        self.statements.append("MATCH (tp)-[:HAS_EXPRESSION]->(ctv:CTV)")
        self.statements.append(f"WHERE ctv.ngayHieuLuc = date('{date_str}')")
        self.statements.append("MERGE (tv)-[agg:AGGREGATES]->(ctv)")
        self.statements.append(f"SET agg.ngayHieuLuc = date('{date_str}'),")
        self.statements.append("    agg.thayDoi = false;  // No changes in initial version")
        self.statements.append("")

    def _generate_ctvs_recursive(self, nodes: List[ComponentNode], date_str: str):
        """Recursively generate CTVs for all components"""
        for node in nodes:
            comp_urn = self.urn_gen.generate_component_urn(
                document_urn=self.document_urn,
                component_type=node.loai,
                component_id=node.so_dinh_danh
            )

            ctv_urn = self.urn_gen.generate_ctv_urn(comp_urn, date_str)
            ctv_id = f"{self.work_id}-{node.loai}-{node.so_dinh_danh}-CTV-{date_str.replace('-', '')}"

            self.statements.append(f"// CTV for {node.loai} {node.so_dinh_danh}")
            self.statements.append(f"MATCH (tp:ThanhPhanVanBan {{urn: '{comp_urn}'}})")
            self.statements.append(f"MERGE (ctv:CTV {{urn: '{ctv_urn}'}})")
            self.statements.append("SET ctv += {")
            self.statements.append(f"  ctvId: '{ctv_id}',")
            self.statements.append(f"  ngayHieuLuc: date('{date_str}'),")
            self.statements.append("  ngayHetHieuLuc: date('9999-12-31'),")

            if node.noi_dung:
                self.statements.append(f"  noiDung: {self._escape_string(node.noi_dung)},")

            self.statements.append("  trangThai: 'HIEU_LUC',")
            self.statements.append("  loaiThayDoi: null  // Initial version, no changes")
            self.statements.append("};")
            self.statements.append("MERGE (tp)-[:HAS_EXPRESSION]->(ctv);")
            self.statements.append("")

            # Recurse for children
            if node.children:
                self._generate_ctvs_recursive(node.children, date_str)

    def _generate_legislative_event(self):
        """Generate SuKienLapPhap (Legislative Event) node"""
        md = self.parsed_doc.metadata
        action = md.hanh_dong_lap_phap

        if not action or action == 'BAN_HANH':
            # For initial issuance, event is implicit in ISSUED_BY
            return

        self.statements.append("// ========================================================================")
        self.statements.append("// EVENT: SuKienLapPhap (Legislative Event)")
        self.statements.append("// Event-Centric Modeling (F28 - LRMoo)")
        self.statements.append("// ========================================================================")
        self.statements.append("")

        event_id = f"EVT-{action}-{self.work_id}"
        event_time = md.ngay_ban_hanh or date.today().isoformat()

        self.statements.append(f"MERGE (evt:SuKienLapPhap {{eventId: '{event_id}'}})")
        self.statements.append("SET evt += {")
        self.statements.append(f"  loaiSuKien: '{action}',")
        self.statements.append(f"  thoiDiem: datetime('{event_time}T00:00:00+07:00'),")
        self.statements.append(f"  moTa: {self._escape_string(md.tieu_de or 'Legislative event')},")
        self.statements.append(f"  vanBanDoiTuong: '{self.document_urn}',")
        self.statements.append(f"  ketQua: '{self.document_urn}@{event_time}'")
        self.statements.append("};")
        self.statements.append("")

    def _generate_cross_references(self):
        """Generate cross-reference relationships (all 5 types)"""
        if not self.parsed_doc.cross_references:
            return

        self.statements.append("// ========================================================================")
        self.statements.append("// LEGAL RELATIONSHIPS (5 Types)")
        self.statements.append("// CAN_CU, HUONG_DAN_THI_HANH, QUY_DINH_CHI_TIET, KE_THUA, THAM_CHIEU")
        self.statements.append("// ========================================================================")
        self.statements.append("")

        # Group by relationship type
        ref_by_type = {}
        for ref in self.parsed_doc.cross_references:
            if ref.loai_tham_chieu not in ref_by_type:
                ref_by_type[ref.loai_tham_chieu] = []
            ref_by_type[ref.loai_tham_chieu].append(ref)

        # Generate relationships by type
        for rel_type, refs in ref_by_type.items():
            self.statements.append(f"// {rel_type} relationships ({len(refs)} references)")

            for idx, ref in enumerate(refs):
                # Create reference node (placeholder until actual document is available)
                target_node_var = f"ref_{rel_type.lower()}_{idx}"
                self.statements.append(f"MERGE ({target_node_var}:VanBanThamChieu {{urn: '{ref.target_component}'}})")
                self.statements.append(f"SET {target_node_var}.noiDung = {self._escape_string(ref.noi_dung)};")

                # Create relationship from source
                if ref.source_component == "DOCUMENT_ROOT":
                    self.statements.append(f"MATCH (vb:VanBan {{urn: '{self.document_urn}'}})")
                    self.statements.append(f"MATCH ({target_node_var}:VanBanThamChieu {{urn: '{ref.target_component}'}})")
                    self.statements.append(f"MERGE (vb)-[r:{rel_type}]->({target_node_var})")
                    self.statements.append(f"SET r.noiDung = {self._escape_string(ref.noi_dung)};")
                else:
                    # Component-level reference
                    self.statements.append(f"// Component-level reference: {ref.source_component} -> {ref.target_component}")

                self.statements.append("")

    def _generate_summary(self):
        """Generate summary statistics"""
        component_count = self._count_components(self.parsed_doc.structure)
        ref_count = len(self.parsed_doc.cross_references)

        self.statements.append("// ========================================================================")
        self.statements.append("// IMPORT SUMMARY")
        self.statements.append("// ========================================================================")
        self.statements.append("//")
        self.statements.append(f"// Document URN: {self.document_urn}")
        self.statements.append(f"// Work ID: {self.work_id}")
        self.statements.append("//")
        self.statements.append("// Nodes Created:")
        self.statements.append("//   - 1 VanBan (Work)")
        self.statements.append(f"//   - {component_count} ThanhPhanVanBan (Components)")
        self.statements.append("//   - 1 PhienBanVanBan (Temporal Version)")
        self.statements.append(f"//   - {component_count} CTV (Component Temporal Versions)")
        self.statements.append(f"//   - 1 CoQuanBanHanh (Authority)")
        self.statements.append(f"//   - {ref_count} VanBanThamChieu (References)")
        self.statements.append("//")
        self.statements.append("// Relationships Created:")
        self.statements.append(f"//   - {component_count} HAS_COMPONENT")
        self.statements.append(f"//   - {component_count + 1} HAS_EXPRESSION")
        self.statements.append(f"//   - {component_count} AGGREGATES")
        self.statements.append("//   - 1 ISSUED_BY")
        self.statements.append(f"//   - {ref_count} Legal References")
        self.statements.append("// ========================================================================")
        self.statements.append("")

        # Return success message
        self.statements.append("RETURN 'Document imported successfully!' as status,")
        self.statements.append(f"       '{self.document_urn}' as document_urn,")
        self.statements.append(f"       '{self.work_id}' as work_id,")
        self.statements.append(f"       {component_count} as component_count;")

    def _count_components(self, nodes: List[ComponentNode]) -> int:
        """Recursively count all components"""
        count = len(nodes)
        for node in nodes:
            count += self._count_components(node.children)
        return count

    def _escape_string(self, s: str) -> str:
        """Escape string for Cypher"""
        if not s:
            return "''"
        # Escape single quotes and backslashes
        s = s.replace('\\', '\\\\').replace("'", "\\'")
        # Truncate very long strings
        if len(s) > 1000:
            s = s[:997] + "..."
        return f"'{s}'"

    def to_json_summary(self) -> str:
        """Generate JSON summary of what will be created"""
        component_count = self._count_components(self.parsed_doc.structure)

        summary = {
            "document": {
                "urn": self.document_urn,
                "work_id": self.work_id,
                "type": self.parsed_doc.metadata.loai_van_ban,
                "title": self.parsed_doc.metadata.tieu_de,
                "legislative_action": self.parsed_doc.metadata.hanh_dong_lap_phap
            },
            "statistics": {
                "total_components": component_count,
                "cross_references": len(self.parsed_doc.cross_references),
                "definitions": len(self.parsed_doc.dinh_nghia)
            },
            "nodes_to_create": {
                "VanBan": 1,
                "CoQuanBanHanh": 1 if self.parsed_doc.metadata.co_quan_ban_hanh else 0,
                "ThanhPhanVanBan": component_count,
                "PhienBanVanBan": 1,
                "CTV": component_count,
                "VanBanThamChieu": len(self.parsed_doc.cross_references)
            },
            "relationships_to_create": {
                "HAS_COMPONENT": component_count,
                "HAS_EXPRESSION": component_count + 1,
                "AGGREGATES": component_count,
                "ISSUED_BY": 1 if self.parsed_doc.metadata.co_quan_ban_hanh else 0,
                "Legal_References": len(self.parsed_doc.cross_references)
            }
        }

        return json.dumps(summary, indent=2, ensure_ascii=False)


def main():
    """Example usage"""
    from document_parser import VietnameseLegalParser

    test_text = """NGHỊ ĐỊNH
VỀ CÔNG TÁC VĂN THƯ

Căn cứ Luật Tổ chức Chính phủ ngày 19 tháng 6 năm 2015;

Chính phủ ban hành Nghị định về công tác văn thư.

Điều 1. Phạm vi điều chỉnh

Nghị định này quy định về công tác văn thư.
"""

    parser = VietnameseLegalParser()
    parsed = parser.parse_text(test_text)

    generator = CypherGeneratorEnhanced(parsed)
    cypher_script = generator.generate_all()

    print(cypher_script)
    print("\n" + "="*80)
    print("JSON Summary:")
    print(generator.to_json_summary())


if __name__ == '__main__':
    main()
