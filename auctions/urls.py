from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("closed_listings", views.closed_listings, name="closed_listings"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("add_watchlist/<int:id>", views.add_watchlist, name="add_watchlist"),
    path("remove_watchlist/<int:id>", views.remove_watchlist, name="remove_watchlist"),
    path("categories", views.categories, name="categories"),
    path("bid/<int:id>", views.bid, name="bid"),
    path("close_listing/<int:id>", views.close_listing, name="close_listing"),
    path("comment/<int:id>", views.comment, name="comment"),
    path("listings_under_category/<int:id>", views.listings_under_category, name="listings_under_category")
]
