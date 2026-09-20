from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class BaseScenario(ABC):
    """場景基類"""

    NAME = ""
    DESCRIPTION = ""
    REQUIRED_PARAMS = []

    def __init__(self):
        self.current_date = datetime.now()
        self.default_end_date = self.current_date.strftime('%Y-%m-%d')
        self.default_start_date = (self.current_date - timedelta(days=30)).strftime('%Y-%m-%d')
        self.default_end_month = self.current_date.strftime('%Y-%m')
        self.default_start_month = (self.current_date - timedelta(days=90)).strftime('%Y-%m')

    @abstractmethod
    def get_mcp_tools(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        獲取需要呼叫的MCP工具列表

        Args:
            params: 使用者輸入引數

        Returns:
            list: MCP工具呼叫列表，每個元素包含 tool_name 和 arguments
        """
        pass

    @abstractmethod
    def aggregate_data(self, raw_data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        聚合MCP返回的資料

        Args:
            raw_data: MCP工具返回的原始資料
            params: 使用者輸入引數

        Returns:
            dict: 聚合後的結構化資料
        """
        pass

    @abstractmethod
    def generate_insights(self, data: Dict[str, Any]) -> List[str]:
        """
        生成關鍵洞察

        Args:
            data: 聚合後的資料

        Returns:
            list: 洞察列表
        """
        pass

    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        驗證引數

        Args:
            params: 使用者輸入引數

        Returns:
            tuple: (is_valid, missing_params)
        """
        missing = []
        for param in self.REQUIRED_PARAMS:
            if param not in params or not params[param]:
                missing.append(param)
        return len(missing) == 0, missing

    def get_scenario_info(self) -> Dict[str, str]:
        """獲取場景資訊"""
        return {
            'name': self.NAME,
            'description': self.DESCRIPTION,
            'required_params': self.REQUIRED_PARAMS
        }
