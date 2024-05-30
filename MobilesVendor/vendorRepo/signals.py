from django.db.models.signals import post_save
from django.db.models import F, Avg, Count
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import DurationField, ExpressionWrapper
from .models import PurchaseOrder, Vendor

@receiver(post_save, sender=PurchaseOrder)
def update_vendor_metrics(sender, instance, **kwargs):
    vendor = instance.vendor
    completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed')

    # On-Time Delivery Rate
    on_time_deliveries = completed_pos.filter(delivery_date__lte=F('delivery_date')).count()
    vendor.on_time_delivery_rate = (on_time_deliveries / completed_pos.count()) if completed_pos.count() else 0

    # Quality Rating Average
    vendor.quality_rating_avg = completed_pos.aggregate(Avg('quality_rating'))['quality_rating__avg'] or 0

    # Average Response Time
    acknowledgment_times = completed_pos.exclude(acknowledgment_date__isnull=True).annotate(
        response_time=ExpressionWrapper(F('acknowledgment_date') - F('issue_date'), output_field=DurationField())
    )
    vendor.average_response_time = acknowledgment_times.aggregate(Avg('response_time'))['response_time__avg'].total_seconds() if acknowledgment_times.exists() else 0

    # Fulfillment Rate
    vendor.fulfillment_rate = (completed_pos.filter(status='completed').count() / completed_pos.count()) if completed_pos.count() else 0

    vendor.save()
