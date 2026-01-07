from django.db import transaction

def allocate_number(doc_type):
    """
    Alocă un număr unic (safe în concurență).
    Ex: OL-00001
    """
    Model = doc_type.__class__
    with transaction.atomic():
        locked = Model.objects.select_for_update().get(pk=doc_type.pk)
        num = locked.next_number
        locked.next_number += 1
        locked.save(update_fields=["next_number"])
    return f"{locked.series}-{num:05d}"
