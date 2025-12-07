import json
from django import forms
from .models import mcq

class MCQAdminForm(forms.ModelForm):
    # hidden field that will carry the JSON list of options
    options_json = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = mcq
        fields = ['question', 'correct_answer', 'options_json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If editing an instance, populate the hidden field so JS can read it
        if self.instance and hasattr(self.instance, 'options'):
            try:
                self.fields['options_json'].initial = json.dumps(self.instance.options)
            except Exception:
                self.fields['options_json'].initial = '[]'

    def clean(self):
        cleaned = super().clean()
        options_json = cleaned.get('options_json', '[]') or '[]'
        try:
            options = json.loads(options_json)
        except Exception:
            raise forms.ValidationError("Options JSON malformed.")
        # ensure options is a list of non-empty strings
        clean_opts = [str(o).strip() for o in options if str(o).strip() != '']
        if not clean_opts:
            raise forms.ValidationError("Please provide at least one option.")
        # If correct_answer exists, ensure it's one of the options
        correct = cleaned.get('correct_answer', '').strip()
        if correct and correct not in clean_opts:
            # if correct isn't in list, we'll clear it (or you can raise)
            cleaned['correct_answer'] = ''
        # attach options list to cleaned data so save() can use it
        cleaned['options'] = clean_opts
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        # form.clean() guaranteed to put 'options'
        obj.options = self.cleaned_data.get('options', [])
        # ensure correct_answer remains valid: if not, clear it
        if obj.correct_answer and obj.correct_answer not in obj.options:
            obj.correct_answer = ''
        if commit:
            obj.save()
        return obj
