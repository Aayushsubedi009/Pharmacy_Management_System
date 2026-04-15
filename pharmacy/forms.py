# pharmacy/forms.py

from django import forms
from .models import Medicine, User


class MedicineForm(forms.ModelForm):
    class Meta:
        model  = Medicine
        fields = ['name','category','price','stock_quantity',
                  'expiry_date','manufacturer','description',
                  'low_stock_threshold','image']
        widgets = {
            'name':                forms.TextInput(attrs={'class':'form-control'}),
            'category':            forms.Select(attrs={'class':'form-select'}),
            'price':               forms.NumberInput(attrs={'class':'form-control','step':'0.01'}),
            'stock_quantity':      forms.NumberInput(attrs={'class':'form-control'}),
            'expiry_date':         forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'manufacturer':        forms.TextInput(attrs={'class':'form-control'}),
            'description':         forms.Textarea(attrs={'class':'form-control','rows':3}),
            'low_stock_threshold': forms.NumberInput(attrs={'class':'form-control'}),
            'image':               forms.ClearableFileInput(attrs={'class':'form-control'}),
        }


class UserCreateForm(forms.ModelForm):
    password         = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control'}))
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control'}))

    class Meta:
        model  = User
        fields = ['username','email','role','password']
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'email':    forms.EmailInput(attrs={'class':'form-control'}),
            'role':     forms.Select(attrs={'class':'form-select'}),
        }

    def clean(self):
        cd = super().clean()
        if cd.get('password') != cd.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match.")
        return cd

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


# ── NEW: Order Form (for eSewa checkout) ──────
class OrderForm(forms.Form):
    """
    Shown when user clicks 'Order Now' from cart.
    Collects delivery address, contact, and payment method.
    """
    PAYMENT_CHOICES = [
        ('esewa', 'Pay with eSewa'),
        ('cash',  'Cash on Delivery'),
    ]

    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class':       'form-control',
            'rows':        2,
            'placeholder': 'Enter your delivery address',
        }),
        label='Delivery Address'
    )

    contact_no = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class':       'form-control',
            'placeholder': '98XXXXXXXX',
        }),
        label='Contact Number'
    )

    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect(),
        label='Payment Method',
        initial='esewa'
    )