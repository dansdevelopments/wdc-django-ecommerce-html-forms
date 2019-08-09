import re
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound

from products.models import Product, Category, ProductImage


def products(request):
    # Get all products from the DB using the Product model
    products = Product.objects.all()  # <YOUR CODE HERE>

    # Get up to 4 `featured=true` Products to be displayed on top
    featured_products = Product.objects.filter(featured=True).order_by('?')[:4]  # <YOUR CODE HERE>

    return render(
        request,
        'products.html',
        context={'products': products, 'featured_products': featured_products}
    )


def create_product(request):
    # Get all categories from the DB
    categories = Category.objects.all()  # <YOUR CODE HERE>
    if request.method == 'GET':
        # Render 'create_product.html' template sending categories as context
        return render(request, 'create_product.html', context={'categories':categories})  # static_form is just used as an example
    elif request.method == 'POST':
        # Validate that all fields below are given in request.POST dictionary,
        # and that they don't have empty values.

        # If any errors, build an errors dictionary with the following format
        # and render 'create_product.html' sending errors and categories as context

        # errors = {'name': 'This field is required.'}
 
        fields = ['name', 'sku', 'price']
        errors = {}
        for field in fields:
            if not request.POST.get(field):
                errors[field] = 'This field is required.'

        # If no errors so far, validate each field one by one and use the same
        # errors dictionary created above in case that any validation fails
        if errors:
            return render(
                request,
                'create_product.html',
                context={
                    'categories':categories,
                    'errors':errors,
                    'payload':request.POST
                    }
                )
        # name validation: can't be longer that 100 characters
        name = request.POST.get('name')
        if len(name) > 100:
            errors['name'] = "Name can't be longer than 100 characters."

        # SKU validation: it must contain 8 alphanumeric characters
        sku = request.POST.get('sku')
        if len(sku) != 8 or sku != re.match('\w*',sku).group():
            errors['sku'] = "Sku must contain 8 alphanumeric characters"

        # Price validation: positive float lower than 10000.00
        price = request.POST.get('price')
        if float(price) >= 10000.0 or float(price) < 0.0:
            errors['price'] = "Price can't be negative or more than $9999.99"

        # if any errors so far, render 'create_product.html' sending errors and
        # categories as context
        if errors:
            return render(
                request,
                'create_product.html',
                context={
                    'categories':categories,
                    'errors':errors,
                    'payload':request.POST
                    }
                )
            
        # If execution reaches this point, there aren't any errors.
        # Get category from DB based on category name given in payload.
        # Create product with data given in payload and proper category
        category = Category.objects.get(name=request.POST.get('category')) 
        product = Product.objects.create(
            name = request.POST.get('name'),
            sku = request.POST.get('sku'),
            category = category,
            description = request.POST.get('description'),
            price = request.POST.get('price')
        )  

        # Up to three images URLs can come in payload with keys 'image-1', 'image-2', etc.
        # For each one, create a ProductImage object with proper URL and product
        images=[]
        for i in range(3):
            image = request.POST.get(f"image_{i+1}")
            if image:
                images.append(image)
        
        for image in images:
            ProductImage.objects.create(
                product=product,
                url=image
            )
            
        # Redirect to 'products' view
        return redirect('products')


def edit_product(request, product_id):
    # Get product with given product_id
    product = Product.objects.get(id=product_id)
    # Get all categories from the DB
    categories = Category.objects.all()  # <YOUR CODE HERE>
    if request.method == 'GET':
        # Render 'edit_product.html' template sending product, categories and
        # a 'images' list containing all product images URLs.
        images = [image.url for image in product.productimage_set.all()]
        return render(
                    request,
                    'edit_product.html',
                    context = {
                        'product':product,
                        'categories':categories,
                        'images':images
                        }
                    )
    elif request.method == 'POST':
        # Validate following fields that come in request.POST in the very same
        # way that you've done it in create_product view
        fields = ['name', 'sku', 'price']
        errors = {}
        name = request.POST.get('name')
        if len(name) > 100:
            errors['name'] = "Name can't be longer than 100 characters."

        sku = request.POST.get('sku')
        if len(sku) != 8 or sku != re.match('\w*',sku).group():
            errors['sku'] = "Sku must contain 8 alphanumeric characters"

        price = request.POST.get('price')
        if float(price) >= 10000.0 or float(price) < 0.0:
            errors['price'] = "Price can't be negative or more than $9999.99"

        if errors:
            return render(
                request,
                'create_product.html',
                context={
                    'categories':categories,
                    'errors':errors,
                    'payload':request.POST
                    }
                )
    
        
        # If execution reaches this point, there aren't any errors.
        # Update product name, sku, price and description from the data that
        # come in request.POST dictionary.
        # Consider that ALL data is given as string, so you might format it
        # properly in some cases.
        product.name = name
        product.sku = sku
        product.price = float(price)
        # Get proper category from the DB based on the category name given in
        # payload. Update product category.
        category = Category.objects.get(name=request.POST.get('category'))
        product.category = category
        product.save()

        # For updating the product images URLs, there are a couple of things that
        # you must consider:
        # 1) Create a ProductImage object for each URL that came in payload and
        #    is not already created for this product.
        # 2) Delete all ProductImage objects for URLs that are created but didn't
        #    come in payload
        # 3) Keep all ProductImage objects that are created and also came in payload
        new_images=[]
        for i in range(1,4):
            image = request.POST.get(f"image_{i}")
            if image:
                new_images.append(image)
        
        current_images = [image.url for image in product.productimage_set.all()]
        for image in current_images:
            if image not in new_images:
                ProductImage.objects.filter(url=image).delete()
        
        for image in new_images:
            ProductImage.objects.create(product=product, url=image)
            

        # Redirect to 'products' view
        return redirect('products')


def delete_product(request, product_id):
    # Get product with given product_id
    product = Product.objects.get(id=product_id)  # <YOUR CODE HERE>
    if request.method == 'GET':
        # render 'delete_product.html' sending product as context
        return render(request,'delete_product.html',context={'product':product})  # <YOUR CODE HERE>
    elif request.method == "POST":
        product.delete()
        return redirect('products')  # <YOUR CODE HERE>


def toggle_featured(request, product_id):
    # Get product with given product_id
    product = Product.objects.get(id=product_id)  # <YOUR CODE HERE>

    # Toggle product featured flag
    product.featured = not product.featured 
    product.save()

    # Redirect to 'products' view
    return redirect('products')
