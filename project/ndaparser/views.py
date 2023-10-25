# -*- coding: utf-8 -*-
import os
import tempfile

from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from django.core.exceptions import ValidationError

from .forms import UploadForm
from .importer import NDAImporter, CSVImporter
from .models import UploadedTransaction
from .parser import parseLine, parseCsv


class NordeaUploadView(FormView):
    form_class = UploadForm
    template_name = "ndaparser/admin/upload.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.kwargs['context'])
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        is_csv = True
        uploaded_file = self.request.FILES['csvfile']

        if not uploaded_file:
            is_csv = False
            uploaded_file = self.request.FILES['ndafile']

        # We have to write out the file in binary mode before we properly parse it by lines
        tmp = tempfile.NamedTemporaryFile(prefix="ndaupload", delete=False)
        with tmp as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)

        transactions_handler = context['transactions_handler']
        transactions = []
        with open(tmp.name) as f:
            if is_csv:
                h = CSVImporter(f)
            else:
                h = NDAImporter(f)
            transactions = h.import_transactions(transactions_handler)

        # parse the file again for the last transaction timestamp
        last_stamp = None
        with open(tmp.name) as fp:
            if is_csv:
                last_stamp = max([t.timestamp for t in parseCsv(fp)])
            else:
                for line in fp:
                    nt = parseLine(line)
                    if not nt:
                        continue
                    if not last_stamp:
                        last_stamp = nt.timestamp
                    if nt.timestamp > last_stamp:
                        last_stamp = nt.timestamp

        try:
            UploadedTransaction(
                last_transaction=last_stamp,
                file=uploaded_file,
                user=self.request.user
            ).save()

            context['title'] = _("Transactions uploaded")
            context['transactions'] = transactions
        except ValidationError:
            context['error'] = _("Invalid NDA document")

        # Done with the temp file, get rid of it
        os.unlink(tmp.name)

        return self.render_to_response(context)
