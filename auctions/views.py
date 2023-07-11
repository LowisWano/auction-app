from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max, Value, FloatField, Count
from django.db.models.functions import Coalesce
from .models import User, Listing, Category, Bid, Comment


def index(request):
    active_listings = Listing.objects.exclude(is_active = False)
    return render(request, "auctions/index.html", {
        "active_listing": active_listings
    })

def closed_listings(request):
    closed_listings = Listing.objects.exclude(is_active = True)
    return render(request, "auctions/closed_listings.html", {
            "closed_listings": closed_listings
        })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create_listing(request):
    # if user "posts" or submits a form for a listing
    if request.method == 'POST':

        # get the data from the form
        name = request.POST["item_name"]
        description = request.POST["item_description"]
        url = request.POST["item_url"]
        start_bid = request.POST["item_starting_bid"]
        item_category = request.POST["item_category"]
        user = request.user
        category_data = Category.objects.get(category_name = item_category)

        # create a new listing object
        listing = Listing(
            product_name = name, 
            product_description = description,
            price = float(start_bid),
            image_url = url,
            category = category_data,
            owner = user,
        )
        # Insert the object in our database
        listing.save()
        # redirect to index page
        return HttpResponseRedirect(reverse("index"))
    
    # if user wants to get the webpage for creating a form
    else:    
        categories = Category.objects.all()
        return render(request,"auctions/create_listing.html", {
            "categories": categories
        })
    

def listing(request, id):
    current_user = request.user
    user_watchlist = None

    if current_user.is_authenticated:
        user_watchlist = current_user.watchlists.all()

    listing_data = Listing.objects.get(pk=id)
    highest_bid = Bid.objects.filter(listing_bid=listing_data).aggregate(max_bid=Max('user_bid'))
    max_bid_value = highest_bid['max_bid'] or 0
    bid_count = listing_data.listing_bid.count()
    comment_data = Comment.objects.filter(listing_associated_with_comment=listing_data)

    highest_bid = Bid.objects.filter(listing_bid=listing_data).order_by('-user_bid').first()
    highest_bid_user = highest_bid.current_user if highest_bid else None

    return render(request, "auctions/listing.html",{
        "listing": listing_data,
        "user_watchlist": user_watchlist,
        "highest_bid": max_bid_value,
        "bid_count": bid_count,
        "highest_bid_user": highest_bid_user,
        "comments": comment_data,
    })

    
def close_listing(request, id):
    listing_data = Listing.objects.get(pk=id)
    listing_data.is_active = False
    listing_data.save()

    highest_bid = Bid.objects.filter(listing_bid=listing_data).order_by('-user_bid').first()
    highest_bid_user = highest_bid.current_user if highest_bid else None
    return render(request, "auctions/listing.html",{
        "listing": listing_data,
        "highest_bid_user": highest_bid_user,
    })

def watchlist(request):
    current_user = request.user
    # get the list of the user's watchlist
    watchlisted_listings = current_user.watchlists.all()
    # render watchlist page and pass in a list of the user's watchlist
    return render(request, "auctions/watchlist.html", {
        "listings": watchlisted_listings
    })

def add_watchlist(request, id):
    if request.method == "POST":
        user = request.user
        listing_data = Listing.objects.get(pk=id)
        listing_data.watchlist.add(user)
        user_watchlist = Listing.objects.filter(watchlist=user)
        highest_bid = Bid.objects.filter(listing_bid=listing_data).aggregate(max_bid=Max('user_bid'))
        max_bid_value = highest_bid['max_bid'] or 0
        bid_count = listing_data.listing_bid.count()
        highest_bid = Bid.objects.filter(listing_bid=listing_data).order_by('-user_bid').first()
        highest_bid_user = highest_bid.current_user if highest_bid else None
        comment_data = Comment.objects.filter(listing_associated_with_comment=listing_data)

        return render(request, "auctions/listing.html",{
        "listing": listing_data,
        "user_watchlist": user_watchlist,
        "highest_bid": max_bid_value,
        "bid_count": bid_count,
        "highest_bid_user": highest_bid_user,
        "comments": comment_data,
        })
    
def remove_watchlist(request, id):
    if request.method == "POST":
        user = request.user
        listing_data = Listing.objects.get(pk=id)
        listing_data.watchlist.remove(user)
        highest_bid = Bid.objects.filter(listing_bid=listing_data).aggregate(max_bid=Max('user_bid'))
        max_bid_value = highest_bid['max_bid'] or 0
        bid_count = listing_data.listing_bid.count()
        highest_bid = Bid.objects.filter(listing_bid=listing_data).order_by('-user_bid').first()
        highest_bid_user = highest_bid.current_user if highest_bid else None
        comment_data = Comment.objects.filter(listing_associated_with_comment=listing_data) 

        return render(request, "auctions/listing.html", {
        "listing": listing_data,
        "highest_bid": max_bid_value,
        "bid_count": bid_count,
        "highest_bid_user": highest_bid_user,
        "comments": comment_data,
        })
    

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def listings_under_category(request, id):
    category_data = Category.objects.get(pk=id)
    active_listings = Listing.objects.filter(category=category_data, is_active=True)

    return render(request, "auctions/listings_under_category.html",{
        "category": category_data,
        "active_listings": active_listings
    })



def bid(request, id):
    if request.method == "POST":
        # get bid from form
        bid = int(request.POST["bid_item"])

        # get listing price
        listing_data = Listing.objects.get(pk=id)
        price = listing_data.price

        # get highest bid from all bid entries
        highest_bid = Bid.objects.filter(listing_bid=listing_data).aggregate(max_bid=Max('user_bid'))
        max_bid_value = highest_bid['max_bid'] or 0

        # if bid greater than price
        if bid >= price: 
        
            # bid less than highest bid
            if bid <= max_bid_value:
                highest_bid = Bid.objects.filter(listing_bid=listing_data).aggregate(max_bid=Max('user_bid'))
                max_bid_value = highest_bid['max_bid'] or 0
                bid_count = listing_data.listing_bid.count()
                user_watchlist = Listing.objects.filter(watchlist=request.user)
                highest_bid = Bid.objects.filter(listing_bid=listing_data).order_by('-user_bid').first()
                highest_bid_user = highest_bid.current_user if highest_bid else None
                comment_data = Comment.objects.filter(listing_associated_with_comment=listing_data) 

                return render(request, "auctions/listing.html", {
                "listing": listing_data,
                "error": "Bid is not enough.",
                "bid_validated": False,
                "highest_bid": max_bid_value,
                "bid_count": bid_count,
                "user_watchlist": user_watchlist,
                "highest_bid_user": highest_bid_user,
                "comments": comment_data,
                })
            
            else:
                bid = Bid(
                    user_bid = bid,
                    current_user = request.user,
                    listing_bid = listing_data,
                    )
                bid.save()
                highest_bid = Bid.objects.filter(listing_bid=listing_data).aggregate(max_bid=Max('user_bid'))
                max_bid_value = highest_bid['max_bid'] or 0
                bid_count = listing_data.listing_bid.count()
                user_watchlist = Listing.objects.filter(watchlist=request.user)
                highest_bid = Bid.objects.filter(listing_bid=listing_data).order_by('-user_bid').first()
                highest_bid_user = highest_bid.current_user if highest_bid else None
                comment_data = Comment.objects.filter(listing_associated_with_comment=listing_data)

                return render(request, "auctions/listing.html", {
                "listing": listing_data,
                "success": "Bid successfully placed.",
                "bid_too_low": False,
                "highest_bid": max_bid_value,
                "bid_count": bid_count,
                "user_watchlist": user_watchlist,
                "highest_bid_user": highest_bid_user,
                "comments": comment_data,
                })
        else:
            highest_bid = Bid.objects.filter(listing_bid=listing_data).aggregate(max_bid=Max('user_bid'))
            max_bid_value = highest_bid['max_bid'] or 0
            bid_count = listing_data.listing_bid.count()
            user_watchlist = Listing.objects.filter(watchlist=request.user)
            highest_bid = Bid.objects.filter(listing_bid=listing_data).order_by('-user_bid').first()
            highest_bid_user = highest_bid.current_user if highest_bid else None
            comment_data = Comment.objects.filter(listing_associated_with_comment=listing_data) 
            return render(request, "auctions/listing.html", {
                "listing": listing_data,
                "error": "Bid is not enough.",
                "bid_validated": False,
                "highest_bid": max_bid_value,
                "bid_count": bid_count,
                "user_watchlist": user_watchlist,
                "highest_bid_user": highest_bid_user,
                "comments": comment_data,
                })


def comment(request, id):
    # if user "posts" or submits a form for a comment
    if request.method == "POST":

        # get the data from the form
        comment_owner = request.user
        comment_content = request.POST["comment_input_box"]
        listing_data = Listing.objects.get(pk=id)

        # create a new comment object and fill in the proper fields
        comment = Comment(
            user_name = comment_owner,
            user_comment = comment_content,
            listing_associated_with_comment = listing_data,
        )
        
        # save object to database
        comment.save()

        # render listing.html

        # all data field required for render listing
        highest_bid = Bid.objects.filter(listing_bid=listing_data).aggregate(max_bid=Max('user_bid'))
        max_bid_value = highest_bid['max_bid'] or 0
        bid_count = listing_data.listing_bid.count()
        user_watchlist = Listing.objects.filter(watchlist=request.user)
        highest_bid = Bid.objects.filter(listing_bid=listing_data).order_by('-user_bid').first()
        highest_bid_user = highest_bid.current_user if highest_bid else None

        # data field unique to comment function
        comment_data = Comment.objects.filter(listing_associated_with_comment=listing_data) 

        return render(request, "auctions/listing.html", {
            "listing": listing_data,
            "highest_bid": max_bid_value,
            "bid_count": bid_count,
            "user_watchlist": user_watchlist,
            "highest_bid_user": highest_bid_user,
            "comments": comment_data,
            })



