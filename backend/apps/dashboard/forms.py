"""Dashboard forms."""

from django import forms
from apps.products.models import Product, Category, ProductImage
from apps.store.models import StoreSettings


class ProductForm(forms.ModelForm):
    images = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={"accept": "image/*"}),
        label="Foto Produk",
    )

    class Meta:
        model = Product
        fields = ["name", "category", "price", "description", "is_active", "is_featured"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "dash-form__input"}),
            "category": forms.Select(attrs={"class": "dash-form__select"}),
            "price": forms.NumberInput(attrs={"class": "dash-form__input", "min": 0}),
            "description": forms.Textarea(attrs={"class": "dash-form__textarea", "rows": 4}),
        }

    def save(self, commit=True):
        product = super().save(commit=False)
        if commit:
            product.save()
            # Handle image uploads
            images = self.files.getlist("images")
            for idx, img_file in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image_url=img_file,
                    alt_text=product.name,
                    sort_order=idx,
                )
        return product


class StoreSettingsForm(forms.ModelForm):
    class Meta:
        model = StoreSettings
        fields = ["store_name", "description", "shipping_cost", "whatsapp_number",
                  "instagram_handle", "email_contact"]
        widgets = {
            "store_name": forms.TextInput(attrs={"class": "dash-form__input"}),
            "description": forms.Textarea(attrs={"class": "dash-form__textarea", "rows": 3}),
            "shipping_cost": forms.NumberInput(attrs={"class": "dash-form__input", "min": 0}),
            "whatsapp_number": forms.TextInput(attrs={"class": "dash-form__input", "placeholder": "081234567890"}),
            "instagram_handle": forms.TextInput(attrs={"class": "dash-form__input", "placeholder": "@username"}),
            "email_contact": forms.EmailInput(attrs={"class": "dash-form__input"}),
        }
