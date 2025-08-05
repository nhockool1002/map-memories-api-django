from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from faker import Faker
import random
import base64
from decimal import Decimal

from accounts.models import User
from locations.models import Location
from memories.models import Memory, MemoryLike
from media.models import MediaFile
from shop.models import ShopItem, UserItem, TransactionLog

fake = Faker()

# Sample base64 image (1x1 pixel PNG)
SAMPLE_IMAGE_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Number of users to create (default: 20)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        users_count = options['users']
        
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()
        
        self.stdout.write('Starting data seeding...')
        
        with transaction.atomic():
            # Create admin user
            admin_user = self.create_admin_user()
            
            # Create shop items
            shop_items = self.create_shop_items()
            
            # Create regular users
            users = self.create_users(users_count)
            
            # Create locations and memories
            self.create_locations_and_memories(users, shop_items)
            
            # Create user items and transactions
            self.create_user_items_and_transactions(users, shop_items, admin_user)
            
            # Create likes
            self.create_memory_likes(users)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded database with:\n'
                f'- 1 admin user (admin@admin.com)\n'
                f'- {users_count} regular users\n'
                f'- {len(shop_items)} shop items\n'
                f'- Sample locations, memories, and media files\n'
            )
        )

    def clear_data(self):
        """Clear existing data"""
        User.objects.filter(username__startswith='user_').delete()
        User.objects.filter(email='admin@admin.com').delete()
        Location.all_objects.all().hard_delete()
        Memory.all_objects.all().hard_delete()
        MediaFile.all_objects.all().hard_delete()
        ShopItem.all_objects.all().hard_delete()
        UserItem.all_objects.all().hard_delete()
        TransactionLog.objects.all().delete()

    def create_admin_user(self):
        """Create admin user"""
        admin_user, created = User.objects.get_or_create(
            email='admin@admin.com',
            defaults={
                'username': 'admin',
                'is_admin': True,
                'is_staff': True,
                'is_superuser': True,
                'full_name': 'System Administrator',
                'currency': 1000000,  # 1 million Xu for admin
            }
        )
        
        if created:
            admin_user.set_password('admin')
            admin_user.save()
            self.stdout.write(f'Created admin user: admin@admin.com (password: admin)')
        else:
            self.stdout.write('Admin user already exists')
        
        return admin_user

    def create_shop_items(self):
        """Create sample shop items"""
        shop_items_data = [
            {
                'name': 'Red Star Marker',
                'description': 'Beautiful red star marker for special locations',
                'price': 1000,
                'stock': 50,
                'item_type': 'marker'
            },
            {
                'name': 'Blue Diamond Marker',
                'description': 'Elegant blue diamond marker for premium locations',
                'price': 1500,
                'stock': 30,
                'item_type': 'marker'
            },
            {
                'name': 'Green Heart Marker',
                'description': 'Lovely green heart marker for romantic spots',
                'price': 800,
                'stock': 100,
                'item_type': 'marker'
            },
            {
                'name': 'Golden Crown Marker',
                'description': 'Luxurious golden crown marker for royal experiences',
                'price': 2500,
                'stock': 20,
                'item_type': 'marker'
            },
            {
                'name': 'Rainbow Theme',
                'description': 'Colorful rainbow theme for your memory map',
                'price': 3000,
                'stock': 25,
                'item_type': 'theme'
            }
        ]
        
        shop_items = []
        for item_data in shop_items_data:
            shop_item, created = ShopItem.objects.get_or_create(
                name=item_data['name'],
                defaults={
                    **item_data,
                    'image_base64': SAMPLE_IMAGE_BASE64
                }
            )
            shop_items.append(shop_item)
            
            if created:
                self.stdout.write(f'Created shop item: {shop_item.name}')
        
        return shop_items

    def create_users(self, count):
        """Create regular users"""
        users = []
        for i in range(count):
            username = f'user_{i+1:03d}'
            email = f'user{i+1:03d}@example.com'
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'full_name': fake.name(),
                    'currency': random.randint(0, 10000),
                    'is_admin': False
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                users.append(user)
        
        self.stdout.write(f'Created {len(users)} regular users')
        return users

    def create_locations_and_memories(self, users, shop_items):
        """Create locations and memories with 1-1 relationship"""
        countries = ['Vietnam', 'USA', 'Japan', 'France', 'Germany', 'Australia']
        cities = {
            'Vietnam': ['Hanoi', 'Ho Chi Minh City', 'Da Nang', 'Hoi An'],
            'USA': ['New York', 'Los Angeles', 'Chicago', 'Miami'],
            'Japan': ['Tokyo', 'Osaka', 'Kyoto', 'Hiroshima'],
            'France': ['Paris', 'Lyon', 'Marseille', 'Nice'],
            'Germany': ['Berlin', 'Munich', 'Hamburg', 'Cologne'],
            'Australia': ['Sydney', 'Melbourne', 'Brisbane', 'Perth']
        }
        
        memory_count = 0
        location_count = 0
        
        for user in users:
            # Each user creates 2-5 memories
            num_memories = random.randint(2, 5)
            
            for _ in range(num_memories):
                country = random.choice(countries)
                city = random.choice(cities[country])
                
                # Create location first
                location = Location.objects.create(
                    user=user,
                    name=fake.sentence(nb_words=3).replace('.', ''),
                    description=fake.text(max_nb_chars=200),
                    latitude=Decimal(str(fake.latitude())),
                    longitude=Decimal(str(fake.longitude())),
                    address=fake.address(),
                    country=country,
                    city=city,
                    marker_item=random.choice(shop_items) if random.choice([True, False]) else None
                )
                location_count += 1
                
                # Create memory with 1-1 relationship to location
                memory = Memory.objects.create(
                    user=user,
                    location=location,
                    title=fake.sentence(nb_words=4).replace('.', ''),
                    content=fake.text(max_nb_chars=500),
                    visit_date=fake.date_between(start_date='-2y', end_date='today'),
                    is_public=random.choice([True, False]),
                    tags=[fake.word() for _ in range(random.randint(1, 4))]
                )
                memory_count += 1
                
                # Create 1-3 media files for each memory
                num_media = random.randint(1, 3)
                for j in range(num_media):
                    MediaFile.objects.create(
                        memory=memory,
                        filename=f"{fake.uuid4()}.jpg",
                        original_filename=f"{fake.word()}.jpg",
                        file_path=SAMPLE_IMAGE_BASE64,
                        file_size=random.randint(50000, 5000000),
                        mime_type='image/jpeg',
                        media_type='image',
                        display_order=j,
                        width=random.randint(800, 2000),
                        height=random.randint(600, 1500)
                    )
        
        self.stdout.write(f'Created {location_count} locations and {memory_count} memories')

    def create_user_items_and_transactions(self, users, shop_items, admin_user):
        """Create user items and transaction history"""
        for user in users:
            # Random chance to have purchased items
            if random.choice([True, False]):
                # Purchase 1-3 random items
                num_purchases = random.randint(1, 3)
                for _ in range(num_purchases):
                    shop_item = random.choice(shop_items)
                    quantity = random.randint(1, 2)
                    
                    # Create user item
                    user_item, created = UserItem.objects.get_or_create(
                        user=user,
                        shop_item=shop_item,
                        defaults={'quantity': quantity}
                    )
                    
                    if not created:
                        user_item.quantity += quantity
                        user_item.save()
                    
                    # Create transaction log
                    total_cost = shop_item.price * quantity
                    TransactionLog.objects.create(
                        user=user,
                        type='purchase',
                        amount=-total_cost,
                        description=f'Purchased {quantity}x {shop_item.name}',
                        shop_item=shop_item,
                        quantity=quantity,
                        balance_before=user.currency + total_cost,
                        balance_after=user.currency
                    )
            
            # Random admin transactions
            if random.choice([True, False]):
                # Admin gives bonus
                bonus_amount = random.randint(100, 1000)
                user.currency += bonus_amount
                user.save()
                
                TransactionLog.objects.create(
                    user=user,
                    admin=admin_user,
                    type='admin_add',
                    amount=bonus_amount,
                    description=f'Welcome bonus from admin',
                    balance_before=user.currency - bonus_amount,
                    balance_after=user.currency
                )

    def create_memory_likes(self, users):
        """Create random memory likes"""
        all_memories = Memory.objects.filter(is_public=True)
        
        for user in users:
            # Each user likes 3-8 random public memories
            num_likes = random.randint(3, 8)
            memories_to_like = random.sample(list(all_memories), min(num_likes, len(all_memories)))
            
            for memory in memories_to_like:
                # Don't like your own memories
                if memory.user != user:
                    MemoryLike.objects.get_or_create(
                        user=user,
                        memory=memory
                    )
        
        total_likes = MemoryLike.objects.count()
        self.stdout.write(f'Created {total_likes} memory likes')