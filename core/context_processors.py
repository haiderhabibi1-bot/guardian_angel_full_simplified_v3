
def site_lang(request):
    return {'lang': request.session.get('lang','en')}
