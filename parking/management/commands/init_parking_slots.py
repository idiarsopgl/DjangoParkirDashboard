from django.core.management.base import BaseCommand
from parking.models import ParkingSlot

class Command(BaseCommand):
    help = 'Initialize parking slots with default values'

    def handle(self, *args, **options):
        # Define initial slots
        initial_slots = [
            # Car slots (A1-A10)
            *[('A' + str(i), 'CAR') for i in range(1, 11)],
            
            # Motorcycle slots (B1-B20)
            *[('B' + str(i), 'MOTORCYCLE') for i in range(1, 21)],
            
            # Truck slots (C1-C5)
            *[('C' + str(i), 'TRUCK') for i in range(1, 6)],
        ]

        slots_created = 0
        slots_skipped = 0

        for slot_number, slot_type in initial_slots:
            # Check if slot already exists
            if not ParkingSlot.objects.filter(slot_number=slot_number).exists():
                ParkingSlot.objects.create(
                    slot_number=slot_number,
                    slot_type=slot_type
                )
                slots_created += 1
            else:
                slots_skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {slots_created} parking slots '
                f'(skipped {slots_skipped} existing slots)'
            )
        )
