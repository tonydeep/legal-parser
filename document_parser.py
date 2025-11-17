#!/usr/bin/env python3
"""
Vietnamese Legal Document Parser
Extracts structured information from Vietnamese legal documents in various formats.
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class DocumentMetadata:
    """Metadata extracted from legal document (15 doc types, 8 legislative actions)"""
    loai_van_ban: Optional[str] = None  # 15 types: HIEN_PHAP, LUAT, BO_LUAT, etc.
    so_hieu: Optional[str] = None
    tieu_de: Optional[str] = None
    ngay_ban_hanh: Optional[str] = None
    ngay_hieu_luc: Optional[str] = None
    co_quan_ban_hanh: Optional[str] = None
    nguoi_ky: Optional[str] = None
    hanh_dong_lap_phap: Optional[str] = None  # BAN_HANH, SUA_DOI, BO_SUNG, THAY_THE, BAI_BO, DINH_CHI, HUY_BO, HET_HIEU_LUC
    can_cu: List[str] = None

    def __post_init__(self):
        if self.can_cu is None:
            self.can_cu = []


@dataclass
class ComponentNode:
    """Represents a structural component (7-tier: Phan, Chuong, Muc, Dieu, Khoan, Diem, Tieu_Muc)"""
    loai: str  # PHAN, CHUONG, MUC, DIEU, KHOAN, DIEM, TIEU_MUC
    so_dinh_danh: str  # "1", "2", "a", "b"
    tieu_de: Optional[str] = None
    noi_dung: Optional[str] = None
    thu_tu: int = 0
    cap_bac: int = 1
    children: List['ComponentNode'] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


@dataclass
class CrossReference:
    """Cross-reference to another component (5 legal relationship types)"""
    source_component: str  # URN of source
    target_component: str  # URN of target
    loai_tham_chieu: str  # CAN_CU, HUONG_DAN_THI_HANH, QUY_DINH_CHI_TIET, KE_THUA, THAM_CHIEU
    noi_dung: str


@dataclass
class ParsedDocument:
    """Complete parsed document structure"""
    metadata: DocumentMetadata
    structure: List[ComponentNode]
    cross_references: List[CrossReference]
    dinh_nghia: Dict[str, str]  # Term definitions from Điều 3


class VietnameseLegalParser:
    """Parser for Vietnamese legal documents"""

    # Patterns for document types (15 types by legal hierarchy)
    DOC_TYPE_PATTERNS = {
        r'^HIẾN PHÁP': 'HIEN_PHAP',  # Constitution (Highest)
        r'^BỘ LUẬT': 'BO_LUAT',  # Legal Code
        r'^LUẬT': 'LUAT',  # Law
        r'^NGHỊ QUYẾT.*QUỐC HỘI': 'NGHI_QUYET_QH',  # National Assembly Resolution
        r'^PHÁP LỆNH': 'PHAP_LENH',  # Ordinance
        r'^NGHỊ QUYẾT.*ỦY BAN THƯỜNG VỤ QUỐC HỘI': 'NGHI_QUYET_UBTVQH',  # Standing Committee Resolution
        r'^NGHỊ QUYẾT.*UBTVQH': 'NGHI_QUYET_UBTVQH',  # Standing Committee Resolution (short form)
        r'^NGHỊ ĐỊNH': 'NGHI_DINH',  # Decree
        r'^THÔNG TƯ': 'THONG_TU',  # Circular
        r'^QUYẾT ĐỊNH.*THỦ TƯỚNG': 'QUYET_DINH_TTG',  # Prime Minister Decision
        r'^QUYẾT ĐỊNH.*BỘ TRƯỞNG': 'QUYET_DINH_BO_TRUONG',  # Minister Decision
        r'^QUYẾT ĐỊNH.*CHỦ TỊCH': 'QUYET_DINH_CHU_TICH',  # Chairman Decision
        r'^QUYẾT ĐỊNH': 'QUYET_DINH',  # General Decision
        r'^CHỈ THỊ': 'CHI_THI',  # Directive
        r'^NGHỊ QUYẾT': 'NGHI_QUYET',  # General Resolution
    }

    # Patterns for 8 legislative actions
    LEGISLATIVE_ACTION_PATTERNS = {
        r'ban hành': 'BAN_HANH',  # Issue/Promulgate
        r'sửa đổi': 'SUA_DOI',  # Amend
        r'bổ sung': 'BO_SUNG',  # Supplement
        r'thay thế': 'THAY_THE',  # Replace
        r'bãi bỏ': 'BAI_BO',  # Abolish
        r'đình chỉ': 'DINH_CHI',  # Suspend
        r'hủy bỏ': 'HUY_BO',  # Revoke
        r'hết hiệu lực': 'HET_HIEU_LUC',  # Expire
    }

    # Patterns for 5 legal relationship types
    RELATIONSHIP_PATTERNS = {
        r'Căn cứ': 'CAN_CU',  # Legal basis
        r'[Hh]ướng dẫn thi hành': 'HUONG_DAN_THI_HANH',  # Implementation guidance
        r'[Qq]uy định chi tiết': 'QUY_DINH_CHI_TIET',  # Detailed regulation
        r'[Kk]ế thừa': 'KE_THUA',  # Inheritance
        r'[Tt]ham chiếu': 'THAM_CHIEU',  # Reference
    }
    
    # Patterns for structural components (7-tier hierarchy)
    COMPONENT_PATTERNS = {
        'PHAN': r'^Phần\s+(thứ\s+)?([IVX]+|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)',
        'CHUONG': r'^Chương\s+([IVX]+|\d+)',
        'MUC': r'^Mục\s+(\d+)',
        'DIEU': r'^Điều\s+(\d+)\.',
        'KHOAN': r'^(\d+)\.',
        'DIEM': r'^([a-zđ])\)',
        'TIEU_MUC': r'^([a-zđ])\.',  # Sub-section (7th level, after DIEM)
    }
    
    # Date patterns
    DATE_PATTERNS = [
        r'ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})',
        r'(\d{1,2})/(\d{1,2})/(\d{4})',
        r'(\d{4})-(\d{2})-(\d{2})',
    ]
    
    def __init__(self):
        self.parsed_doc = None
        
    def parse_text(self, text: str) -> ParsedDocument:
        """Main parsing function"""
        lines = text.strip().split('\n')
        
        # Step 1: Extract metadata
        metadata = self._extract_metadata(lines)
        
        # Step 2: Parse structure
        structure = self._parse_structure(lines)
        
        # Step 3: Extract definitions (usually in Điều 3)
        definitions = self._extract_definitions(structure)
        
        # Step 4: Detect cross-references
        cross_refs = self._detect_cross_references(structure, metadata)
        
        self.parsed_doc = ParsedDocument(
            metadata=metadata,
            structure=structure,
            cross_references=cross_refs,
            dinh_nghia=definitions
        )
        
        return self.parsed_doc
    
    def _extract_metadata(self, lines: List[str]) -> DocumentMetadata:
        """Extract document metadata from header"""
        metadata = DocumentMetadata()

        # Detect document type from first line
        for pattern, doc_type in self.DOC_TYPE_PATTERNS.items():
            if re.match(pattern, lines[0].strip(), re.IGNORECASE):
                metadata.loai_van_ban = doc_type
                break

        # Extract title (usually second line or after document type)
        title_candidates = []
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            if line and not re.match(r'^(NGHỊ ĐỊNH|LUẬT|BỘ LUẬT|THÔNG TƯ|QUYẾT ĐỊNH|NGHỊ QUYẾT|PHÁP LỆNH|HIẾN PHÁP|CHỈ THỊ)', line):
                if len(line) > 10 and line.isupper():
                    title_candidates.append(line)

        if title_candidates:
            metadata.tieu_de = title_candidates[0]

        # Detect legislative action from title or content
        for i, line in enumerate(lines[:20]):
            for pattern, action in self.LEGISLATIVE_ACTION_PATTERNS.items():
                if re.search(pattern, line, re.IGNORECASE):
                    metadata.hanh_dong_lap_phap = action
                    break
            if metadata.hanh_dong_lap_phap:
                break

        # Default to BAN_HANH if no action detected
        if not metadata.hanh_dong_lap_phap:
            metadata.hanh_dong_lap_phap = 'BAN_HANH'
        
        # Extract legal basis (Căn cứ)
        can_cu_section = False
        for line in lines[:30]:
            line = line.strip()
            if re.match(r'^Căn cứ', line, re.IGNORECASE):
                can_cu_section = True
                # Extract the basis from this line
                basis = re.sub(r'^Căn cứ\s+', '', line, flags=re.IGNORECASE)
                if basis.endswith(';'):
                    basis = basis[:-1]
                if basis:
                    metadata.can_cu.append(basis)
            elif can_cu_section:
                if line.startswith('Theo đề nghị') or line.startswith('Chính phủ'):
                    can_cu_section = False
                elif line and line.endswith(';'):
                    metadata.can_cu.append(line[:-1])
        
        # Extract issuing authority
        for line in lines[:30]:
            if re.search(r'Chính phủ\s+ban hành', line, re.IGNORECASE):
                metadata.co_quan_ban_hanh = 'CHINH_PHU'
                break
            elif re.search(r'Quốc hội\s+ban hành', line, re.IGNORECASE):
                metadata.co_quan_ban_hanh = 'QUOC_HOI'
                break
        
        # Extract dates
        for line in lines[:30]:
            for pattern in self.DATE_PATTERNS:
                match = re.search(pattern, line)
                if match:
                    if len(match.groups()) == 3:
                        try:
                            # Format: day, month, year or year, month, day
                            groups = match.groups()
                            if int(groups[0]) > 1900:  # Year first
                                date_str = f"{groups[0]}-{groups[1]:0>2}-{groups[2]:0>2}"
                            else:  # Day first
                                date_str = f"{groups[2]}-{groups[1]:0>2}-{groups[0]:0>2}"
                            
                            if not metadata.ngay_ban_hanh:
                                metadata.ngay_ban_hanh = date_str
                        except:
                            pass
        
        return metadata
    
    def _parse_structure(self, lines: List[str]) -> List[ComponentNode]:
        """Parse hierarchical structure of document"""
        structure = []
        current_hierarchy = {}  # Track current node at each level
        
        # Find where actual content starts (after metadata)
        content_start = 0
        for i, line in enumerate(lines):
            if re.match(self.COMPONENT_PATTERNS['CHUONG'], line.strip(), re.IGNORECASE) or \
               re.match(self.COMPONENT_PATTERNS['DIEU'], line.strip(), re.IGNORECASE):
                content_start = i
                break
        
        i = content_start
        current_content = []
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Check for component headers
            component_found = False
            for comp_type, pattern in self.COMPONENT_PATTERNS.items():
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    # Save accumulated content to previous node
                    if current_content and current_hierarchy:
                        last_level = max(current_hierarchy.keys())
                        if current_hierarchy[last_level]:
                            current_hierarchy[last_level].noi_dung = '\n'.join(current_content).strip()
                    current_content = []
                    
                    # Create new component
                    so_dinh_danh = match.group(1)
                    cap_bac = self._get_level(comp_type)
                    
                    # Extract title (rest of the line after number)
                    title_part = line[match.end():].strip()
                    
                    node = ComponentNode(
                        loai=comp_type,
                        so_dinh_danh=so_dinh_danh,
                        tieu_de=title_part if title_part else None,
                        cap_bac=cap_bac
                    )
                    
                    # Add to structure
                    if cap_bac == 1:
                        structure.append(node)
                        current_hierarchy = {1: node}
                    else:
                        # Find parent
                        parent_level = cap_bac - 1
                        while parent_level > 0:
                            if parent_level in current_hierarchy:
                                parent = current_hierarchy[parent_level]
                                node.thu_tu = len(parent.children)
                                parent.children.append(node)
                                break
                            parent_level -= 1
                        
                        # Update hierarchy
                        current_hierarchy[cap_bac] = node
                        # Remove deeper levels
                        for level in list(current_hierarchy.keys()):
                            if level > cap_bac:
                                del current_hierarchy[level]
                    
                    component_found = True
                    break
            
            if not component_found:
                # Accumulate content
                current_content.append(line)
            
            i += 1
        
        # Save last accumulated content
        if current_content and current_hierarchy:
            last_level = max(current_hierarchy.keys())
            if current_hierarchy[last_level]:
                current_hierarchy[last_level].noi_dung = '\n'.join(current_content).strip()
        
        return structure
    
    def _get_level(self, component_type: str) -> int:
        """Get hierarchy level for component type (7 levels)"""
        levels = {
            'PHAN': 1,      # Part
            'CHUONG': 2,    # Chapter
            'MUC': 3,       # Section
            'DIEU': 4,      # Article
            'KHOAN': 5,     # Clause
            'DIEM': 6,      # Point
            'TIEU_MUC': 7,  # Sub-section
        }
        return levels.get(component_type, 1)
    
    def _extract_definitions(self, structure: List[ComponentNode]) -> Dict[str, str]:
        """Extract term definitions (usually from Điều 3)"""
        definitions = {}
        
        def find_definitions_recursive(nodes: List[ComponentNode]):
            for node in nodes:
                # Check if this is a definitions article
                if node.loai == 'DIEU' and node.tieu_de and \
                   'giải thích từ ngữ' in node.tieu_de.lower():
                    # Extract definitions from children (khoản)
                    for child in node.children:
                        if child.loai == 'KHOAN' and child.noi_dung:
                            # Pattern: "Term" là definition
                            match = re.match(r'^["\"]([^"\"]+)["\"]\\s+là\\s+(.+)', child.noi_dung)
                            if match:
                                term = match.group(1)
                                definition = match.group(2)
                                definitions[term] = definition
                
                # Recurse into children
                if node.children:
                    find_definitions_recursive(node.children)
        
        find_definitions_recursive(structure)
        return definitions
    
    def _detect_cross_references(self, structure: List[ComponentNode],
                                 metadata: DocumentMetadata) -> List[CrossReference]:
        """Detect cross-references to other components or documents (5 relationship types)"""
        cross_refs = []

        # Detect references in legal basis (CAN_CU)
        for basis in metadata.can_cu:
            cross_refs.append(CrossReference(
                source_component="DOCUMENT_ROOT",
                target_component=f"urn:lex:vn:unknown:{basis[:30]}",
                loai_tham_chieu="CAN_CU",
                noi_dung=basis
            ))

        # Detect all 5 relationship types within document content
        def detect_in_content(nodes: List[ComponentNode]):
            for node in nodes:
                if node.noi_dung:
                    # Check for each relationship pattern
                    for pattern, rel_type in self.RELATIONSHIP_PATTERNS.items():
                        matches = re.finditer(pattern + r'[^.;]*[.;]', node.noi_dung, re.IGNORECASE)
                        for match in matches:
                            ref_text = match.group(0)
                            # Extract referenced document/component
                            doc_ref_match = re.search(r'(Luật|Nghị định|Thông tư|Quyết định|Bộ luật|Pháp lệnh)\s+[^.;]{5,50}', ref_text, re.IGNORECASE)
                            if doc_ref_match:
                                target_urn = f"urn:lex:vn:ref:{doc_ref_match.group(0)[:30].replace(' ', '_')}"
                                source_urn = f"COMPONENT_{node.loai}_{node.so_dinh_danh}"
                                cross_refs.append(CrossReference(
                                    source_component=source_urn,
                                    target_component=target_urn,
                                    loai_tham_chieu=rel_type,
                                    noi_dung=ref_text.strip()
                                ))

                # Recurse into children
                if node.children:
                    detect_in_content(node.children)

        detect_in_content(structure)

        return cross_refs
    
    def to_json_summary(self) -> str:
        """Convert parsed document to JSON summary for validation"""
        if not self.parsed_doc:
            return json.dumps({"error": "No document parsed yet"}, indent=2, ensure_ascii=False)
        
        # Convert dataclasses to dict for JSON serialization
        def convert_node(node: ComponentNode) -> dict:
            node_dict = {
                'loai': node.loai,
                'so_dinh_danh': node.so_dinh_danh,
                'tieu_de': node.tieu_de,
                'noi_dung': node.noi_dung[:100] + '...' if node.noi_dung and len(node.noi_dung) > 100 else node.noi_dung,
                'cap_bac': node.cap_bac,
                'so_con': len(node.children)
            }
            if node.children:
                node_dict['children'] = [convert_node(child) for child in node.children]
            return node_dict
        
        summary = {
            'metadata': asdict(self.parsed_doc.metadata),
            'structure_summary': {
                'total_components': self._count_components(self.parsed_doc.structure),
                'top_level_count': len(self.parsed_doc.structure),
                'structure': [convert_node(node) for node in self.parsed_doc.structure]
            },
            'definitions_count': len(self.parsed_doc.dinh_nghia),
            'definitions': self.parsed_doc.dinh_nghia,
            'cross_references_count': len(self.parsed_doc.cross_references),
            'cross_references': [asdict(ref) for ref in self.parsed_doc.cross_references]
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
    
    if len(sys.argv) < 2:
        print("Usage: python document_parser.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    parser = VietnameseLegalParser()
    parsed = parser.parse_text(text)
    
    print(parser.to_json_summary())


if __name__ == '__main__':
    main()
