from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.admin.sites import NotRegistered
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from .models import Department, Group, Student, Teacher, User


for model in (AuthGroup, OutstandingToken, BlacklistedToken):
    try:
        admin.site.unregister(model)
    except NotRegistered:
        pass


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'last_name', 'first_name', 'middle_name', 'contacts', 'role')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(required=False)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'last_name',
            'first_name',
            'middle_name',
            'contacts',
            'role',
            'is_active',
            'is_staff',
            'is_superuser',
        )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    ordering = ('username',)
    list_display = ('username', 'email', 'last_name', 'first_name', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'last_name', 'first_name', 'middle_name')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('last_name', 'first_name', 'middle_name', 'contacts', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'last_name',
                    'first_name',
                    'middle_name',
                    'contacts',
                    'role',
                    'password1',
                    'password2',
                    'is_staff',
                    'is_superuser',
                ),
            },
        ),
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('number',)
    search_fields = ('number',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'group_number')
    search_fields = ('user__email', 'user__last_name', 'user__first_name', 'group_number__number')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'student_limit', 'is_norm_controller')
    list_filter = ('is_norm_controller',)
    search_fields = ('user__email', 'user__last_name', 'user__first_name', 'department__name')
