import csv
import os
from django.core.management.base import BaseCommand
from core.models import Question

class Command(BaseCommand):
    help = 'Import MCQs from CSV'

    def handle(self, *args, **kwargs):
        file_path = os.path.join("random_questions.csv")  # Adjust path as needed

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Question.objects.create(
                    question_text=row['Question'],
                    option_a=row['Option A'],
                    option_b=row['Option B'],
                    option_c=row['Option C'],
                    option_d=row['Option D'],
                    correct_option=row['Correct Option'].strip().upper()
                )
        self.stdout.write(self.style.SUCCESS("✅ MCQs imported successfully!"))
