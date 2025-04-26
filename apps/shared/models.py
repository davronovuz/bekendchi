from django.db import models
import uuid

class BaseModel(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True




class Banner(BaseModel):
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    text = models.CharField(max_length=200, verbose_name="Matn")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Bannerlar"

    def __str__(self):
        return self.title