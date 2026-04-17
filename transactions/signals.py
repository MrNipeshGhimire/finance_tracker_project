from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Category


@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    if created:
        default_categories = [
            # 💸 Expense
            ('Food', 'expense', '🍔'),
            ('Shopping', 'expense', '🛍️'),
            ('Travel', 'expense', '✈️'),
            ('Entertainment', 'expense', '🎬'),
            ('Fuel', 'expense', '⛽'),
            ('Recharge', 'expense', '📱'),

            # 💰 Income
            ('Salary', 'income', '💼'),
            ('Investment', 'income', '📈'),
            ('Freelance', 'income', '💻'),
        ]

        for name, type_, icon in default_categories:
            Category.objects.create(
                user=instance,
                name=name,
                type=type_,
                icon=icon,
                is_default=True
            )