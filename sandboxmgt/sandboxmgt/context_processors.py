def govuk_overrides(request):
    from django.conf import settings
    from django.utils.translation import ugettext as _
    return {
        'homepage_url': '/',
        'logo_link_title': 'Go to the GOV.UK homepage',
    }
