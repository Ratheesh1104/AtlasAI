from django.urls import path

from .views.commercial import InvoiceListView, ProductListView, QuoteCalculateView, QuoteSaveView
from .views.companies import CompanyDetailView, CompanyListView, CompanyTimelineView, SearchView
from .views.dashboard import DashboardAISummaryView, DashboardLegacyView, DashboardV2View
from .views.engagement import BriefView, FollowupApproveView, FollowupView
from .views.knowledge import KnowledgeSearchView, PolicyListView
from .views.misc import RootView, SeedView, TaskListView
from .views.workbench import (
    WorkbenchCardActionView, WorkbenchCardsView, WorkbenchExecuteView,
    WorkbenchOverviewView, WorkbenchProactiveView,
)

urlpatterns = [
    path("", RootView.as_view()),
    path("root", RootView.as_view()),
    path("seed", SeedView.as_view()),

    path("dashboard/v2", DashboardV2View.as_view()),
    path("dashboard/ai-summary", DashboardAISummaryView.as_view()),
    path("dashboard", DashboardLegacyView.as_view()),

    path("companies", CompanyListView.as_view()),
    path("companies/<str:company_id>/timeline", CompanyTimelineView.as_view()),
    path("companies/<str:company_id>", CompanyDetailView.as_view()),

    path("policies", PolicyListView.as_view()),
    path("knowledge/search", KnowledgeSearchView.as_view()),

    path("products", ProductListView.as_view()),
    path("invoices", InvoiceListView.as_view()),
    path("quote/calculate", QuoteCalculateView.as_view()),
    path("quote/save", QuoteSaveView.as_view()),

    path("search", SearchView.as_view()),

    path("brief", BriefView.as_view()),
    path("followup", FollowupView.as_view()),
    path("followup/approve", FollowupApproveView.as_view()),

    path("workbench/overview", WorkbenchOverviewView.as_view()),
    path("workbench/cards", WorkbenchCardsView.as_view()),
    path("workbench/proactive", WorkbenchProactiveView.as_view()),
    path("workbench/execute", WorkbenchExecuteView.as_view()),
    path("workbench/cards/<uuid:card_id>/<str:action>", WorkbenchCardActionView.as_view()),

    path("tasks", TaskListView.as_view()),
]
