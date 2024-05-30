# vendors/tests.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Vendor, PurchaseOrder
from django.utils import timezone

class VendorTests(APITestCase):
    def test_create_vendor(self):
        url = reverse('vendor-list')
        data = {'name': 'Test Vendor', 'contact_details': '123456789', 'address': '123 Test St', 'vendor_code': 'V123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_delete_vendor(self):
        vendor = Vendor.objects.create(name='Test Vendor', contact_details='123456789', address='123 Test St', vendor_code='V123')
        url = reverse('vendor-detail', args=[vendor.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], f'You have deleted the vendor: {vendor.name}.')

class PurchaseOrderTests(APITestCase):
    def test_create_purchase_order(self):
        vendor = Vendor.objects.create(name='Test Vendor', contact_details='123456789', address='123 Test St', vendor_code='V123')
        url = reverse('purchaseorder-list')
        data = {'po_number': 'PO123', 'vendor': vendor.id, 'order_date': timezone.now(), 'delivery_date': timezone.now(), 'items': {}, 'quantity': 10, 'status': 'pending', 'issue_date': timezone.now()}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
