#!/usr/bin/env python3
"""
Query Templates for Vietnamese Legal Knowledge Graph
Production-ready Cypher queries for common use cases
"""

from typing import Dict, Any, Optional
from datetime import date


class LegalQueryTemplates:
    """Collection of parameterized Cypher queries for Vietnamese legal documents"""

    @staticmethod
    def point_in_time_article(
        work_id: str,
        article_number: str,
        target_date: str
    ) -> tuple[str, Dict[str, Any]]:
        """
        Retrieve a specific article at a point in time

        Args:
            work_id: Document work ID (e.g., "HIENPHAP-2013")
            article_number: Article number (e.g., "6")
            target_date: Date in YYYY-MM-DD format

        Returns:
            (query, params) tuple
        """
        query = """
        MATCH (dieu:Dieu {soDinhDanh: $article_number})
          <-[:HAS_COMPONENT]-(vb:VanBan {workId: $work_id})
        MATCH (dieu)-[:HAS_EXPRESSION]->(ctv:CTV)
        WHERE ctv.ngayHieuLuc <= date($target_date)
          AND ctv.ngayHetHieuLuc >= date($target_date)
          AND ctv.trangThai = 'HIEU_LUC'
        RETURN dieu.tieuDe as tieuDe,
               ctv.noiDung as noiDung,
               ctv.ngayHieuLuc as ngayHieuLuc,
               ctv.ctvId as ctvId
        ORDER BY ctv.ngayHieuLuc DESC
        LIMIT 1
        """

        params = {
            'work_id': work_id,
            'article_number': article_number,
            'target_date': target_date
        }

        return query, params

    @staticmethod
    def reconstruct_document(
        work_id: str,
        target_date: str,
        max_depth: int = 7
    ) -> tuple[str, Dict[str, Any]]:
        """
        Reconstruct entire document structure at a specific date

        Args:
            work_id: Document work ID
            target_date: Date in YYYY-MM-DD format
            max_depth: Maximum hierarchy depth (default 7 for Vietnamese legal docs)

        Returns:
            (query, params) tuple
        """
        query = """
        WITH date($target_date) as targetDate
        MATCH (vb:VanBan {workId: $work_id})
        MATCH (vb)-[:HAS_EXPRESSION]->(tv:PhienBanVanBan)
        WHERE tv.ngayHieuLuc <= targetDate
          AND tv.ngayHetHieuLuc >= targetDate
        MATCH (tv)-[:AGGREGATES]->(ctv:CTV)
        MATCH (ctv)<-[:HAS_EXPRESSION]-(tp:ThanhPhanVanBan)
        WHERE ctv.trangThai = 'HIEU_LUC'
        RETURN tp.loaiThanhPhan as loai,
               tp.soDinhDanh as so,
               tp.tieuDe as tieuDe,
               ctv.noiDung as noiDung,
               tp.capBac as capBac,
               tp.thuTuSapXep as thuTu,
               ctv.ctvId as ctvId
        ORDER BY tp.capBac, tp.thuTuSapXep
        """

        params = {
            'work_id': work_id,
            'target_date': target_date
        }

        return query, params

    @staticmethod
    def document_version_history(
        work_id: str,
        component_id: Optional[str] = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Get version history for a document or specific component

        Args:
            work_id: Document work ID
            component_id: Optional component ID (e.g., "DIEU-6")

        Returns:
            (query, params) tuple
        """
        if component_id:
            query = """
            MATCH (vb:VanBan {workId: $work_id})
            MATCH (vb)-[:HAS_COMPONENT*1..]->(tp:ThanhPhanVanBan {workId: $component_id})
            MATCH (tp)-[:HAS_EXPRESSION]->(ctv:CTV)
            OPTIONAL MATCH (ctv)-[:IS_DERIVATIVE_OF]->(ctvPrev:CTV)
            OPTIONAL MATCH (ctv)-[:PRODUCED_BY]->(evt:SuKienLapPhap)
            OPTIONAL MATCH (evt)-[:COMMANDED_BY]->(tpInst:ThanhPhanVanBan)
              <-[:HAS_COMPONENT*1..5]-(vbInst:VanBan)
            RETURN ctv.ngayHieuLuc as ngayHieuLuc,
                   ctv.ngayHetHieuLuc as ngayHetHieuLuc,
                   ctv.noiDung as noiDung,
                   ctv.loaiThayDoi as loaiThayDoi,
                   ctvPrev.noiDung as noiDungTruoc,
                   evt.loaiSuKien as loaiSuKien,
                   vbInst.tenGoi as vanBanSuaDoi,
                   vbInst.soHieu as soHieuSuaDoi
            ORDER BY ctv.ngayHieuLuc
            """
            params = {'work_id': work_id, 'component_id': component_id}
        else:
            query = """
            MATCH (vb:VanBan {workId: $work_id})
            MATCH (vb)-[:HAS_EXPRESSION]->(tv:PhienBanVanBan)
            OPTIONAL MATCH (tv)-[:IS_DERIVATIVE_OF]->(tvPrev:PhienBanVanBan)
            RETURN tv.ngayHieuLuc as ngayHieuLuc,
                   tv.ngayHetHieuLuc as ngayHetHieuLuc,
                   tv.loaiPhienBan as loaiPhienBan,
                   tv.vanBanSuaDoi as vanBanSuaDoi,
                   tv.soThanhPhanThayDoi as soThanhPhanThayDoi,
                   tv.ghiChu as ghiChu
            ORDER BY tv.ngayHieuLuc
            """
            params = {'work_id': work_id}

        return query, params

    @staticmethod
    def changes_in_period(
        work_id: str,
        start_date: str,
        end_date: str
    ) -> tuple[str, Dict[str, Any]]:
        """
        Find all changes to a document within a time period

        Args:
            work_id: Document work ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            (query, params) tuple
        """
        query = """
        WITH date($start_date) as startDate,
             date($end_date) as endDate
        MATCH (vb:VanBan {workId: $work_id})
        MATCH (vb)-[:HAS_COMPONENT*1..7]->(tp:ThanhPhanVanBan)
        MATCH (tp)-[:HAS_EXPRESSION]->(ctv:CTV)
        WHERE ctv.ngayHieuLuc >= startDate
          AND ctv.ngayHieuLuc <= endDate
          AND ctv.loaiThayDoi IS NOT NULL
        OPTIONAL MATCH (ctv)-[:PRODUCED_BY]->(evt:SuKienLapPhap)
        OPTIONAL MATCH (evt)<-[:BAN_HANH]-(vbSuaDoi:VanBan)
        RETURN tp.loaiThanhPhan as loaiThanhPhan,
               tp.soDinhDanh as soDinhDanh,
               tp.tieuDe as tieuDe,
               ctv.ngayHieuLuc as ngayThayDoi,
               ctv.loaiThayDoi as loaiThayDoi,
               ctv.noiDung as noiDungMoi,
               evt.loaiSuKien as loaiSuKien,
               vbSuaDoi.tenGoi as vanBanSuaDoi,
               vbSuaDoi.soHieu as soHieu
        ORDER BY ctv.ngayHieuLuc, tp.capBac, tp.thuTuSapXep
        """

        params = {
            'work_id': work_id,
            'start_date': start_date,
            'end_date': end_date
        }

        return query, params

    @staticmethod
    def implementing_documents(
        work_id: str,
        relationship_type: str = 'HUONG_DAN_THI_HANH'
    ) -> tuple[str, Dict[str, Any]]:
        """
        Find all documents that implement/guide a law

        Args:
            work_id: Document work ID
            relationship_type: Type of relationship (HUONG_DAN_THI_HANH, QUY_DINH_CHI_TIET, etc.)

        Returns:
            (query, params) tuple
        """
        query = f"""
        MATCH (luat:VanBan {{workId: $work_id}})
        MATCH (vbHuongDan:VanBan)-[r:{relationship_type}]->(luat)
        OPTIONAL MATCH (vbHuongDan)-[:ISSUED_BY]->(cq:CoQuanBanHanh)
        RETURN vbHuongDan.tenGoi as tenGoi,
               vbHuongDan.soHieu as soHieu,
               vbHuongDan.loaiVanBan as loaiVanBan,
               vbHuongDan.ngayBanHanh as ngayBanHanh,
               vbHuongDan.ngayHieuLuc as ngayHieuLuc,
               cq.tenVietTat as coQuanBanHanh,
               r.phamVi as phamVi,
               r.noiDung as moTa
        ORDER BY vbHuongDan.ngayBanHanh DESC
        """

        params = {'work_id': work_id}

        return query, params

    @staticmethod
    def legal_basis_chain(
        work_id: str,
        max_depth: int = 5
    ) -> tuple[str, Dict[str, Any]]:
        """
        Find legal basis chain (hierarchical authority)

        Args:
            work_id: Document work ID
            max_depth: Maximum depth to traverse

        Returns:
            (query, params) tuple
        """
        query = """
        MATCH path = (vb:VanBan {workId: $work_id})-[:CAN_CU*1..]->(basis:VanBan)
        WITH path, length(path) as depth
        WHERE depth <= $max_depth
        UNWIND nodes(path) as doc
        WITH doc, depth
        ORDER BY depth DESC
        RETURN DISTINCT doc.tenGoi as tenGoi,
               doc.soHieu as soHieu,
               doc.loaiVanBan as loaiVanBan,
               doc.ngayBanHanh as ngayBanHanh,
               doc.capPhapLy as capPhapLy
        ORDER BY doc.capPhapLy, doc.ngayBanHanh
        """

        params = {
            'work_id': work_id,
            'max_depth': max_depth
        }

        return query, params

    @staticmethod
    def documents_by_authority_and_period(
        authority_id: str,
        doc_type: str,
        year: int
    ) -> tuple[str, Dict[str, Any]]:
        """
        Find all documents of a type issued by an authority in a year

        Args:
            authority_id: Authority ID (e.g., "BO_TAI_CHINH")
            doc_type: Document type (e.g., "THONG_TU")
            year: Year (e.g., 2023)

        Returns:
            (query, params) tuple
        """
        query = """
        MATCH (cq:CoQuanBanHanh {coQuanId: $authority_id})
        MATCH (vb:VanBan {loaiVanBan: $doc_type})-[:ISSUED_BY]->(cq)
        WHERE vb.ngayBanHanh >= date($start_date)
          AND vb.ngayBanHanh <= date($end_date)
        RETURN vb.tenGoi as tenGoi,
               vb.soHieu as soHieu,
               vb.ngayBanHanh as ngayBanHanh,
               vb.ngayHieuLuc as ngayHieuLuc,
               vb.trangThai as trangThai
        ORDER BY vb.ngayBanHanh DESC
        """

        params = {
            'authority_id': authority_id,
            'doc_type': doc_type,
            'start_date': f'{year}-01-01',
            'end_date': f'{year}-12-31'
        }

        return query, params

    @staticmethod
    def cross_document_impact(
        amending_doc_number: str,
        amending_doc_type: str = 'NGHI_DINH'
    ) -> tuple[str, Dict[str, Any]]:
        """
        Find which laws are affected by an amending document

        Args:
            amending_doc_number: Document number (e.g., "01/2021/NĐ-CP")
            amending_doc_type: Document type

        Returns:
            (query, params) tuple
        """
        query = """
        MATCH (nghiDinh:VanBan {soHieu: $doc_number, loaiVanBan: $doc_type})
        MATCH (nghiDinh)-[r:QUY_DINH_CHI_TIET|HUONG_DAN_THI_HANH|SUA_DOI|BO_SUNG]->(affected:VanBan)
        RETURN affected.tenGoi as tenGoi,
               affected.soHieu as soHieu,
               affected.loaiVanBan as loaiVanBan,
               type(r) as loaiQuanHe,
               r.phamVi as phamViAnhHuong,
               r.ngayHieuLuc as ngayHieuLuc
        ORDER BY affected.capPhapLy, affected.ngayBanHanh
        """

        params = {
            'doc_number': amending_doc_number,
            'doc_type': amending_doc_type
        }

        return query, params

    @staticmethod
    def full_text_search(
        search_term: str,
        doc_type: Optional[str] = None,
        limit: int = 20
    ) -> tuple[str, Dict[str, Any]]:
        """
        Full-text search across legal content

        Args:
            search_term: Search query
            doc_type: Optional document type filter
            limit: Maximum results

        Returns:
            (query, params) tuple
        """
        if doc_type:
            query = """
            CALL db.index.fulltext.queryNodes('noi_dung_van_ban', $search_term)
            YIELD node, score
            WHERE node:VanBan AND node.loaiVanBan = $doc_type
            RETURN node.tenGoi as tenGoi,
                   node.soHieu as soHieu,
                   node.loaiVanBan as loaiVanBan,
                   score
            ORDER BY score DESC
            LIMIT $limit
            """
            params = {'search_term': search_term, 'doc_type': doc_type, 'limit': limit}
        else:
            query = """
            CALL db.index.fulltext.queryNodes('noi_dung_van_ban', $search_term)
            YIELD node, score
            RETURN CASE
                     WHEN node:VanBan THEN node.tenGoi
                     WHEN node:ThanhPhanVanBan THEN node.tieuDe
                     WHEN node:CTV THEN node.ctvId
                     ELSE null
                   END as noiDung,
                   labels(node) as loaiNode,
                   score
            ORDER BY score DESC
            LIMIT $limit
            """
            params = {'search_term': search_term, 'limit': limit}

        return query, params

    @staticmethod
    def current_effective_documents(
        doc_type: Optional[str] = None,
        limit: int = 100
    ) -> tuple[str, Dict[str, Any]]:
        """
        Get all currently effective documents

        Args:
            doc_type: Optional document type filter
            limit: Maximum results

        Returns:
            (query, params) tuple
        """
        if doc_type:
            query = """
            MATCH (vb:VanBan {trangThai: 'HIEU_LUC', loaiVanBan: $doc_type})
            OPTIONAL MATCH (vb)-[:ISSUED_BY]->(cq:CoQuanBanHanh)
            RETURN vb.tenGoi as tenGoi,
                   vb.soHieu as soHieu,
                   vb.ngayBanHanh as ngayBanHanh,
                   vb.ngayHieuLuc as ngayHieuLuc,
                   cq.tenVietTat as coQuanBanHanh
            ORDER BY vb.ngayBanHanh DESC
            LIMIT $limit
            """
            params = {'doc_type': doc_type, 'limit': limit}
        else:
            query = """
            MATCH (vb:VanBan {trangThai: 'HIEU_LUC'})
            OPTIONAL MATCH (vb)-[:ISSUED_BY]->(cq:CoQuanBanHanh)
            RETURN vb.tenGoi as tenGoi,
                   vb.soHieu as soHieu,
                   vb.loaiVanBan as loaiVanBan,
                   vb.ngayBanHanh as ngayBanHanh,
                   vb.ngayHieuLuc as ngayHieuLuc,
                   cq.tenVietTat as coQuanBanHanh
            ORDER BY vb.ngayBanHanh DESC
            LIMIT $limit
            """
            params = {'limit': limit}

        return query, params


def main():
    """Example usage of query templates"""
    templates = LegalQueryTemplates()

    # Example 1: Point-in-time query
    query, params = templates.point_in_time_article(
        work_id='HIENPHAP-2013',
        article_number='6',
        target_date='2020-01-01'
    )
    print("=== Point-in-Time Article Query ===")
    print(f"Query:\n{query}")
    print(f"Params: {params}\n")

    # Example 2: Version history
    query, params = templates.document_version_history(
        work_id='BO-LUAT-DAN-SU-2015',
        component_id='DIEU-3'
    )
    print("=== Version History Query ===")
    print(f"Query:\n{query}")
    print(f"Params: {params}\n")

    # Example 3: Changes in period
    query, params = templates.changes_in_period(
        work_id='LUAT-DOANH-NGHIEP-2020',
        start_date='2020-01-01',
        end_date='2023-12-31'
    )
    print("=== Changes in Period Query ===")
    print(f"Query:\n{query}")
    print(f"Params: {params}\n")


if __name__ == '__main__':
    main()
