# report_generator.py
import pandas as pd
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging
from .database_service import CrawlerDatabase

logger = logging.getLogger(__name__)

class CrawlerReport:
    def __init__(self, db: CrawlerDatabase):
        self.db = db
    
    def generate_summary_report(self, crawler_id: str) -> Dict[str, Any]:
        """生成摘要报告"""
        stats = self.db.get_statistics(crawler_id)
        df = self.db.get_crawler_data(crawler_id)
        if df.empty:
            return {"error": f"没有找到爬虫 {crawler_id} 的数据"}
        report = {
            "crawler_id": crawler_id,
            "generated_at": datetime.now().isoformat(),
            "total_requests": int(stats.get('total_requests', 0)),
            "successful_requests": int(stats.get('successful_requests', 0)),
            "failed_requests": int(stats.get('failed_requests', 0)),
            "cache_hits": int(stats.get('cache_hits', 0)),
            "avg_response_time": float(stats.get('avg_response_time', 0)),
            "success_rate": 0,
            "cache_hit_rate": 0
        }
        if report['total_requests'] > 0:
            report['success_rate'] = round(
                report['successful_requests'] / report['total_requests'] * 100, 2
            )
            report['cache_hit_rate'] = round(
                report['cache_hits'] / report['total_requests'] * 100, 2
            )
        if 'status_code' in df.columns:
            status_dist = df['status_code'].value_counts().to_dict()
            report['status_distribution'] = status_dist
        if 'content_type' in df.columns:
            content_dist = df['content_type'].value_counts().to_dict()
            report['content_type_distribution'] = content_dist
        failed_requests = df[df['success'] == 0]
        if not failed_requests.empty:
            report['failed_urls'] = failed_requests[['url', 'status_code', 'error_message']].to_dict('records')
        return report
    
    def generate_excel_report(self, crawler_id: str, output_path: str = None) -> str:
        """生成Excel报告"""
        if output_path is None:
            output_path = f"./reports/crawler_report_{crawler_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df = self.db.get_crawler_data(crawler_id)
        if df.empty:
            logger.warning(f"没有找到爬虫 {crawler_id} 的数据")
            return ""
        stats = self.generate_summary_report(crawler_id)
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            summary_df = pd.DataFrame([stats])
            summary_df.to_excel(writer, sheet_name='统计摘要', index=False)
            df.to_excel(writer, sheet_name='详细数据', index=False)
            if 'status_code' in df.columns:
                status_dist = df['status_code'].value_counts().reset_index()
                status_dist.columns = ['状态码', '数量']
                status_dist.to_excel(writer, sheet_name='状态码分布', index=False)
            failed_df = df[df['success'] == 0]
            if not failed_df.empty:
                failed_df[['url', 'status_code', 'error_message', 'created_at']].to_excel(
                    writer, sheet_name='失败请求', index=False
                )
        
        logger.info(f"Excel报告已生成: {output_path}")
        return output_path
    
    def export_json_report(self, crawler_id: str, output_path: str = None) -> str:
        """导出JSON报告"""
        if output_path is None:
            output_path = f"./reports/crawler_report_{crawler_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report = self.generate_summary_report(crawler_id)
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"JSON报告已生成: {output_path}")
        return output_path
    
    def get_recent_requests(self, crawler_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        df = self.db.get_crawler_data(crawler_id)
        if not df.empty:
            return df.head(limit).to_dict('records')
        return []