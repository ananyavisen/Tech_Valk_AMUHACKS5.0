from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    questionnaire_completed = models.BooleanField(default=False)
    fuel_bonus = models.IntegerField(default=0)
    last_quest_completed = models.DateField(null=True, blank=True)


    def __str__(self):
        return self.user.username
    
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
     Profile.objects.create(user=instance)

class QuestionnaireResponse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    school_language = models.CharField(max_length=50)
    stage_activity = models.CharField(max_length=50)

    extempore_comfort = models.IntegerField()
    public_speaking_confidence = models.IntegerField()
    help_seeking_comfort = models.IntegerField()
    group_discussion_confidence = models.IntegerField()
    adaptability = models.IntegerField()
    total_score = models.IntegerField(default=0)
    COURSE_CHOICES = [
    ("btech", "B.Tech"),
    ("bsc", "B.Sc"),
    ]

    course = models.CharField(max_length=20, choices=COURSE_CHOICES)
    specialisation = models.CharField(max_length=100, blank=True, null=True)

    def calculate_score(self):

     language_score = {
        "english": 3,
        "hindi": 2,
        "regional": 1
     } .get(self.school_language, 1)

     stage_score = {
        "very_much": 3,
        "rarely": 2,
        "never": 1
     }.get(self.stage_activity, 1)

     pressure_score = {
        "motivated": 3,
        "anxious": 2,
        "overwhelmed": 1
     }.get(self.academic_pressure, 1)

     self.total_score = (
        language_score +
        stage_score +
        pressure_score +
        self.extempore_comfort +
        self.public_speaking_confidence +
        self.help_seeking_comfort +
        self.group_discussion_confidence +
        self.adaptability
    )

     self.save()

class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    moods = models.CharField(max_length=200)
    reflection = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at.date()}"
     
class Resource(models.Model):

    COURSE_CHOICES = [
        ("btech", "B.Tech"),
        ("bsc", "B.Sc"),
    ]

    CATEGORY_CHOICES = [
        ("notes", "Notes"),
        ("video", "Video"),
        ("article", "Article"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.CharField(max_length=10, choices=COURSE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    link = models.URLField(blank=True, null=True)  # YouTube/blog link
    file = models.FileField(upload_to="resources/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
