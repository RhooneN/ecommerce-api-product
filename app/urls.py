from django.urls import path, include
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

# API versioning prefix
# ~ app_name = 'products'

urlpatterns = [
     # Categories
     path('categories/', views.CategoryListCreateView.as_view(), name='category-list'),
     path('categories/<int:pk>/', views.CategoryDetailAdminView.as_view(), name='category-detail'),
    
     # Products  
     path('products/', views.ProductListCreateView.as_view(), name='product-list'),
     path('products/<int:pk>/', views.ProductDetailAdminView.as_view(), name='product-detail'),
     
     # ~ fetch_bulk
     path('bulk/', views.fetch_bulk, name='fetch-bulk'),
     
     # Search and user-specific
     path('products/search/', views.ProductSearchView.as_view(), name='product-search'),
     path('products/recommendations/', views.UserProductsView.as_view(), name='product-recommendations'),
     path('stats/', views.ProductStatsView.as_view(), name='stats'),
     path("health/", views.health),
     
      #Swagger
    path(
        "api/schema/", SpectacularAPIView.as_view(permission_classes=[AllowAny]), name="schema",),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema', permission_classes=[AllowAny]), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema', permission_classes=[AllowAny]), name='redoc'),
    ]
