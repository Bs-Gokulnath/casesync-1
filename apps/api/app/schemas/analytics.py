from pydantic import BaseModel


class CountByKey(BaseModel):
    key: str
    label: str
    count: int


class AnalyticsSummary(BaseModel):
    total: int
    by_status: list[CountByKey]
    by_bureau: list[CountByKey]
    by_region: list[CountByKey]
    by_category: list[CountByKey]
    by_priority: list[CountByKey]
    overdue_count: int
    disposed_count: int
    disposal_rate: float
    overlap_by_status: list[CountByKey]
