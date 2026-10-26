from django import forms
from django.contrib.auth.models import User
from .models import Project, ProjectMember


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Project name'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Project description (optional)'}),
        }


class AddMemberForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Enter username to add'})
    )
    role = forms.ChoiceField(choices=ProjectMember.ROLE_CHOICES)

    def __init__(self, project, *args, **kwargs):
        self.project = project
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(f"User '{username}' does not exist.")
        if self.project.is_member(user):
            raise forms.ValidationError(f"User '{username}' is already a member of this project.")
        return username
