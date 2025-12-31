from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="Parolă", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmă parola", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "company_name", "company_cif"]

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise forms.ValidationError("Parolele nu coincid.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = User.Role.CLIENT
        user.is_active = False  # pending approval
        if commit:
            user.save()
        return user
