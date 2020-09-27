from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
# from cgi import escape
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib import admin
from galleryIs.models import Template, Genre, Author, Refurbishment, Painting, Exhibition, Report
import io
from django.conf import settings
from django.http import FileResponse
from reportlab.pdfgen import canvas

# Register your models here.

class RefurbishmentInLine(admin.TabularInline):
    model = Refurbishment
    extra = 0
    readonly_fields = ('state', 'startDT', 'endDT', 'painting')

class AuthorAdmin(admin.ModelAdmin):
    ordering = ['birthday']
    search_fields = ['fullName']

class GenreAdmin(admin.ModelAdmin):
    search_fields = ['title']

class PaintingInLine(admin.TabularInline):
    model = Painting
    extra = 0
    readonly_fields = ('*')


class ExhibitionForm(forms.ModelForm):
    paintings = forms.ModelMultipleChoiceField(
          queryset=Painting.objects.all(),
          required=False,
          widget=FilteredSelectMultiple(
              verbose_name='Paintings',
              is_stacked=False
          )
    )

    def __init__(self, *args, **kwargs):
        super(ExhibitionForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['paintings'].initial = self.instance.paintings.all()
    
    def save(self, commit=True):
        return forms.BaseModelForm.save(self, commit=commit)

    class Meta:
        exclude = ['genres']
        model = Painting

class ExhibitionAdmin(admin.ModelAdmin):
    # autocomplete_fields = ['paintings']
    # filter_horizontal = ('paintings')
    form = ExhibitionForm

class PaintingAdmin(admin.ModelAdmin):
    model = Painting
    inlines = (RefurbishmentInLine,)
    autocomplete_fields = ['authors', 'genres']
    search_fields = ['title','authors']
    
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    ...
    change_form_template = "admin/report_to_pdf.html"


    def response_change(self, request, obj):
        if "_print_pdf" in request.POST:
            template = obj.template.template.path.split('/')[-1]
            exhibition = Exhibition.objects.filter(theme=obj.exhibition.theme)
            ctx = {
                'pagesize':'A4',
                'exhibition_title':obj.exhibition.theme,
                'visitor_qty':obj.visitorsQTY,
                'paintings': exhibition
            }
            return render_to_pdf(template, ctx)

            # return HttpResponse(pdf, content_type='application/pdf')  
            # return FileResponse(pdf, as_attachment=True, filename='hello.pdf')
        return super().response_change(request, obj)

def fetch_pdf_resources(uri, rel):
    if uri.find(settings.MEDIA_URL) != -1:
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    elif uri.find(settings.STATIC_URL) != -1:
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ''))
    else:
        path = None
    return path    

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html  = template.render(context_dict)
    result = io.BytesIO()

    pdf = pisa.pisaDocument(io.BytesIO(html.encode('UTF-8')),
     result, encodind = 'utf-8', link_callback=fetch_pdf_resources)

    if not pdf.err:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'
        response.write(result.getvalue())
        return response
    return None

admin.site.register(Genre, GenreAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Refurbishment)
admin.site.register(Painting, PaintingAdmin)
admin.site.register(Exhibition, ExhibitionAdmin)
admin.site.register(Template)
