from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category_name = models.CharField(max_length=64)

    def __str__(self):
        return self.category_name

class Listing(models.Model):
    product_name = models.CharField(max_length=64)
    product_description = models.TextField()
    price = models.FloatField(default=0)
    image_url = models.CharField(max_length=160)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="watchlists")
    current_bid = models.ForeignKey('Bid', on_delete=models.CASCADE, blank=True, null=True, related_name="bid")


    def __str__(self):
        return self.product_name

class Bid(models.Model):
    user_bid = models.FloatField(default=0)
    current_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="bid_owner")
    listing_bid = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listing_bid")

class Comment(models.Model):
    user_name = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="comment_owner")
    user_comment = models.TextField()
    listing_associated_with_comment = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listing_associated_with_comment")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_name



