
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from datetime import date, timedelta
import uuid

from .models import User, Medicine, Category, Bill, BillItem, CartItem, PharmacyOrder
from .forms import MedicineForm, UserCreateForm, OrderForm
from .generate_signature import genSha256
import base64, json


ESEWA_SECRET_KEY  = '8gBm/:&EnhH.1/q'   
ESEWA_PRODUCT_CODE = 'EPAYTEST'       
ESEWA_PAYMENT_URL  = 'https://rc-epay.esewa.com.np/api/epay/main/v2/form'


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            messages.error(request, "Admins only.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper



def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(request,
                            username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Invalid credentials.")
    return render(request, 'pharmacy/login.html')


def admin_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(request,
                            username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user and user.role == 'admin':
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Admin credentials only.")
    return render(request, 'pharmacy/admin_login.html')


def pharmacist_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(request,
                            username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user and user.role == 'pharmacist':
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Pharmacist credentials only.")
    return render(request, 'pharmacy/pharmacist_login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def dashboard(request):
    today             = date.today()
    total_medicines   = Medicine.objects.count()
    low_stock_meds    = Medicine.objects.filter(stock_quantity__lte=10)
    expired_count     = Medicine.objects.filter(expiry_date__lt=today).count()
    todays_bills      = Bill.objects.filter(created_at__date=today)
    todays_revenue    = todays_bills.aggregate(t=Sum('total_amount'))['t'] or 0
    todays_bill_count = todays_bills.count()
    total_revenue     = Bill.objects.aggregate(t=Sum('total_amount'))['t'] or 0
    recent_bills      = Bill.objects.order_by('-created_at')[:5]

    ctx = dict(
        total_medicines    = total_medicines,
        low_stock_count    = low_stock_meds.count(),
        low_stock_medicines= low_stock_meds[:5],
        expired_medicines  = expired_count,
        todays_revenue     = todays_revenue,
        todays_bill_count  = todays_bill_count,
        total_revenue      = total_revenue,
        recent_bills       = recent_bills,
    )
    if request.user.role == 'admin':
        ctx['total_users'] = User.objects.count()
        return render(request, 'pharmacy/dashboard_admin.html', ctx)
    return render(request, 'pharmacy/dashboard_pharmacist.html', ctx)




@login_required
def medicine_list(request):
    medicines = Medicine.objects.select_related('category').all()
    q = request.GET.get('search', '')
    if q:
        medicines = medicines.filter(name__icontains=q)
    cat = request.GET.get('category', '')
    if cat:
        medicines = medicines.filter(category__id=cat)
    return render(request, 'pharmacy/medicine_list.html', {
        'medicines':    medicines,
        'categories':   Category.objects.all(),
        'search_query': q,
        'today':        date.today(),
    })


@login_required
def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    return render(request, 'pharmacy/medicine_detail.html', {'medicine': medicine})


@login_required
@admin_required
def medicine_add(request):
    form = MedicineForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Medicine added!")
        return redirect('medicine_list')
    return render(request, 'pharmacy/add_medicine.html',
                  {'form': form, 'title': 'Add Medicine', 'action': 'Add'})


@login_required
@admin_required
def medicine_edit(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    form = MedicineForm(request.POST or None, request.FILES or None, instance=medicine)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Medicine updated!")
        return redirect('medicine_list')
    return render(request, 'pharmacy/add_medicine.html',
                  {'form': form, 'title': 'Edit Medicine', 'action': 'Update',
                   'medicine': medicine})


@login_required
@admin_required
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        medicine.delete()
        messages.success(request, f"'{medicine.name}' deleted.")
        return redirect('medicine_list')
    return render(request, 'pharmacy/medicine_confirm_delete.html',
                  {'medicine': medicine})




@login_required
def cart_view(request):
    cart_items  = CartItem.objects.filter(
        user=request.user).select_related('medicine', 'medicine__category')
    grand_total = sum(item.subtotal for item in cart_items)
    return render(request, 'pharmacy/cart.html', {
        'cart_items':  cart_items,
        'grand_total': grand_total,
    })


@login_required
def add_to_cart(request, pk):
    if request.method == 'POST':
        medicine = get_object_or_404(Medicine, pk=pk)
        quantity = int(request.POST.get('quantity', 1))
        if quantity > medicine.stock_quantity:
            messages.error(request, f"Only {medicine.stock_quantity} units available.")
            return redirect('medicine_detail', pk=pk)
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user, medicine=medicine,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        messages.success(request, f"'{medicine.name}' added to cart!")
        return redirect('cart')
    return redirect('medicine_list')


@login_required
def update_cart(request, pk):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, pk=pk, user=request.user)
        qty = int(request.POST.get('quantity', 1))
        if qty < 1:
            cart_item.delete()
        else:
            cart_item.quantity = qty
            cart_item.save()
    return redirect('cart')


@login_required
def remove_from_cart(request, pk):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, pk=pk, user=request.user)
        cart_item.delete()
        messages.success(request, "Item removed from cart.")
    return redirect('cart')


@login_required
def clear_cart(request):
    if request.method == 'POST':
        CartItem.objects.filter(user=request.user).delete()
        messages.success(request, "Cart cleared.")
    return redirect('cart')


@login_required
def order_now(request, pk):
   
    cart_item = get_object_or_404(CartItem, pk=pk, user=request.user)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # ── Create PharmacyOrder record ──
            order = PharmacyOrder.objects.create(
                user           = request.user,
                medicine       = cart_item.medicine,
                cart_item      = cart_item,
                quantity       = cart_item.quantity,
                total_price    = cart_item.subtotal,
                address        = data['address'],
                contact_no     = data['contact_no'],
                payment_method = data['payment_method'],
            )

            if order.payment_method == 'esewa':
                
                esewa_url = reverse('esewa_form')
                return redirect(f'{esewa_url}?o_id={order.id}&c_id={cart_item.id}')

           
           
            cart_item.medicine.stock_quantity -= cart_item.quantity
            cart_item.medicine.save()
            order.payment_status = 'unpaid'
            order.save()
            cart_item.delete()
            messages.success(request, "Order placed successfully!")
            return redirect('my_orders')

    else:
        form = OrderForm()

    return render(request, 'pharmacy/order_form.html', {
        'form':      form,
        'cart_item': cart_item,
    })






@login_required
def my_orders(request):
    """
    Shows all orders placed by the logged-in user.
    URL: /my-orders/
    Template: pharmacy/my_orders.html
    """
    orders = PharmacyOrder.objects.filter(
        user=request.user).select_related('medicine').order_by('-created_at')
    return render(request, 'pharmacy/my_orders.html', {'orders': orders})




class EsewaFormView(View):
   

    def get(self, request, *args, **kwargs):
        o_id      = request.GET.get('o_id')
        c_id      = request.GET.get('c_id')

        order     = get_object_or_404(PharmacyOrder, id=o_id, user=request.user)
        cart_item = get_object_or_404(CartItem, id=c_id)

        transaction_uuid = str(uuid.uuid4())

      
        order.transaction_uuid = transaction_uuid
        order.save()

        data_to_sign = (
            f"total_amount={order.total_price},"
            f"transaction_uuid={transaction_uuid},"
            f"product_code={ESEWA_PRODUCT_CODE}"
        )
        signature = genSha256(ESEWA_SECRET_KEY, data_to_sign)

     
        success_url = request.build_absolute_uri(
            reverse('esewa_success')
        )
        failure_url = request.build_absolute_uri(
            reverse('esewa_failure')
        )

        data = {
            'amount': order.total_price, 
            'tax_amount':       0,
            'total_amount':     order.total_price,       # 
            'transaction_uuid': transaction_uuid,
            'product_code':     ESEWA_PRODUCT_CODE,
            'product_service_charge': 0,
            'product_delivery_charge': 0,
            'success_url':      success_url,
            'failure_url':      failure_url,
            'signed_field_names': 'total_amount,transaction_uuid,product_code',
            'signature':        signature,
        }

        return render(request, 'pharmacy/esewa_form.html', {
            'order':       order,
            'cart_item':   cart_item,
            'data':        data,
            'payment_url': ESEWA_PAYMENT_URL,
        })


def esewa_success(request):
   
    

    encoded_data = request.GET.get('data', '')

    try:
  
        decoded_bytes = base64.b64decode(encoded_data)
        decoded_str   = decoded_bytes.decode('utf-8')
        response_data = json.loads(decoded_str)

        transaction_uuid = response_data.get('transaction_uuid')
        status           = response_data.get('status')
        total_amount     = response_data.get('total_amount')

        if status == 'COMPLETE':
            # Find the order using transaction UUID
            order = PharmacyOrder.objects.get(transaction_uuid=transaction_uuid)
            order.payment_status = 'paid'
            order.save()

           
            order.medicine.stock_quantity -= order.quantity
            order.medicine.save()

            if order.cart_item:
                order.cart_item.delete()

            return render(request, 'pharmacy/esewa_success.html', {
                'order':         order,
                'response_data': response_data,
            })
        else:
            messages.error(request, "Payment was not completed.")
            return redirect('cart')

    except Exception as e:
        messages.error(request, f"Payment verification failed: {str(e)}")
        return redirect('cart')


def esewa_failure(request):

    return render(request, 'pharmacy/esewa_failure.html')



@login_required
def create_bill(request):
    if request.method == 'POST':
        medicine_ids   = request.POST.getlist('medicine_id')
        quantities     = request.POST.getlist('quantity')
        customer_name  = request.POST.get('customer_name', 'Walk-in Customer')
        customer_phone = request.POST.get('customer_phone', '')

        if not medicine_ids:
            messages.error(request, "Add at least one medicine.")
            return redirect('create_bill')

    
        bill = Bill.objects.create(
            bill_number    = f"BILL-{uuid.uuid4().hex[:8].upper()}",
            pharmacist     = request.user,
            customer_name  = customer_name,
            customer_phone = customer_phone,
        )
        total = 0
        for med_id, qty in zip(medicine_ids, quantities):
            try:
                med = Medicine.objects.get(pk=med_id)
                qty = int(qty)
                if qty > 0 and med.stock_quantity >= qty:
                    BillItem.objects.create(
                        bill=bill, medicine=med,
                        quantity=qty, unit_price=med.price)
                    med.stock_quantity -= qty
                    med.save()
                    total += qty * med.price
            except Medicine.DoesNotExist:
                pass
        bill.total_amount = total
        bill.save()
        messages.success(request, f"Bill #{bill.bill_number} created!")
        return redirect('bill_invoice', pk=bill.pk)

    medicines = Medicine.objects.filter(stock_quantity__gt=0)
    return render(request, 'pharmacy/billing.html', {'medicines': medicines})


@login_required
def bill_list(request):
    bills = Bill.objects.select_related('pharmacist').order_by('-created_at')
    if request.GET.get('date'):
        bills = bills.filter(created_at__date=request.GET['date'])
    if request.GET.get('today'):
        bills = bills.filter(created_at__date=date.today())
    return render(request, 'pharmacy/bill_list.html', {
        'bills': bills,
        'total': bills.aggregate(t=Sum('total_amount'))['t'] or 0,
    })


@login_required
def bill_invoice(request, pk):
    bill  = get_object_or_404(Bill, pk=pk)
    items = bill.billitem_set.select_related('medicine').all()
    return render(request, 'pharmacy/bill_invoice.html', {'bill': bill, 'items': items})



@login_required
@admin_required
def reports(request):
    today   = date.today()
    last_7  = today - timedelta(days=7)
    last_30 = today - timedelta(days=30)
    daily_sales = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        t   = Bill.objects.filter(created_at__date=day).aggregate(
                  t=Sum('total_amount'))['t'] or 0
        daily_sales.append({'date': day.strftime('%d %b'), 'total': float(t)})
    return render(request, 'pharmacy/reports.html', {
        'today_revenue':  Bill.objects.filter(created_at__date=today).aggregate(t=Sum('total_amount'))['t'] or 0,
        'week_revenue':   Bill.objects.filter(created_at__date__gte=last_7).aggregate(t=Sum('total_amount'))['t'] or 0,
        'month_revenue':  Bill.objects.filter(created_at__date__gte=last_30).aggregate(t=Sum('total_amount'))['t'] or 0,
        'total_revenue':  Bill.objects.aggregate(t=Sum('total_amount'))['t'] or 0,
        'daily_sales':    daily_sales,
        'top_medicines':  BillItem.objects.values('medicine__name').annotate(
        total_sold=Sum('quantity')).order_by('-total_sold')[:5],
    })


@login_required
@admin_required
def user_list(request):
    return render(request, 'pharmacy/user_list.html',
                  {'users': User.objects.all().order_by('role')})


@login_required
@admin_required
def user_create(request):
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "User created!")
        return redirect('user_list')
    return render(request, 'pharmacy/user_form.html',
                  {'form': form, 'title': 'Create User'})


@login_required
def get_medicine_price(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    return JsonResponse({'price': float(medicine.price),
    'stock': medicine.stock_quantity,
    'name':  medicine.name})