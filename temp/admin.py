from django.contrib import admin
from .models import Student,Course,authors,books,mcq

# admin.site.register(MediaFile)
# admin.site.register(AudioFile)
# admin.site.register(Student)
# admin.site.register(Course)
# admin.site.register(authors)

from django.contrib import admin
from .models import Product

from django import forms
from django.contrib import admin
from .models import Product
import json

class ProductForm(forms.ModelForm):
    metadata = forms.JSONField(required=False, widget=forms.Textarea(attrs={'rows':6, 'cols':80}))

    class Meta:
        model = Product
        fields = '__all__'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ('name', 'price', 'pretty_metadata')

    def pretty_metadata(self, obj):
        try:
            return json.dumps(obj.metadata, indent=2)[:200]  # সীমিত দেখাবে
        except Exception:
            return str(obj.metadata)
    pretty_metadata.short_description = "Metadata (preview)"

from django import forms
from .models import books , a,Chapter


# class b(admin.TabularInline):
#     model = books
#     extra = 2
#     inlines =[A]

# class B(admin.ModelAdmin):
#     inlines = [A]

# admin.site.register(books, B)
# class authorsAdmin(admin.ModelAdmin):
#     inlines =[b]

# admin.site.register(authors, authorsAdmin)
import nested_admin
class A(nested_admin.NestedTabularInline):
    model = a
    extra = 2
class c(nested_admin.NestedTabularInline):
    model = Chapter
    extra = 2

class b(nested_admin.NestedTabularInline):
    model = books 
    extra=1
    inlines =[c,A]
class a(nested_admin.NestedModelAdmin):
    inlines =[b]
admin.site.register(authors, a)

