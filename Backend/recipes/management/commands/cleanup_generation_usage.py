from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from recipes.models import RecipeGenerationUsage


class Command(BaseCommand):
    help = 'Delete RecipeGenerationUsage records older than GENERATION_USAGE_RETENTION_DAYS days'

    def handle(self, *args, **options):
        retention_days = getattr(settings, 'GENERATION_USAGE_RETENTION_DAYS', 30)
        cutoff = timezone.now().date() - timezone.timedelta(days=retention_days)
        deleted, _ = RecipeGenerationUsage.objects.filter(date__lt=cutoff).delete()
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {deleted} generation usage records older than {retention_days} days')
        )
