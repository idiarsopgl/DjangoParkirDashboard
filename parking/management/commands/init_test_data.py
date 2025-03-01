from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from parking.models import ParkingOperator, Shift, ShiftLog
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Initialize test data for parking operators, shifts, and logs'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')

        # Create test operators
        operators_data = [
            {
                'username': 'operator1',
                'password': 'parkir123',
                'first_name': 'Budi',
                'last_name': 'Santoso',
                'email': 'budi@parking.com',
                'employee_id': 'EMP001',
                'phone_number': '081234567890',
                'address': 'Jl. Sudirman No. 123, Jakarta'
            },
            {
                'username': 'operator2',
                'password': 'parkir123',
                'first_name': 'Dewi',
                'last_name': 'Sari',
                'email': 'dewi@parking.com',
                'employee_id': 'EMP002',
                'phone_number': '081234567891',
                'address': 'Jl. Thamrin No. 456, Jakarta'
            },
            {
                'username': 'operator3',
                'password': 'parkir123',
                'first_name': 'Ahmad',
                'last_name': 'Hidayat',
                'email': 'ahmad@parking.com',
                'employee_id': 'EMP003',
                'phone_number': '081234567892',
                'address': 'Jl. Gatot Subroto No. 789, Jakarta'
            }
        ]

        operators = []
        for op_data in operators_data:
            # Create User
            user = User.objects.create_user(
                username=op_data['username'],
                email=op_data['email'],
                password=op_data['password'],
                first_name=op_data['first_name'],
                last_name=op_data['last_name']
            )
            
            # Create ParkingOperator
            operator = ParkingOperator.objects.create(
                user=user,
                employee_id=op_data['employee_id'],
                phone_number=op_data['phone_number'],
                address=op_data['address']
            )
            operators.append(operator)
            self.stdout.write(f'Created operator: {operator}')

        # Create shifts for the past week
        shift_types = ['pagi', 'siang', 'malam']
        shift_times = {
            'pagi': {'start': '06:00', 'end': '14:00'},
            'siang': {'start': '14:00', 'end': '22:00'},
            'malam': {'start': '22:00', 'end': '06:00'}
        }

        today = timezone.now().date()
        for i in range(7):  # Past week
            date = today - timedelta(days=i)
            for shift_type in shift_types:
                operator = random.choice(operators)
                times = shift_times[shift_type]
                
                shift = Shift.objects.create(
                    operator=operator,
                    shift_type=shift_type,
                    date=date,
                    start_time=datetime.strptime(times['start'], '%H:%M').time(),
                    end_time=datetime.strptime(times['end'], '%H:%M').time()
                )

                # Create shift log with random data
                if date < today:  # Only create logs for past shifts
                    transactions = random.randint(10, 50)
                    revenue = transactions * random.randint(5000, 20000)
                    
                    check_in = datetime.combine(date, shift.start_time) + timedelta(minutes=random.randint(-15, 15))
                    check_out = datetime.combine(date, shift.end_time) + timedelta(minutes=random.randint(-15, 15))
                    
                    ShiftLog.objects.create(
                        shift=shift,
                        check_in=check_in,
                        check_out=check_out,
                        total_transactions=transactions,
                        total_revenue=revenue,
                        notes=f'Shift berjalan normal. {transactions} transaksi.'
                    )
                    self.stdout.write(f'Created shift and log for {operator} on {date} ({shift_type})')

        self.stdout.write(self.style.SUCCESS('Successfully created test data'))
