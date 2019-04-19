from django.db import models
from carts.models import Cart
from first_app.utils import unique_order_id_generartor
from django.db.models.signals import pre_save, post_save
import math
from billing.models import BillingProfile
from addresses.models import Address

ORDER_STATUS_CHOICES = (
			('created','Created'),
			('paid','Paid'),
			('shipped','Shipped'),
			('refunded','Refunded'),
			)

class OrderManager(models.Manager):
	def new_or_get(self, billing_profile, cart_obj):
		created = False
		qs =self.get_queryset().filter(cart=cart_obj,
							billing_profile=billing_profile,
							 active=True)
		if qs.count() == 1:
			obj = qs.first()
		else:
			obj = self.model.objects.create(cart=cart_obj,
							billing_profile=billing_profile)
			created = True
		return obj, created
class Order(models.Model):
	order_id = models.CharField(max_length=120, blank=True)
	billing_profile = models.ForeignKey(BillingProfile, null=True,blank=True)
	billing_address = models.ForeignKey(Address,related_name="billing_address",null=True,blank=True)
	shipping_address = models.ForeignKey(Address,related_name="shipping_address",null=True,blank=True)
	cart = models.ForeignKey(Cart)
	status = models.CharField(max_length=120, default='created',choices=ORDER_STATUS_CHOICES)
	shipping_total = models.DecimalField(default=5.99,max_digits=100,decimal_places=2)
	total = models.DecimalField(default=0.00,max_digits=100,decimal_places=2)
	active = models.BooleanField(default=True)
	def __str__(self):
		return self.order_id
	objects = OrderManager()
	def update_total(self):
		cart_total = self.cart.total
		shipping_total = self.shipping_total
		new_total = math.fsum([cart_total,shipping_total])
		formatted_total = format(new_total,'.2f')
		self.total = formatted_total
		self.save()
		return new_total

def pre_save_create_order_id(sender, instance,*args,**kwargs):
	if not instance.order_id:
		instance.order_id = unique_order_id_generartor(instance)
	qs = Order.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
	if qs.exists():
		qs.update(active=False)
pre_save.connect(pre_save_create_order_id,sender=Order)
def post_save_cart_total(sender,instance,created,*args,**kwargs):
	if not created:
		cart_obj = instance
		qs = Order.objects.filter(cart__id=cart_obj.id)
		if qs.count() == 1:
			order_obj = qs.first()
			order_obj.update_total()
post_save.connect(post_save_cart_total, sender=Cart)

def post_save_order(sender, instance, created, *args, **kwargs):
	if created:
		instance.update_total()
post_save.connect(post_save_order, sender=Order)
