from django.http import HttpResponse
from django.utils.html import format_html
from django.views.generic import View
from django.utils.translation import ugettext_lazy as _
from django_multisafepay.client import MultiSafepayClient
from django_multisafepay.signals import order_status_changed


class OrderNotifyView(View):
    """
    View to be called by MultiSafepay when a status update occured.
    """
    return_link_text = _('Return to webshop')


    def get(self, request, *args, **kwargs):
        self.transaction_id = request.GET['transactionid']
        self.type = request.GET['type']

        # Request the new status from the server.
        client = MultiSafepayClient()
        statusreply = client.status(self.transaction_id)

        # Let the project update the status
        order_status_changed.send(self.__class__, response=statusreply)

        if self.type == 'initial':
            # displayed at the last page of the transaction proces (if no redirect_url is set)
            url = request.build_absolute_uri('/')
            return HttpResponse(format_html(u'<a href="{0}">{1}</a>', url, self.return_link_text))
        else:
            # MultiSafepay back-end expects an "ok" if no error occurred
            return HttpResponse('ok')
