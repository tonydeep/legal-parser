#!/usr/bin/env python3
"""
Neo4j Cypher Statement Generator for Vietnamese Legal Documents
Converts parsed document structure into Neo4j Cypher statements.
"""

import json
from typing import List, Dict, Set
from datetime import datetime
from document_parser import ParsedDocument, ComponentNode, DocumentMetadata, CrossReference


class CypherGenerator:
    """Generates Cypher statements for Neo4j import"""
    
    def __init__(self, parsed_doc: ParsedDocument):
        self.parsed_doc = parsed_doc
        self.generated_urns: Set[str] = set()
        self.statements: List[str] = []
        
    def generate_all(self) -> str:
        """Generate complete Cypher script"""
        self.statements = []
        
        # Header
        self.statements.append("// Vietnamese Legal Document Import")
        self.statements.append(f"// Generated: {datetime.now().isoformat()}")
        self.statements.append("// Document: " + (self.parsed_doc.metadata.tieu_de or "Unknown"))
        self.statements.append("")
        
        # 1. Create VanBan (Work) node
        self._generate_van_ban_node()
        
        # 2. Create CoQuanBanHanh if needed
        if self.parsed_doc.metadata.co_quan_ban_hanh:
            self._generate_authority_node()
        
        # 3. Create ThanhPhanVanBan (Component) nodes
        self._generate_component_hierarchy()
        
        # 4. Create PhienBanVanBan (Temporal Version) - initial version
        self._generate_initial_version()
        
        # 5. Create CTVs (Component Temporal Versions)
        self._generate_ctvs()
        
        # 6. Create cross-reference relationships
        self._generate_cross_references()
        
        return '\n'.join(self.statements)
    
    def _generate_van_ban_node(self):
        """Generate VanBan (Document Work) node"""
        md = self.parsed_doc.metadata
        
        # Generate URN
        loai = md.loai_van_ban or "UNKNOWN"
        date_part = md.ngay_ban_hanh.replace('-', '') if md.ngay_ban_hanh else "00000000"
        so_part = md.so_hieu.replace('/', '-') if md.so_hieu else "000"
        
        urn = f"urn:lex:vn:quochoi:{loai.lower()}:{date_part};{so_part}"
        work_id = f"{loai}-{date_part}"
        
        self.generated_urns.add(urn)
        
        self.statements.append("// Create VanBan (Document Work)")
        self.statements.append("MERGE (vb:VanBan {urn: $urn})")
        self.statements.append("SET vb += {")
        self.statements.append(f"  workId: '{work_id}',")
        if md.tieu_de:
            self.statements.append(f"  tenGoi: {self._escape_string(md.tieu_de)},")
        if md.loai_van_ban:
            self.statements.append(f"  loaiVanBan: '{md.loai_van_ban}',")
        if md.so_hieu:
            self.statements.append(f"  soHieu: '{md.so_hieu}',")
        if md.co_quan_ban_hanh:
            self.statements.append(f"  coQuanBanHanh: '{md.co_quan_ban_hanh}',")
        if md.ngay_ban_hanh:
            self.statements.append(f"  ngayBanHanh: date('{md.ngay_ban_hanh}'),")
        if md.ngay_hieu_luc:
            self.statements.append(f"  ngayHieuLuc: date('{md.ngay_hieu_luc}'),")
        self.statements.append("  trangThai: 'HIEU_LUC'")
        self.statements.append("};")
        self.statements.append("")
        
        return urn
    
    def _generate_authority_node(self):
        """Generate CoQuanBanHanh node"""
        co_quan = self.parsed_doc.metadata.co_quan_ban_hanh
        
        self.statements.append("// Create CoQuanBanHanh (Issuing Authority)")
        self.statements.append(f"MERGE (cq:CoQuanBanHanh {{coQuanId: '{co_quan}'}})")
        self.statements.append("SET cq.tenDayDu = CASE cq.coQuanId")
        self.statements.append("  WHEN 'CHINH_PHU' THEN 'Chính phủ'")
        self.statements.append("  WHEN 'QUOC_HOI' THEN 'Quốc hội'")
        self.statements.append("  ELSE cq.coQuanId")
        self.statements.append("END;")
        self.statements.append("")
        
        # Create ISSUED_BY relationship
        self.statements.append("// Link VanBan to Authority")
        self.statements.append("MATCH (vb:VanBan {urn: $urn})")
        self.statements.append(f"MATCH (cq:CoQuanBanHanh {{coQuanId: '{co_quan}'}})")
        self.statements.append("MERGE (vb)-[r:ISSUED_BY]->(cq)")
        if self.parsed_doc.metadata.ngay_ban_hanh:
            self.statements.append(f"SET r.ngayBanHanh = date('{self.parsed_doc.metadata.ngay_ban_hanh}');")
        self.statements.append("")
    
    def _generate_component_hierarchy(self):
        """Generate ThanhPhanVanBan nodes with hierarchy"""
        self.statements.append("// Create Component Hierarchy")
        self.statements.append("MATCH (vb:VanBan {urn: $urn})")
        self.statements.append("")
        
        # Track parent URN for relationships
        self._generate_components_recursive(self.parsed_doc.structure, "vb", is_root=True)
    
    def _generate_components_recursive(self, nodes: List[ComponentNode], 
                                      parent_var: str, is_root: bool = False):
        """Recursively generate component nodes"""
        for idx, node in enumerate(nodes):
            # Generate URN for component
            comp_urn = self._generate_component_urn(node)
            comp_var = f"c_{node.loai.lower()}_{node.so_dinh_danh.replace('.', '_')}"
            
            # Create component node
            label = self._get_component_label(node.loai)
            self.statements.append(f"MERGE ({comp_var}:{label}:ThanhPhanVanBan {{urn: '{comp_urn}'}})")
            self.statements.append(f"SET {comp_var} += {{")
            self.statements.append(f"  workId: '{comp_urn.split(':')[-1]}',")
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
    
    def _generate_initial_version(self):
        """Generate initial PhienBanVanBan (Temporal Version)"""
        md = self.parsed_doc.metadata
        date = md.ngay_ban_hanh or md.ngay_hieu_luc or datetime.now().strftime('%Y-%m-%d')
        
        self.statements.append("// Create Initial Temporal Version")
        self.statements.append("MATCH (vb:VanBan {urn: $urn})")
        self.statements.append(f"MERGE (tv:PhienBanVanBan {{urn: $urn + '@{date}'}})")
        self.statements.append("SET tv += {")
        self.statements.append(f"  expressionId: vb.workId + '-TV-{date.replace('-', '')}',")
        self.statements.append(f"  ngayHieuLuc: date('{date}'),")
        self.statements.append("  ngayHetHieuLuc: date('9999-12-31'),")
        self.statements.append("  loaiPhienBan: 'BAN_DAU',")
        self.statements.append("  soThanhPhanThayDoi: 0")
        self.statements.append("};")
        self.statements.append("")
        self.statements.append("MERGE (vb)-[:HAS_EXPRESSION]->(tv);")
        self.statements.append("")
    
    def _generate_ctvs(self):
        """Generate CTVs (Component Temporal Versions)"""
        md = self.parsed_doc.metadata
        date = md.ngay_ban_hanh or md.ngay_hieu_luc or datetime.now().strftime('%Y-%m-%d')
        
        self.statements.append("// Create Component Temporal Versions (CTVs)")
        self.statements.append(f"WITH date('{date}') as validDate")
        self.statements.append("MATCH (vb:VanBan {urn: $urn})")
        self.statements.append(f"MATCH (tv:PhienBanVanBan {{urn: $urn + '@{date}'}})")
        self.statements.append("")
        
        self._generate_ctvs_recursive(self.parsed_doc.structure, date)
        
        self.statements.append("// Create AGGREGATES relationships from TV to CTVs")
        self.statements.append("MATCH (vb:VanBan {urn: $urn})")
        self.statements.append(f"MATCH (tv:PhienBanVanBan {{urn: $urn + '@{date}'}})")
        self.statements.append("MATCH (vb)-[:HAS_COMPONENT*]->(tp:ThanhPhanVanBan)")
        self.statements.append("MATCH (tp)-[:HAS_EXPRESSION]->(ctv:CTV)")
        self.statements.append(f"WHERE ctv.ngayHieuLuc = date('{date}')")
        self.statements.append("MERGE (tv)-[agg:AGGREGATES]->(ctv)")
        self.statements.append(f"SET agg.ngayHieuLuc = date('{date}'),")
        self.statements.append("    agg.thayDoi = false;")
        self.statements.append("")
    
    def _generate_ctvs_recursive(self, nodes: List[ComponentNode], date: str):
        """Recursively generate CTVs for all components"""
        for node in nodes:
            comp_urn = self._generate_component_urn(node)
            ctv_urn = f"{comp_urn}@{date}"
            
            self.statements.append(f"// CTV for {node.loai} {node.so_dinh_danh}")
            self.statements.append(f"MATCH (tp:ThanhPhanVanBan {{urn: '{comp_urn}'}})")
            self.statements.append(f"MERGE (ctv:CTV {{urn: '{ctv_urn}'}})")
            self.statements.append("SET ctv += {")
            self.statements.append(f"  ctvId: tp.workId + '-CTV-{date.replace('-', '')}',")
            self.statements.append(f"  ngayHieuLuc: date('{date}'),")
            self.statements.append("  ngayHetHieuLuc: date('9999-12-31'),")
            if node.noi_dung:
                self.statements.append(f"  noiDung: {self._escape_string(node.noi_dung)},")
            self.statements.append("  trangThai: 'HIEU_LUC',")
            self.statements.append("  loaiThayDoi: null")
            self.statements.append("};")
            self.statements.append("MERGE (tp)-[:HAS_EXPRESSION]->(ctv);")
            self.statements.append("")
            
            # Recurse for children
            if node.children:
                self._generate_ctvs_recursive(node.children, date)
    
    def _generate_cross_references(self):
        """Generate cross-reference relationships"""
        if not self.parsed_doc.cross_references:
            return
        
        self.statements.append("// Create Cross-References")
        self.statements.append("")
        
        for ref in self.parsed_doc.cross_references:
            if ref.loai_tham_chieu == "CAN_CU":
                # Create CAN_CU relationship
                self.statements.append("// Legal basis reference")
                self.statements.append("MATCH (vb:VanBan {urn: $urn})")
                self.statements.append(f"// Target: {ref.noi_dung}")
                self.statements.append("// TODO: Create proper target node when document is available")
                self.statements.append("")
    
    def _generate_component_urn(self, node: ComponentNode) -> str:
        """Generate URN for component"""
        base_urn = list(self.generated_urns)[0] if self.generated_urns else "urn:lex:vn:unknown"
        comp_id = f"{node.loai.lower()}{node.so_dinh_danh.replace('.', '_')}"
        return f"{base_urn}!{comp_id}"
    
    def _get_component_label(self, loai: str) -> str:
        """Get Neo4j label for component type"""
        labels = {
            'PHAN': 'Phan',
            'CHUONG': 'Chuong',
            'MUC': 'Muc',
            'DIEU': 'Dieu',
            'KHOAN': 'Khoan',
            'DIEM': 'Diem',
        }
        return labels.get(loai, 'ThanhPhanVanBan')
    
    def _escape_string(self, s: str) -> str:
        """Escape string for Cypher"""
        if not s:
            return "''"
        # Escape single quotes and backslashes
        s = s.replace('\\', '\\\\').replace("'", "\\'")
        # Truncate very long strings
        if len(s) > 500:
            s = s[:497] + "..."
        return f"'{s}'"
    
    def to_json_summary(self) -> str:
        """Generate JSON summary of what will be created"""
        summary = {
            "document": {
                "urn": list(self.generated_urns)[0] if self.generated_urns else None,
                "type": self.parsed_doc.metadata.loai_van_ban,
                "title": self.parsed_doc.metadata.tieu_de
            },
            "statistics": {
                "total_statements": len(self.statements),
                "components_count": self._count_components(self.parsed_doc.structure),
                "cross_references": len(self.parsed_doc.cross_references)
            },
            "nodes_to_create": {
                "VanBan": 1,
                "CoQuanBanHanh": 1 if self.parsed_doc.metadata.co_quan_ban_hanh else 0,
                "ThanhPhanVanBan": self._count_components(self.parsed_doc.structure),
                "PhienBanVanBan": 1,
                "CTV": self._count_components(self.parsed_doc.structure)
            },
            "relationships_to_create": {
                "HAS_COMPONENT": self._count_components(self.parsed_doc.structure),
                "HAS_EXPRESSION": 1 + self._count_components(self.parsed_doc.structure),
                "AGGREGATES": self._count_components(self.parsed_doc.structure),
                "ISSUED_BY": 1 if self.parsed_doc.metadata.co_quan_ban_hanh else 0
            }
        }
        
        return json.dumps(summary, indent=2, ensure_ascii=False)
    
    def _count_components(self, nodes: List[ComponentNode]) -> int:
        """Recursively count all components"""
        count = len(nodes)
        for node in nodes:
            count += self._count_components(node.children)
        return count


def main():
    """Example usage"""
    import sys
    from document_parser import VietnameseLegalParser
    
    if len(sys.argv) < 2:
        print("Usage: python cypher_generator.py <parsed_json>")
        sys.exit(1)
    
    # Load parsed document
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        # This would need proper deserialization
        pass


if __name__ == '__main__':
    main()
