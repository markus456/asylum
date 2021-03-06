# -*- coding: utf-8 -*-
import calendar
import datetime
import logging

import environ
from creditor.handlers import BaseRecurringTransactionsHandler, BaseTransactionHandler
from creditor.models import Transaction, TransactionTag
from django.core.mail import EmailMessage
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from examples.utils import get_holvi_singleton
from members.handlers import BaseApplicationHandler, BaseMemberHandler

from .utils import get_nordea_payment_reference

logger = logging.getLogger('hhlcallback.handlers')
env = environ.Env()


class ApplicationHandler(BaseApplicationHandler):
    fresh_emails = {}

    def on_saving(self, instance, *args, **kwargs):
        """Called just before passing control to save()"""
        if not instance.pk:
            self.fresh_emails[instance.email] = True

    def on_saved(self, instance, *args, **kwargs):
        """Called after save() returns"""
        if instance.email in self.fresh_emails:
            # Just created
            del(self.fresh_emails[instance.email])
            mail = EmailMessage()
            mail.from_email = '"%s" <%s>' % (instance.name, instance.email)
            mail.to = ["hallitus@helsinki.hacklab.fi", ]
            mail.subject = "Jäsenhakemus: %s" % instance.name
            mail.body = "Uusi hakemus Asylumissa: https://lataamo.hacklab.fi/admin/members/membershipapplication/%d/" % instance.pk
            mail.send()
        pass

    def on_approved(self, application, member):
        rest_of_year_free = False
        fee_msg_fi = "Jäsenmaksusta tulee sinulle erillinen viesti."
        fee_msg_en = "You will receive a separate message about membership fee."
        # If application was received in Q4, rest of this year is free
        if application.received.month >= 10:
            rest_of_year_free = True
            fee_msg_fi = "Vuoden %s jäsenmaksua ei peritä." % application.received.year
            fee_msg_en = "Membership fee for year %s has been waived." % application.received.year

        # Auto-add the membership fee as recurring transaction
        membership_fee = env.float('HHL_MEMBERSHIP_FEE', default=None)
        membership_tag = 1
        if membership_fee and membership_tag:
            from creditor.models import RecurringTransaction, TransactionTag
            rt = RecurringTransaction()
            rt.tag = TransactionTag.objects.get(pk=membership_tag)
            rt.owner = member
            rt.amount = -membership_fee
            rt.rtype = RecurringTransaction.YEARLY
            # If application was received in Q4 set the recurringtransaction to start from next year
            if rest_of_year_free:
                rt.start = datetime.date(year=application.received.year + 1, month=1, day=1)
            rt.save()
            rt.conditional_add_transaction()

        # Subscribe to mailing list
        mailman_subscribe = env('HHL_MAILMAN_SUBSCRIBE', default=None)
        if mailman_subscribe:
            mail = EmailMessage()
            mail.from_email = member.email
            mail.to = [mailman_subscribe, ]
            mail.subject = 'subscribe'
            mail.body = 'subscribe'
            mail.send()

        # Welcome-email
        mail = EmailMessage()
        mail.to = [member.email, ]
        mail.from_email = "hallitus@helsinki.hacklab.fi"
        mail.subject = "Helsinki Hacklabin jäsenhakemus hyväksytty! | Your membership application has been approved!"
        mail.body = """Tervetuloa Helsinki Hacklabin jäseneksi!

Jäsenenä olet tervetullut kaikkiin Helsinki Hacklabin tilaisuuksiin, kuten tiistaisiin jäseniltoihin, torstaisiin kurssipäiviin, sekä muihin järjestettäviin tapahtumiin.

Sähköisesti hacklabilaisten kanssa voi keskustella Suomen hacklabien foorumilla (https://discourse.hacklab.fi/), sekä IRC kanavallamme #helsinki.hacklab.fi Freenode-verkossa.

{fee_msg_fi}

Jos sinulla on jäsenyyteen tai tähän viestiin liittyviä kysymyksiä, voit lähettää ne Helsinki Hacklabin hallitukselle vastaamalla tähän viestiin tai lähettämällä viestin osoitteeseen hallitus@helsinki.hacklab.fi

----

Helsinki Hacklab welcomes you as a member!

As a member you are most welcome to attend all events organised by Helsinki Hacklab. These include the weekly member gathering every Tuesday, our courses and workshops held on Thurdays and other events we might come up with.

Electronic communication between our members is handled forum of finnish hacklabs (https://discourse.hacklab.fi/) and on our IRC channel #helsinki.hacklab.fi @ Freenode.

{fee_msg_en}

For questions regarding your membership or this message, please contact the board of Helsinki Hacklab at hallitus@helsinki.hacklab.fi or simply reply to this message.

""".format(fee_msg_fi=fee_msg_fi, fee_msg_en=fee_msg_en)
        mail.send()



class RecurringTransactionsHolviHandler(BaseRecurringTransactionsHandler):
    category_maps = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        HOLVI_CNC = get_holvi_singleton()
        if HOLVI_CNC:
            import holviapi
            caa = holviapi.CategoriesAPI(HOLVI_CNC)
            self.category_maps = {  # Keyed by tag pk
                1: caa.get_category('101ea72cbfadf52d4f7684a52bdb8947'),  # Membership feee
                2: caa.get_category('7ac3020b14d926e5f0c6fb005f0457ac'),  # Keyholder fee
            }

    def on_creating(self, rt, t, *args, **kwargs):
        # Only negative amounts go to invoices
        if t.amount >= 0.0:
            return True
        if t.tag.pk == 1:  # Membership feee
            return self.make_membershipfee_invoice(rt, t)
        if t.tag.pk == 2:  # Keyholder feee
            t.reference = get_nordea_payment_reference(t.owner.member_id, int(t.tag.tmatch))
        return True

    def make_membershipfee_invoice(self, rt, t):
        HOLVI_CNC = get_holvi_singleton()
        if not HOLVI_CNC:
            return True

        import holviapi
        invoice_api = holviapi.InvoiceAPI(HOLVI_CNC)
        invoice = holviapi.Invoice(invoice_api)
        invoice.receiver = holviapi.contacts.InvoiceContact({
            'email': t.owner.email,
            'name': t.owner.name,
        })
        invoice.items.append(holviapi.InvoiceItem(invoice))
        if t.stamp:
            year = t.stamp.year
        else:
            year = datetime.datetime.now().year
        invoice.items[0].description = "%s %s" % (t.tag.label, year)
        invoice.items[0].net = -t.amount  # Negative amount transaction -> positive amount invoice
        invoice.items[0].category = self.category_maps[1]
        invoice.subject = "%s / %s" % (invoice.items[0].description, invoice.receiver.name)
        invoice = invoice.save()
        invoice.send()
        t.reference = invoice.rf_reference
        return True


class TransactionHandler(BaseTransactionHandler):

    def __init__(self, *args, **kwargs):
        # We have to do this late to avoid problems with circular imports
        from members.models import Member
        self.memberclass = Member
        self.try_methods = [
            self.import_generic_transaction,
            self.import_legacy_transaction,
        ]
        super().__init__(*args, **kwargs)

    def import_transaction(self, at):
        # We only care about transactions with reference numbers
        if not at.reference:
            return None

        # If local transaction exists, return as-is
        lt = at.get_local()
        if lt.pk:
            return lt

        # We have few importers to try
        for m in self.try_methods:
            new_lt = m(at, lt)
            if new_lt is not None:
                return new_lt
        # Nothing worked, return None
        return None

    def import_generic_transaction(self, at, lt):
        """Look for a transaction with same reference but oppsite value. If found use that for owner and tag"""
        qs = Transaction.objects.filter(reference=at.reference, amount=-at.amount).order_by('-stamp')
        if not qs.count():
            return None
        base = qs[0]
        lt.tag = base.tag
        lt.owner = base.owner
        lt.save()
        return lt

    def import_legacy_transaction(self, at, lt):
        """Look at the reference number and use it to find owner and tag if it matches our old reference format"""
        # Last meaningful number (last number is checksum) of the reference is used to recognize the TransactionTag
        if len(at.reference) < 2: # Jus so we do not get indexerrors from empty references or something
            return None
        if at.reference[0:2] == "RF":
            return None
        try:
            lt.tag = TransactionTag.objects.get(tmatch=at.reference[-2])
        except TransactionTag.DoesNotExist:
            # No tag matched, skip...
            return None
        # Numbers up to the tag identifier in the reference is the member_id + 1000
        try:
            lt.owner = self.memberclass.objects.get(member_id=(int(at.reference[0:-2], 10) - 1000))
        except self.memberclass.DoesNotExist:
            # No member matched, skip...
            return None

        # Rest of the fields are directly mapped already by get_local()
        lt.save()
        return lt

    def __str__(self):
        return str(_("Helsinki Hacklab ry transactions handler"))
