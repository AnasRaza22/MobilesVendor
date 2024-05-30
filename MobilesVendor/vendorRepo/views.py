from rest_framework import viewsets,status
from rest_framework.decorators import action
from time import timezone
from rest_framework.response import Response
from .models import Vendor, PurchaseOrder
from .signals import update_vendor_metrics
from .serializers import VendorSerializer, VendorCreateUpdateSerializer,PurchaseOrderCreateUpdateSerializer,PurchaseOrderSerializer

class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return VendorCreateUpdateSerializer
        return VendorSerializer
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        vendor = self.get_object()
        serializer = VendorSerializer(vendor)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance=self.get_object()
        vendor_name=instance.name
        self.perform_destroy(instance)

        return Response({"msg":f"You have deleted {vendor_name} vendor"},status=status.HTTP_204_NO_CONTENT)
    def perform_destroy(self, instance):
        instance.delete()

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PurchaseOrderCreateUpdateSerializer
        return PurchaseOrderSerializer
    
    def perform_create(self, serializer):
        purchase_order = serializer.save()
        update_vendor_metrics(sender=PurchaseOrder, instance=purchase_order)

    def perform_update(self, serializer):
        purchase_order = serializer.save()
        update_vendor_metrics(sender=PurchaseOrder, instance=purchase_order)

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        purchase_order = self.get_object()
        purchase_order.acknowledgment_date = timezone.now()
        purchase_order.save()
        update_vendor_metrics(sender=PurchaseOrder, instance=purchase_order)
        return Response({'status': 'acknowledged'})
