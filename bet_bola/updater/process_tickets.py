from ticket.models import Ticket
from django.db.models import Q


def process_tickets(tickets=None):
    if not tickets:
        tickets = Ticket.objects.filter(status=0)

    for ticket in tickets:
        print("Processing Ticket: "+ str(ticket.ticket_id))
        valid_cotations = ticket.cotations.filter(game__status__in=[0,1,2,3])
        if valid_cotations.filter(settlement=1):
            ticket.status = 1
            ticket.save()
            return None
        if valid_cotations.filter(settlement=0):
            return None
        if not valid_cotations.filter(~Q(settlement=2)):
            if ticket.payment.status == 2:
                ticket.status = 4
                ticket.save()
            else:
                ticket.status = 3
                ticket.save()

