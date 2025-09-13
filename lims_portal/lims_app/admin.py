from django.contrib import admin
from .models import Reader, Book, Borrowing,User
from django.contrib.auth.admin import UserAdmin

# Custom User Admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone', 'address')}),
    )


#  Reader Admin 
@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ['reference_id', 'reader_name', 'reader_contact', 'active']
    search_fields = ['reference_id', 'reader_name', 'reader_contact']
    list_filter = ['active']
    list_editable = ['reader_contact']
    list_per_page = 5


#  Book Admin 
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'genre', 'available_quantity']
    search_fields = ['title', 'author', 'genre']
    list_filter = ['genre']
    list_per_page = 5


#  Borrowing Admin 
@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = ['member', 'book', 'borrowed_on', 'due_date']    
    #   search inside related fields
    search_fields = ['member__reader_name', 'member__reference_id', 'book__title', 'book__author']
    list_filter = ['borrowed_on', 'due_date', 'book__genre']
    list_per_page = 5
