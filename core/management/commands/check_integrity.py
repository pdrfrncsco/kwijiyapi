from django.core.management.base import BaseCommand
from quizzes.models import Question

class Command(BaseCommand):
    help = 'Checks data integrity for questions and options'

    def handle(self, *args, **options):
        self.stdout.write("Starting integrity check...")
        
        # Check questions without correct options
        questions = Question.objects.all()
        issues = 0
        
        for q in questions:
            correct_options = q.options.filter(is_correct=True).count()
            if correct_options == 0:
                self.stdout.write(self.style.ERROR(f"Question {q.id} has NO correct option: {q.question_text}"))
                issues += 1
            elif correct_options > 1:
                self.stdout.write(self.style.WARNING(f"Question {q.id} has multiple correct options: {q.question_text}"))
        
        if issues == 0:
            self.stdout.write(self.style.SUCCESS("All questions have valid options!"))
        else:
            self.stdout.write(self.style.ERROR(f"Found {issues} critical issues."))
