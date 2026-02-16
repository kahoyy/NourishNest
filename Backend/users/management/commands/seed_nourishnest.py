from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from inventory.models import DietaryTag, InventoryItem
from recipes.models import Recipe
from users.models import SubscriptionPlan, UserBaseProfile, UserRewards


class Command(BaseCommand):
    help = "Seed demo data for NourishNest."

    def handle(self, *args, **options):
        user_model = get_user_model()

        plans = [
            ("Free", 0.00, ["Inventory", "Basic AI"], "Starter plan"),
            ("Premium", 9.99, ["Analytics", "Planner", "Higher limits"], "Premium features"),
            ("Pro", 19.99, ["All features", "Top limits"], "Power user"),
        ]
        for name, price, features, description in plans:
            SubscriptionPlan.objects.get_or_create(
                name=name,
                defaults={
                    "price": price,
                    "features": features,
                    "description": description,
                    "is_active": True,
                },
            )

        demo_user, created = user_model.objects.get_or_create(
            email="demo@nourishnest.local",
            defaults={"username": "demo_user", "first_name": "Demo", "last_name": "User"},
        )
        if created:
            demo_user.set_password("Password123!")
            demo_user.save()

        UserBaseProfile.objects.get_or_create(
            user=demo_user,
            defaults={
                "height_cm": 170,
                "weight_kg": 68.0,
                "allergies": ["peanuts"],
                "dietary_restrictions": ["vegetarian"],
                "fitness_goals": ["weight_loss"],
                "budget_limit": 2000.00,
                "calorie_target": 2000,
            },
        )

        UserRewards.objects.get_or_create(user=demo_user)

        tags = [
            ("Protein", "High protein foods"),
            ("Vegan", "Plant-based"),
            ("Gluten-Free", "No gluten"),
            ("Perishable", "Expires soon"),
            ("Green", "Sustainable choice"),
        ]
        tag_map = {}
        for name, description in tags:
            tag, _ = DietaryTag.objects.get_or_create(name=name, defaults={"description": description})
            tag_map[name] = tag

        today = timezone.now().date()
        inventory_items = [
            ("Spinach", "1 bunch", True, today + timedelta(days=2), ["Green", "Perishable"]),
            ("Eggs", "6 pcs", True, today + timedelta(days=7), ["Protein", "Perishable"]),
            ("Rice", "1 kg", False, None, []),
        ]
        for name, quantity, perishable, expiry, tag_names in inventory_items:
            item, _ = InventoryItem.objects.get_or_create(
                user=demo_user,
                name=name,
                defaults={
                    "quantity": quantity,
                    "perishable": perishable,
                    "expiry_date": expiry,
                },
            )
            if tag_names:
                item.tags.set([tag_map[tag] for tag in tag_names])

        recipe, _ = Recipe.objects.get_or_create(
            name="Spinach Egg Scramble",
            defaults={
                "description": "Quick protein-packed scramble using pantry staples.",
                "instructions": "Step 1: Saute spinach.\nStep 2: Add eggs and scramble.",
                "ingredients_text": ["1 bunch spinach", "2 eggs", "salt", "pepper"],
                "generated_by_llm": False,
                "nutrition_info": {
                    "calories": 320,
                    "protein_g": 28,
                    "carbs_g": 8,
                    "fat_g": 18,
                    "fiber_g": 3,
                },
                "match_score": 0.85,
                "servings": 2,
                "difficulty": "easy",
                "created_by": demo_user,
                "is_public": True,
            },
        )
        recipe.tags.set([tag_map["Protein"], tag_map["Green"]])

        self.stdout.write(self.style.SUCCESS("Seed data created. Demo user: demo@nourishnest.local / Password123!"))
