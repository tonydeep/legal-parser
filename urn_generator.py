#!/usr/bin/env python3
"""
URN Generator for Vietnamese Legal Documents
Implements the URN scheme: urn:lex:vn:{jurisdiction}:{type}:{date};{number}[@version][~language][!component]
"""

import re
from datetime import date, datetime
from typing import Optional
from urllib.parse import quote


class URNGenerator:
    """Generate and parse URNs for Vietnamese legal documents following LexML standards"""

    # Mapping document types to URN types
    DOC_TYPE_TO_URN = {
        'HIEN_PHAP': 'hienphap',
        'BO_LUAT': 'boluật',
        'LUAT': 'luat',
        'NGHI_QUYET_QH': 'nghiquyet.qh',
        'PHAP_LENH': 'phaplenh',
        'NGHI_QUYET_UBTVQH': 'nghiquyet.ubtvqh',
        'NGHI_DINH': 'nghidinh',
        'THONG_TU': 'thongtu',
        'QUYET_DINH_TTG': 'quyetdinh.ttg',
        'QUYET_DINH_BO_TRUONG': 'quyetdinh.botruong',
        'QUYET_DINH_CHU_TICH': 'quyetdinh.chutich',
        'QUYET_DINH': 'quyetdinh',
        'CHI_THI': 'chithi',
        'NGHI_QUYET': 'nghiquyet',
    }

    # Mapping authority to jurisdiction
    AUTHORITY_TO_JURISDICTION = {
        'QUOC_HOI': 'quochoi',
        'UBTVQH': 'ubtvqh',
        'CHINH_PHU': 'chinhphu',
        'THU_TUONG': 'thutruong',
        'BO_TAI_CHINH': 'bo.taichinh',
        'BO_NOI_VU': 'bo.noiva',
        'BO_TU_PHAP': 'bo.tuphap',
        'BO_CONG_THUONG': 'bo.conghuong',
        'BO_Y_TE': 'bo.yte',
    }

    def __init__(self):
        self.base_namespace = "urn:lex:vn"

    def generate_document_urn(
        self,
        doc_type: str,
        authority: str,
        issue_date: str,  # YYYY-MM-DD format
        number: Optional[str] = None,
        version_date: Optional[str] = None,
        language: Optional[str] = None
    ) -> str:
        """
        Generate URN for a legal document

        Example:
            urn:lex:vn:quochoi:luat:2013-11-28;71
            urn:lex:vn:chinhphu:nghidinh:2021-01-05;01-2021-nd-cp@2021-03-01
        """
        # Validate inputs
        if doc_type not in self.DOC_TYPE_TO_URN:
            raise ValueError(f"Unknown document type: {doc_type}")

        # Parse date
        try:
            parsed_date = datetime.strptime(issue_date, '%Y-%m-%d')
            date_part = parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Invalid date format: {issue_date}. Expected YYYY-MM-DD")

        # Get jurisdiction
        jurisdiction = self.AUTHORITY_TO_JURISDICTION.get(authority, 'vietnam')

        # Get type
        urn_type = self.DOC_TYPE_TO_URN[doc_type]

        # Build number part
        if number:
            # Clean and URL-encode number
            number_clean = self._clean_number(number)
            number_part = f";{number_clean}"
        else:
            number_part = ""

        # Build base URN
        urn = f"{self.base_namespace}:{jurisdiction}:{urn_type}:{date_part}{number_part}"

        # Add version date if provided
        if version_date:
            try:
                v_date = datetime.strptime(version_date, '%Y-%m-%d')
                urn += f"@{v_date.strftime('%Y-%m-%d')}"
            except ValueError:
                raise ValueError(f"Invalid version date: {version_date}")

        # Add language if provided
        if language:
            urn += f"~{language}"

        return urn

    def generate_component_urn(
        self,
        document_urn: str,
        component_type: str,
        component_id: str
    ) -> str:
        """
        Generate URN for a document component

        Example:
            urn:lex:vn:quochoi:luat:2013-11-28;71!dieu6
            urn:lex:vn:quochoi:luat:2013-11-28;71@2020-01-01!dieu6.khoan2
        """
        # Clean component ID (remove special characters, use Latin transliteration)
        component_clean = self._clean_component_id(component_type, component_id)

        return f"{document_urn}!{component_clean}"

    def generate_ctv_urn(
        self,
        component_urn: str,
        effective_date: str
    ) -> str:
        """
        Generate URN for Component Temporal Version (CTV)

        Example:
            urn:lex:vn:quochoi:luat:2013-11-28;71!dieu6@2020-01-01
        """
        try:
            parsed_date = datetime.strptime(effective_date, '%Y-%m-%d')
            date_part = parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Invalid effective date: {effective_date}")

        # Remove any existing version date from component URN
        base_urn = component_urn.split('@')[0]

        return f"{base_urn}@{date_part}"

    def generate_manifestation_urn(
        self,
        expression_urn: str,
        format_type: str
    ) -> str:
        """
        Generate URN for manifestation (physical format)

        Example:
            urn:lex:vn:quochoi:luat:2013-11-28;71@2020-01-01~vi$pdf
        """
        format_clean = format_type.lower().replace('/', '.')
        return f"{expression_urn}${format_clean}"

    def parse_urn(self, urn: str) -> dict:
        """
        Parse a URN and extract its components

        Returns dict with: namespace, jurisdiction, type, date, number, version, language, component, format
        """
        # Validate URN prefix
        if not urn.startswith('urn:lex:vn:'):
            raise ValueError(f"Invalid URN prefix: {urn}")

        result = {
            'namespace': 'urn:lex:vn',
            'jurisdiction': None,
            'type': None,
            'date': None,
            'number': None,
            'version': None,
            'language': None,
            'component': None,
            'format': None,
        }

        # Remove namespace
        remainder = urn[len('urn:lex:vn:'):]

        # Split by delimiters
        # Format: {jurisdiction}:{type}:{date}[;{number}][@{version}][~{language}][!{component}][${format}]

        # Extract format first
        if '$' in remainder:
            remainder, result['format'] = remainder.split('$', 1)

        # Extract component
        if '!' in remainder:
            remainder, result['component'] = remainder.split('!', 1)

        # Extract language
        if '~' in remainder:
            remainder, result['language'] = remainder.split('~', 1)

        # Extract version
        if '@' in remainder:
            remainder, result['version'] = remainder.split('@', 1)

        # Split main parts
        parts = remainder.split(':')
        if len(parts) >= 3:
            result['jurisdiction'] = parts[0]
            result['type'] = parts[1]

            # Date and number are in the third part, separated by ';'
            date_number = parts[2]
            if ';' in date_number:
                result['date'], result['number'] = date_number.split(';', 1)
            else:
                result['date'] = date_number

        return result

    def _clean_number(self, number: str) -> str:
        """Clean and URL-encode document number"""
        # Replace / with - for URL safety
        cleaned = number.replace('/', '-')
        # Remove extra spaces
        cleaned = re.sub(r'\s+', '-', cleaned.strip())
        # URL encode
        return quote(cleaned, safe='-.')

    def _clean_component_id(self, component_type: str, component_id: str) -> str:
        """
        Clean component identifier

        Examples:
            DIEU, "6" -> "dieu6"
            KHOAN, "2" -> "khoan2"
            DIEM, "a" -> "diema"
            DIEM, "đ" -> "diemd"  # Transliterate đ -> d
        """
        type_map = {
            'PHAN': 'phan',
            'CHUONG': 'chuong',
            'MUC': 'muc',
            'DIEU': 'dieu',
            'KHOAN': 'khoan',
            'DIEM': 'diem',
            'TIEU_MUC': 'tieumuc',
        }

        type_part = type_map.get(component_type, component_type.lower())

        # Transliterate Vietnamese characters
        id_clean = self._transliterate_vietnamese(component_id)

        # Remove special characters
        id_clean = re.sub(r'[^a-z0-9]', '', id_clean.lower())

        return f"{type_part}{id_clean}"

    def _transliterate_vietnamese(self, text: str) -> str:
        """Simple Vietnamese to Latin transliteration for URNs"""
        transliteration = {
            'á': 'a', 'à': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
            'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
            'â': 'a', 'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
            'đ': 'd',
            'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
            'ê': 'e', 'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
            'í': 'i', 'ì': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
            'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
            'ô': 'o', 'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
            'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
            'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
            'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
            'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
        }

        result = text
        for viet, latin in transliteration.items():
            result = result.replace(viet, latin)
            result = result.replace(viet.upper(), latin.upper())

        return result

    def generate_work_id(self, doc_type: str, year: int, number: Optional[str] = None) -> str:
        """
        Generate a human-readable work ID

        Example:
            HIEN_PHAP, 2013 -> "HIENPHAP-2013"
            LUAT, 2020, "58/2020/QH14" -> "LUAT-2020-58"
        """
        type_part = doc_type.replace('_', '')

        if number:
            # Extract just the number part
            num_match = re.search(r'(\d+)', number)
            if num_match:
                num_part = num_match.group(1)
                return f"{type_part}-{year}-{num_part}"

        return f"{type_part}-{year}"


def main():
    """Example usage"""
    urn_gen = URNGenerator()

    # Example 1: Hiến pháp 2013
    doc_urn = urn_gen.generate_document_urn(
        doc_type='HIEN_PHAP',
        authority='QUOC_HOI',
        issue_date='2013-11-28',
        number='71/QH13'
    )
    print(f"Document URN: {doc_urn}")

    # Example 2: Component URN
    comp_urn = urn_gen.generate_component_urn(
        document_urn=doc_urn,
        component_type='DIEU',
        component_id='6'
    )
    print(f"Component URN: {comp_urn}")

    # Example 3: CTV URN
    ctv_urn = urn_gen.generate_ctv_urn(
        component_urn=comp_urn,
        effective_date='2020-01-01'
    )
    print(f"CTV URN: {ctv_urn}")

    # Example 4: Parse URN
    parsed = urn_gen.parse_urn(ctv_urn)
    print(f"\nParsed URN: {parsed}")

    # Example 5: Work ID
    work_id = urn_gen.generate_work_id('HIEN_PHAP', 2013, '71/QH13')
    print(f"Work ID: {work_id}")


if __name__ == '__main__':
    main()
