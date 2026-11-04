from django import forms

from posts.models import Comentario


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ["nome", "texto"]
