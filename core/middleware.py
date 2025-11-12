
from django.utils.deprecation import MiddlewareMixin
class LanguageSwitcherMiddleware(MiddlewareMixin):
    def process_request(self, request):
        lang = request.GET.get('lang')
        if lang in ('en','fr'):
            request.session['lang'] = lang
