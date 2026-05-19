# views.py
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from shared.simple_permissions import IsAuth, IsAuthOrReadOnly, IsAdmin, IsAdminOrReadOnly

from django.http import JsonResponse

def health(request):
    return JsonResponse({"status": "ok"})
    
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def fetch_bulk(request):
	
    # --- Handle POST ---
    if request.method == "POST":
        ids = request.data.get("ids", [])
    else:  # --- Handle GET ---
        ids_param = request.query_params.get("ids", "")
        ids = [int(i) for i in ids_param.split(",") if i.isdigit()] if ids_param else []

    if not ids:
        return Response({"error": "No valid ids provided"}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch all products in one query
    products = Product.objects.filter(id__in=ids)
    product_map = {p.id: p for p in products}

    # Rebuild in the original order
    ordered_products = [product_map[i] for i in ids if i in product_map]

    serializer = ProductSerializer(ordered_products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryListCreateView(generics.ListCreateAPIView):
    """List categories (anyone) + Create categories (admin only)"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly] 
    
    def perform_create(self, serializer):
                # Manual admin check for creation
        if not getattr(self.request.user, 'is_admin', False):
            raise PermissionDenied("Admin access required to create categories")
        serializer.save(owner_id=self.request.user.user_id)

class CategoryDetailAdminView(generics.RetrieveUpdateDestroyAPIView):
    """List categories (anyone) + Create categories (admin only)"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]  
    

class ProductListCreateView(generics.ListCreateAPIView):
    """List products (anyone) + Create products (admin only)"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]  
    
    def perform_create(self, serializer):
                # Manual admin check for creation
        if not getattr(self.request.user, 'is_admin', False):
            raise PermissionDenied("Admin access required to create categories")
        serializer.save(owner_id=self.request.user.user_id)
        
class ProductDetailAdminView(generics.RetrieveUpdateDestroyAPIView):
    """Admin-only product management"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer    
    permission_classes = [IsAdminOrReadOnly]  

# Additional API views with shared permissions
class ProductSearchView(APIView):
    """Search products - authenticated users only"""
    permission_classes = [IsAuth]
    
    def get(self, request):
        # request.user_id is available from JWT middleware
        query = self.request.GET.get('q', '')
        products = Product.objects.filter(name__icontains=query)[:50]
        serializer = ProductSerializer(products, many=True)
        return Response({
            'query': query,
            'products': serializer.data,
            'user_id': getattr(request.user, 'user_id', None)
        })

class ProductStatsView(APIView):
    """Product statistics - admin only"""
    permission_classes = [IsAdmin]  # Using shared permission
    
    def get(self, request):
        # request.is_admin is True (guaranteed by permission)
        stats = {
            'total_products': Product.objects.count(),
            'total_categories': Category.objects.count(),
            'admin_user': getattr(request.user, 'user_id', None)
        }
        return Response(stats)

class UserProductsView(APIView):
    """Products related to authenticated user"""
    permission_classes = [IsAuth]  # Using shared permission
    
    def get(self, request):
        # User-specific logic using request.user_id
        user_id = getattr(request.user, 'user_id')
        
        # Example: Get products user might be interested in
        products = Product.objects.all()[:10]  # Simplified
        serializer = ProductSerializer(products, many=True)
        
        return Response({
            'user_id': user_id,
            'recommended_products': serializer.data
        })

# Utility view for debugging permissions
class PermissionTestView(APIView):
    """Test different permission levels"""
    permission_classes = [IsAuth]  # Base authentication required
    
    def get(self, request):
        return Response({
            'user_id': getattr(request.user, 'user_id', None),
            'is_admin': getattr(request.user, 'is_admin', False),
            'permissions': getattr(request.user, 'user_permissions', []),
            'message': 'You are authenticated!'
        })

# Custom exception handling for permission errors
from rest_framework.exceptions import PermissionDenied

def manual_admin_check(request):
    """Helper function for manual admin checks"""
    if not getattr(request.user, 'is_admin', False):
        raise PermissionDenied("Admin privileges required")

def manual_auth_check(request):
    """Helper function for manual authentication checks"""
    if not getattr(request.user, 'user_id', None):
        raise PermissionDenied("Authentication required")
