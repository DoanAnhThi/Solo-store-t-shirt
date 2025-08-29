from django.core.management.base import BaseCommand
from store.models import Category, Product, ProductImage, ProductOption, ProductVariant


class Command(BaseCommand):
    help = 'Seed the database with demo data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data...')

        # Create categories
        categories_data = [
            {'name': 'Shirts', 'description': 'Comfortable and stylish shirts'},
            {'name': 'Sweatshirts', 'description': 'Warm and cozy sweatshirts'},
            {'name': 'Pants', 'description': 'Comfortable pants for everyday wear'},
            {'name': 'Merch', 'description': 'Special merchandise items'},
            {'name': 'Hummingbird Food', 'description': 'Natural hummingbird food and nectar'},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create products
        products_data = [
            {
                'title': 'Medusa T-Shirt',
                'handle': 't-shirt',
                'description': 'Reimagine the feeling of a classic T-shirt. With our cotton T-shirts, everyday essentials no longer have to be ordinary.',
                'category': 'Shirts',
                'weight': 400,
                'status': 'published',
                'images': [
                    'https://medusa-public-images.s3.eu-west-1.amazonaws.com/tee-black-front.png',
                    'https://medusa-public-images.s3.eu-west-1.amazonaws.com/tee-black-back.png',
                    'https://medusa-public-images.s3.eu-west-1.amazonaws.com/tee-white-front.png',
                    'https://medusa-public-images.s3.eu-west-1.amazonaws.com/tee-white-back.png',
                ],
                'options': [
                    {'name': 'Size', 'values': ['S', 'M', 'L', 'XL']},
                    {'name': 'Color', 'values': ['Black', 'White']},
                ],
                'variants': [
                    {'title': 'S / Black', 'sku': 'SHIRT-S-BLACK', 'options': {'Size': 'S', 'Color': 'Black'}, 'price': 15.00},
                    {'title': 'S / White', 'sku': 'SHIRT-S-WHITE', 'options': {'Size': 'S', 'Color': 'White'}, 'price': 15.00},
                    {'title': 'M / Black', 'sku': 'SHIRT-M-BLACK', 'options': {'Size': 'M', 'Color': 'Black'}, 'price': 15.00},
                    {'title': 'M / White', 'sku': 'SHIRT-M-WHITE', 'options': {'Size': 'M', 'Color': 'White'}, 'price': 15.00},
                    {'title': 'L / Black', 'sku': 'SHIRT-L-BLACK', 'options': {'Size': 'L', 'Color': 'Black'}, 'price': 15.00},
                    {'title': 'L / White', 'sku': 'SHIRT-L-WHITE', 'options': {'Size': 'L', 'Color': 'White'}, 'price': 15.00},
                    {'title': 'XL / Black', 'sku': 'SHIRT-XL-BLACK', 'options': {'Size': 'XL', 'Color': 'Black'}, 'price': 15.00},
                    {'title': 'XL / White', 'sku': 'SHIRT-XL-WHITE', 'options': {'Size': 'XL', 'Color': 'White'}, 'price': 15.00},
                ]
            },
            {
                'title': 'Medusa Sweatshirt',
                'handle': 'sweatshirt',
                'description': 'Reimagine the feeling of a classic sweatshirt. With our cotton sweatshirt, everyday essentials no longer have to be ordinary.',
                'category': 'Sweatshirts',
                'weight': 400,
                'status': 'published',
                'images': [
                    'https://medusa-public-images.s3.eu-west-1.amazonaws.com/sweatshirt-vintage-front.png',
                    'https://medusa-public-images.s3.eu-west-1.amazonaws.com/sweatshirt-vintage-back.png',
                ],
                'options': [
                    {'name': 'Size', 'values': ['S', 'M', 'L', 'XL']},
                ],
                'variants': [
                    {'title': 'S', 'sku': 'SWEATSHIRT-S', 'options': {'Size': 'S'}, 'price': 25.00},
                    {'title': 'M', 'sku': 'SWEATSHIRT-M', 'options': {'Size': 'M'}, 'price': 25.00},
                    {'title': 'L', 'sku': 'SWEATSHIRT-L', 'options': {'Size': 'L'}, 'price': 25.00},
                    {'title': 'XL', 'sku': 'SWEATSHIRT-XL', 'options': {'Size': 'XL'}, 'price': 25.00},
                ]
            },
            {
                'title': 'Medusa Sweatpants',
                'handle': 'sweatpants',
                'description': 'Reimagine the feeling of classic sweatpants. With our cotton sweatpants, everyday essentials no longer have to be ordinary.',
                'category': 'Pants',
                'weight': 400,
                'status': 'published',
                'images': [
                    'https://medusa-public-images.s3.eu-west-1.amazonaws.com/sweatpants-gray-front.png',
                    'https://medusa-public-images.s3.eu-west-1.amazonaws.com/sweatpants-gray-back.png',
                ],
                'options': [
                    {'name': 'Size', 'values': ['S', 'M', 'L', 'XL']},
                ],
                'variants': [
                    {'title': 'S', 'sku': 'SWEATPANTS-S', 'options': {'Size': 'S'}, 'price': 30.00},
                    {'title': 'M', 'sku': 'SWEATPANTS-M', 'options': {'Size': 'M'}, 'price': 30.00},
                    {'title': 'L', 'sku': 'SWEATPANTS-L', 'options': {'Size': 'L'}, 'price': 30.00},
                    {'title': 'XL', 'sku': 'SWEATPANTS-XL', 'options': {'Size': 'XL'}, 'price': 30.00},
                ]
            },
            {
                'title': 'Medusa Shorts',
                'handle': 'shorts',
                'description': 'Reimagine the feeling of classic shorts. With our cotton shorts, everyday essentials no longer have to be ordinary.',
                'category': 'Merch',
                'weight': 400,
                'status': 'published',
                'images': [
                    'https://medusa-public-images.s3.eu-west-1.amazonaws.com/shorts-vintage-front.png',
                    'https://medusa-public-images.s3.eu-west-1.amazonaws.com/shorts-vintage-back.png',
                ],
                'options': [
                    {'name': 'Size', 'values': ['S', 'M', 'L', 'XL']},
                ],
                'variants': [
                    {'title': 'S', 'sku': 'SHORTS-S', 'options': {'Size': 'S'}, 'price': 20.00},
                    {'title': 'M', 'sku': 'SHORTS-M', 'options': {'Size': 'M'}, 'price': 20.00},
                    {'title': 'L', 'sku': 'SHORTS-L', 'options': {'Size': 'L'}, 'price': 20.00},
                    {'title': 'XL', 'sku': 'SHORTS-XL', 'options': {'Size': 'XL'}, 'price': 20.00},
                ]
            },
            {
                'title': 'Magic Nectar - Hummingbird Food',
                'handle': 'magic-nectar',
                'description': 'Transform your backyard into a hummingbird paradise with our all-natural nectar blend. Made with pure cane sugar, no dyes or preservatives.',
                'category': 'Hummingbird Food',
                'weight': 200,
                'status': 'published',
                'images': [
                    'https://hummingbirdfood.co/cdn/shop/files/The_Best_Hummingbird_Food_On_Earth_1.jpg',
                    'https://hummingbirdfood.co/cdn/shop/files/1703560330299-Vintage-Green.webp',
                    'https://hummingbirdfood.co/cdn/shop/files/1703560327588-Cameo-Brown.webp',
                ],
                'options': [
                    {'name': 'Size', 'values': ['Standard', 'Large']},
                ],
                'variants': [
                    {'title': 'Standard Pack', 'sku': 'NECTAR-STD', 'options': {'Size': 'Standard'}, 'price': 12.00},
                    {'title': 'Large Pack', 'sku': 'NECTAR-LRG', 'options': {'Size': 'Large'}, 'price': 18.00},
                ]
            },
        ]

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                handle=product_data['handle'],
                defaults={
                    'title': product_data['title'],
                    'description': product_data['description'],
                    'category': categories[product_data['category']],
                    'weight': product_data['weight'],
                    'status': product_data['status'],
                }
            )
            
            if created:
                self.stdout.write(f'Created product: {product.title}')
                
                # Create options
                for option_data in product_data['options']:
                    ProductOption.objects.create(
                        product=product,
                        name=option_data['name'],
                        values=option_data['values']
                    )
                
                # Create variants
                for variant_data in product_data['variants']:
                    ProductVariant.objects.create(
                        product=product,
                        title=variant_data['title'],
                        sku=variant_data['sku'],
                        options=variant_data['options'],
                        price=variant_data['price'],
                        inventory_quantity=1000
                    )
                
                # Create images (skip actual image download for now)
                for i, image_url in enumerate(product_data['images']):
                    ProductImage.objects.create(
                        product=product,
                        image=f'products/{product.handle}-{i+1}.jpg',
                        alt_text=f'{product.title} - Image {i+1}',
                        is_primary=(i == 0)
                    )

        self.stdout.write(self.style.SUCCESS('Successfully seeded demo data!'))
