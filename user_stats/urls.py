from django.urls import path
from .views import ExpenseSummaryStats,IncomeSummaryStats

urlpatterns = [
    path('expense_category_data',ExpenseSummaryStats.as_view(),name = "expense-category-summary"),
    path('income_source_data',IncomeSummaryStats.as_view(),name = "income-source-summary")
]