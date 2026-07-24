from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from api.models import Product

class Command(BaseCommand):
    help = 'Seeds the database with default users and products'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # 1. Create Default Users
        # Admin
        admin_email = 'admin@nourseen.com'
        if not User.objects.filter(email=admin_email).exists():
            admin_user = User.objects.create_superuser(
                username=admin_email,
                email=admin_email,
                password='admin123',
                first_name='Demo Admin'
            )
            Token.objects.get_or_create(user=admin_user)
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_email}'))
        else:
            self.stdout.write('Admin user already exists.')

        # Regular User
        user_email = 'user@nourseen.com'
        if not User.objects.filter(email=user_email).exists():
            reg_user = User.objects.create_user(
                username=user_email,
                email=user_email,
                password='user123',
                first_name='Demo User'
            )
            Token.objects.get_or_create(user=reg_user)
            self.stdout.write(self.style.SUCCESS(f'Created regular user: {user_email}'))
        else:
            self.stdout.write('Regular user already exists.')

        # 2. Create Default Products
        DEFAULT_PRODUCTS = [
            {
                "id": 1,
                "title": "Aura Linen Summer Dress",
                "title_ar": "فستان هالة الصيفي من الكتان",
                "category": "women",
                "price": 89.00,
                "originalPrice": None,
                "rating": 4.8,
                "badge": "New",
                "badgeType": "new",
                "image": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=700&auto=format&fit=crop&q=80",
                "description": "An elegant, airy pastel linen dress crafted for warm afternoons. Features puffed sleeves, a detailed button-down front, and a matching waist tie. Made from 100% organic, breathable linen.",
                "description_ar": "فستان كتان صيفي ناعم بلون هادئ ومناسب لأوقات الظهيرة الدافئة. يتميز بأكمام منفوخة وأزرار أمامية أنيقة وحزام خصر متناسق. مصنوع من الكتان العضوي الطبيعي بنسبة 100٪.",
                "sizes": ["XS", "S", "M", "L", "XL"],
                "colors": ["#F5D6C6", "#FFFFFF", "#1E1E24"],
                "weight": 0.35,
                "can_be_returned": True
            },
            {
                "id": 2,
                "title": "Tailored Double-Breasted Blazer",
                "title_ar": "سترة رسمية مزدوجة الصدر",
                "category": "women",
                "price": 145.00,
                "originalPrice": 180.00,
                "rating": 4.9,
                "badge": "Sale",
                "badgeType": "sale",
                "image": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=700&auto=format&fit=crop&q=80",
                "description": "Structure meets elegance. This double-breasted blazer is designed with an oversized fit, peaked lapels, and custom tortoiseshell buttons. Ideal for transitioning from office hours to dinner.",
                "description_ar": "هيكل متناسق وأناقة عصرية. صممت هذه السترة الرسمية بقصة مريحة واسعة وأزرار صدفية مميزة ومثالية للارتداء اليومي وأوقات العمل والمساء.",
                "sizes": ["S", "M", "L", "XL"],
                "colors": ["#D2B48C", "#1E1E24", "#F5F5F5"],
                "weight": 0.85,
                "can_be_returned": True
            },
            {
                "id": 3,
                "title": "Cozy Cable-Knit Sweater",
                "title_ar": "كنزة صوفية دافئة محبوكة",
                "category": "women",
                "price": 75.00,
                "originalPrice": None,
                "rating": 4.7,
                "badge": "",
                "badgeType": "",
                "image": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=700&auto=format&fit=crop&q=80",
                "description": "A timeless knit sweater in soft cream wool. Boasting a classic cable pattern, relaxed crew neck, and ribbed hems. Incredibly cozy and perfect for cold seasons.",
                "description_ar": "كنزة صوفية كلاسيكية محبوكة بنقوش مميزة من الصوف الكريمي الناعم. ياقة مستديرة وحواف مطاطية مريحة، مثالية للأجواء الباردة والشتوية.",
                "sizes": ["XS", "S", "M", "L"],
                "colors": ["#Fdfbf7", "#9E90A2", "#2B2B2B"],
                "weight": 0.65,
                "can_be_returned": True
            },
            {
                "id": 4,
                "title": "Terracotta Linen Romper",
                "title_ar": "رومبير أطفال من الكتان الطيني",
                "category": "kids",
                "price": 42.00,
                "originalPrice": 55.00,
                "rating": 4.6,
                "badge": "Sale",
                "badgeType": "sale",
                "image": "https://images.unsplash.com/photo-1519457431-44ccd64a579b?w=700&auto=format&fit=crop&q=80",
                "description": "Cute and playful linen dungaree romper for your little one. Features adjustable cross-back straps, elastic leg openings, and brass button details. Gentle on sensitive skin.",
                "description_ar": "رومبير كتان لطيف ومريح لأطفالك. حمالات كتف متقاطعة قابلة للتعديل وتفاصيل أزرار نحاسية ناعمة وآمن تمامًا على بشرة الأطفال الحساسة.",
                "sizes": ["6-12M", "12-18M", "2T", "3T", "4T"],
                "colors": ["#D66853", "#bfa37a", "#2A9D8F"],
                "weight": 0.18,
                "can_be_returned": True
            },
            {
                "id": 5,
                "title": "Kids Denim Adventure Jacket",
                "title_ar": "سترة دنيم للأطفال للمغامرات",
                "category": "kids",
                "price": 58.00,
                "originalPrice": None,
                "rating": 4.9,
                "badge": "Best Seller",
                "badgeType": "new",
                "image": "https://images.unsplash.com/photo-1503919545889-aef636e10ad4?w=700&auto=format&fit=crop&q=80",
                "description": "Classic blue denim jacket built for kids on the move. Heavy-duty denim cotton fabric with soft jersey lining, double chest pockets, and easy snap-button enclosures.",
                "description_ar": "جاكيت جينز أزرق كلاسيكي للأطفال محبي الحركة. قماش قطني متين مع بطانة داخلية ناعمة، جيوب مزدوجة وأزرار كبس سهلة الإغلاق.",
                "sizes": ["2T", "3T", "4T", "5T", "6-7Y"],
                "colors": ["#4682B4", "#2F4F4F"],
                "weight": 0.48,
                "can_be_returned": True
            },
            {
                "id": 6,
                "title": "Organic Sleepy Pajama Set",
                "title_ar": "طقم بيجامة نوم قطنية عضوية",
                "category": "kids",
                "price": 36.00,
                "originalPrice": None,
                "rating": 4.8,
                "badge": "",
                "badgeType": "",
                "image": "https://images.unsplash.com/photo-1515488042361-404e9250afef?w=700&auto=format&fit=crop&q=80",
                "description": "Two-piece sleep set made from ultra-soft rib cotton. Non-toxic organic dye, envelope neckline for easy dressing, and flatlock seams for maximum comfort during bedtime.",
                "description_ar": "طقم نوم مريح من قطعتين للأطفال مصنوع من القطن العضوي فائق النعومة. أصباغ طبيعية آمنة، درزات مسطحة لراحة تامة أثناء النوم المريح.",
                "sizes": ["3-6M", "6-12M", "18-24M", "2T", "3T"],
                "colors": ["#B0E0E6", "#FFB6C1", "#E6E6FA"],
                "weight": 0.22,
                "can_be_returned": False  # Sleepwear intimate items example
            },
            {
                "id": 7,
                "title": "Floral Meadow Maxi Dress",
                "title_ar": "فستان ماكسي بنقوش الزهور",
                "category": "women",
                "price": 110.00,
                "originalPrice": None,
                "rating": 4.7,
                "badge": "New",
                "badgeType": "new",
                "image": "https://images.unsplash.com/photo-1612336307429-8a898d10e223?w=700&auto=format&fit=crop&q=80",
                "description": "Embrace the outdoors with this flowy maxi dress printed with delicate wildflowers. Features an adjustable halter neck, tiered skirt, and smocked back panel for a comfortable fit.",
                "description_ar": "فستان ماكسي ناعم بنقوش أزهار برية رقيقة. حمالة عنق قابلة للتعديل وتصميم خفيف ومريح ومناسب للنزهات الصيفية والحدائق العامة.",
                "sizes": ["S", "M", "L"],
                "colors": ["#FFF0F5", "#E0FFFF"],
                "weight": 0.40,
                "can_be_returned": True
            },
            {
                "id": 8,
                "title": "Cozy Cotton Knit Hoodie",
                "title_ar": "سترة هودي قطنية دافئة للأطفال",
                "category": "kids",
                "price": 48.00,
                "originalPrice": None,
                "rating": 4.5,
                "badge": "",
                "badgeType": "",
                "image": "https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?w=700&auto=format&fit=crop&q=80",
                "description": "A warm knit sweater hoodie featuring a whimsical hood and pocket detailing. Knit with thick premium cotton yarn to keep toddlers warm during crisp park outings.",
                "description_ar": "سترة صوفية محبوكة بقلنسوة وتفاصيل جيوب جميلة. محبوكة بخيوط قطنية سميكة وممتازة للحفاظ على دفء الأطفال الصغار خلال النزهات الخارجية الباردة.",
                "sizes": ["12-18M", "2T", "3T", "4T", "5T"],
                "colors": ["#708090", "#BC8F8F", "#F5F5DC"],
                "weight": 0.32,
                "can_be_returned": True
            }
        ]

        # Reset products to ensure seed matches exactly, using update_or_create to preserve ids
        for prod in DEFAULT_PRODUCTS:
            variants = [
                {
                    "color": color,
                    "sizes": [{"size": size, "weight": prod["weight"]} for size in prod["sizes"]]
                }
                for color in prod["colors"]
            ]
            Product.objects.update_or_create(
                id=prod['id'],
                defaults={
                    'title': prod['title'],
                    'title_ar': prod['title_ar'],
                    'category': prod['category'],
                    'price': prod['price'],
                    'originalPrice': prod['originalPrice'],
                    'rating': prod['rating'],
                    'badge': prod['badge'],
                    'badgeType': prod['badgeType'],
                    'image': prod['image'],
                    'description': prod['description'],
                    'description_ar': prod['description_ar'],
                    'sizes': prod['sizes'],
                    'colors': prod['colors'],
                    'variants': variants,
                    'weight': prod['weight'],
                    'can_be_returned': prod['can_be_returned'],
                }
            )
            self.stdout.write(f"Seeded product: {prod['title']}")

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
