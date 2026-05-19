from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description', "owner_id"] #all field is not needed
        extra_kwargs = {"owner_id": {"read_only": True}}
        extra_kwargs = {"is_staff": {"read_only": True}}
        
        def __init__(self, *args, **kwargs):
            super.__init__(*args, **kwargs)
            request = self.context.get("request")
            if request and not request.user.is_staff:
                self.fields.pop("owner_id")

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["owner_id", 'name', 'description', "category", "price", "image", "inventory"]
        extra_kwargs = {"owner_id": {"read_only": True}}
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            request = self.context.get("request")
            if request and not request.user.is_staff:
                # Hide staff field for non-admins
                self.fields.pop("owner_id")
        
        

       
