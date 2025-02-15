from django import template

register = template.Library()

@register.filter(name='filter_work_status')
def filter_work_status(items, status):
    """智能過濾器自動適應資料類型"""
    try:
        # 優先嘗試 QuerySet 過濾
        return items.filter(work_status=status)
    except AttributeError:
        # 降級使用列表推導式
        return [item for item in items if getattr(item, 'work_status', None) == status]