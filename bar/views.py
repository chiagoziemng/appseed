# bar/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views import View
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas  # Add this import statement
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from .models import Category, Drink, Order, Transaction, Invoice, DrinkHistory
from .forms import DrinkForm ,  DrinkFilterForm 



class DashboardView(View):
    template_name = 'dashboard.html'

    def get(self, request):
        # Calculate total sales
        total_sales = Transaction.objects.aggregate(total_sales=models.Sum('total_amount'))['total_sales'] or 0

        # Get top-selling drinks based on quantity sold
        top_selling_drinks = Drink.objects.annotate(quantity_sold=models.Sum('order__quantity')).order_by('-quantity_sold')[:5]

        # Get available inventory
        available_inventory = Drink.objects.all()

        return render(request, self.template_name, {
            'total_sales': total_sales,
            'top_selling_drinks': top_selling_drinks,
            'available_inventory': available_inventory,
        })
    
class DrinkListView(View):
    template_name = 'drink_list.html'

    def get(self, request):
        # Retrieve all drinks by default
        drinks = Drink.objects.all()

        # Get the filter form
        form = DrinkFilterForm(request.GET)

        if form.is_valid():
            # Apply filters if form is submitted
            name = form.cleaned_data.get('name')
            category = form.cleaned_data.get('category')

            if name:
                drinks = drinks.filter(name__icontains=name)

            if category:
                drinks = drinks.filter(category=category)

        # Add pagination
        paginator = Paginator(drinks, 10)  # Show 10 drinks per page
        page = request.GET.get('page')
        try:
            drinks = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver the first page.
            drinks = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver the last page of results.
            drinks = paginator.page(paginator.num_pages)

        return render(request, self.template_name, {'drinks': drinks, 'form': form})
    

class DrinkDetailView(View):
    template_name = 'drink_detail.html'

    def get(self, request, pk):
        # Get the drink object
        drink = get_object_or_404(Drink, pk=pk)
        return render(request, self.template_name, {'drink': drink})

    def post(self, request, pk):
        # Get the drink object
        drink = get_object_or_404(Drink, pk=pk)
        form = DrinkForm(request.POST, instance=drink)
        
        if form.is_valid():
            # Record the drink quantity change in DrinkHistory
            new_quantity = form.cleaned_data['quantity_in_stock']
            old_quantity = drink.quantity_in_stock
            if new_quantity != old_quantity:
                action = "ADD" if new_quantity > old_quantity else "REDUCE"
                quantity_changed = abs(new_quantity - old_quantity)
                DrinkHistory.objects.create(drink=drink, action=action, quantity_changed=quantity_changed)

            form.save()
            return redirect('drink_detail', pk=pk)

        return render(request, self.template_name, {'drink': drink, 'form': form})

    
class UpdateDrinkView(View):
    template_name = 'drink_update.html'

    def get(self, request, pk):
        # Get the drink object to be updated
        drink = get_object_or_404(Drink, pk=pk)
        form = DrinkForm(instance=drink)
        return render(request, self.template_name, {'form': form})

    def post(self, request, pk):
        # Get the drink object to be updated
        drink = get_object_or_404(Drink, pk=pk)
        form = DrinkForm(request.POST, instance=drink)
        
        if form.is_valid():
            form.save()
            return redirect('drink_list')

        return render(request, self.template_name, {'form': form})
    
class DeleteDrinkView(View):
    template_name = 'drink_confirm_delete.html'

    def get(self, request, pk):
        # Get the drink object to be deleted
        drink = get_object_or_404(Drink, pk=pk)
        return render(request, self.template_name, {'drink': drink})

    def post(self, request, pk):
        # Get the drink object to be deleted
        drink = get_object_or_404(Drink, pk=pk)

        # Perform the deletion
        drink.delete()

        # Redirect to the drink list after successful deletion
        return redirect('drink_list')
    
class DownloadPDFView(View):
    def get(self, request):
        # Fetch all drinks from the database
        drinks = Drink.objects.all()

        # Create a PDF file
        response = HttpResponse(content_type='application/pdf')  # Use HttpResponse to send the PDF content
        response['Content-Disposition'] = 'attachment; filename="drink_list.pdf"'  # Set the filename for the download
        p = canvas.Canvas(response, pagesize=letter)

        # Define the font and font size
        font_name = "Helvetica"
        font_size = 12

        # Set the header and footer
        header_text = "Drink List"
        footer_text = "Bar Management System"

        # Position for writing text
        x, y = 100, 800
        line_spacing = 20

        # Write header
        p.setFont(font_name, font_size + 4)
        p.drawString(x, y, header_text)
        y -= line_spacing

        # Write drink details
        p.setFont(font_name, font_size)
        for drink in drinks:
            p.drawString(x, y, f"Drink Name: {drink.name}")
            y -= line_spacing
            p.drawString(x, y, f"Price: ${drink.price:.2f}")
            y -= line_spacing
            p.drawString(x, y, f"Quantity in Stock: {drink.quantity_in_stock}")
            y -= line_spacing
            p.drawString(x, y, "-" * 50)
            y -= line_spacing

        # Write footer
        p.drawString(x, 50, footer_text)

        # Save the PDF file
        p.showPage()
        p.save()

        # Return the HttpResponse
        return response

class AllCategoriesView(View):
    template_name = 'all_categories.html'

    def get(self, request):
        categories = Category.objects.all()
        return render(request, self.template_name, {'categories': categories})

class CreateCategoryView(View):
    template_name = 'create_category.html'

    def post(self, request):
        category_name = request.POST.get('category_name')
        category = Category.objects.create(name=category_name)
        return redirect('drink_list')

    def get(self, request):
        return render(request, self.template_name)

class AddDrinkView(View):
    template_name = 'add_drink.html'

    def post(self, request):
        drink_name = request.POST.get('drink_name')
        drink_price = float(request.POST.get('drink_price', 0))
        drink_quantity = int(request.POST.get('drink_quantity', 0))
        category_id = int(request.POST.get('drink_category'))

        category = Category.objects.get(pk=category_id)

        drink = Drink.objects.create(
            name=drink_name,
            price=drink_price,
            quantity_in_stock=drink_quantity,
            category=category
        )
        return redirect('drink_list')

    def get(self, request):
        categories = Category.objects.all()
        return render(request, self.template_name, {'categories': categories})


    
class CreateOrderView(View):
    template_name = 'create_order.html'

    def get(self, request):
        drinks = Drink.objects.all()
        return render(request, self.template_name, {'drinks': drinks})

    def post(self, request):
        drink_id = request.POST.get('drink_id')
        quantity = int(request.POST.get('quantity', 1))  # Default to 1 if quantity not provided
        drink = Drink.objects.get(pk=drink_id)
        total_price = drink.price * quantity  # Calculate the total price
        order = Order.objects.create(drink=drink, quantity=quantity, total_price=total_price)  # Set the total price
        
        # Add the drink ID to the cart session variable
        cart_items = request.session.get('cart', [])
        cart_items.append(drink.pk)
        request.session['cart'] = cart_items

        return redirect('cart')
    


class AddDrinkQuantityView(View):
    template_name = 'add_drink_quantity.html'

    def post(self, request, drink_id):
        drink = Drink.objects.get(pk=drink_id)
        quantity_to_add = int(request.POST.get('quantity_to_add', 0))
        if quantity_to_add > 0:
            drink.quantity_in_stock += quantity_to_add
            drink.save()
        return redirect('drink_list')

    def get(self, request, drink_id):
        drink = Drink.objects.get(pk=drink_id)
        return render(request, self.template_name, {'drink': drink})

class ReduceDrinkQuantityView(View):
    template_name = 'reduce_drink_quantity.html'

    def post(self, request, drink_id):
        drink = Drink.objects.get(pk=drink_id)
        quantity_to_reduce = int(request.POST.get('quantity_to_reduce', 0))
        if quantity_to_reduce > 0:
            drink.quantity_in_stock -= quantity_to_reduce
            drink.save()
        return redirect('drink_list')

    def get(self, request, drink_id):
        drink = Drink.objects.get(pk=drink_id)
        return render(request, self.template_name, {'drink': drink})
    


class CartView(View):
    template_name = 'cart.html'

    def get(self, request):
        # Retrieve cart items from the session
        cart_items = request.session.get('cart', [])
        drinks = Drink.objects.filter(pk__in=cart_items)

        # Calculate drink_quantity for each drink in the cart
        drink_quantities = {}
        for drink in drinks:
            drink_quantity = cart_items.count(drink.pk)
            drink_quantities[drink.pk] = drink_quantity
        return render(request, self.template_name, {'drinks': drinks, 'drink_quantities': drink_quantities})


    def post(self, request):
        # Retrieve cart items from the session
        cart_items = request.session.get('cart', [])

        # Get the drink ID to remove from the cart
        drink_id_to_remove = request.POST.get('drink_id_to_remove')

        if drink_id_to_remove:
            try:
                drink_id_to_remove = int(drink_id_to_remove)
                if drink_id_to_remove in cart_items:
                    cart_items.remove(drink_id_to_remove)
                    request.session['cart'] = cart_items
            except ValueError:
                pass  # Ignore if the drink_id_to_remove is not a valid integer

        return redirect('cart')
    

class CompleteTransactionView(View):
    template_name = 'complete_transaction.html'

    def post(self, request):
        # Retrieve cart items from the session
        cart_items = request.session.get('cart', [])
        
        # Check if the cart is empty
        if not cart_items:
            messages.warning(request, 'Your cart is empty.')
            return redirect('cart')

        # Fetch all drinks at once for optimization
        drinks = Drink.objects.filter(pk__in=cart_items)
        drink_quantities = {drink.pk: cart_items.count(drink.pk) for drink in drinks}

        # Check if there is sufficient quantity for each drink in the cart
        insufficient_drinks = []
        for drink_id, quantity in drink_quantities.items():
            drink = get_object_or_404(Drink, pk=drink_id)
            if quantity > drink.quantity_in_stock:
                insufficient_drinks.append(drink)

        if insufficient_drinks:
            return render(request, self.template_name, {'insufficient_drinks': insufficient_drinks})

        # Calculate the total price of the transaction
        total_price = sum(drink.price * quantity for drink, quantity in zip(drinks, drink_quantities.values()))

        # Create a new transaction
        transaction = Transaction.objects.create(total_amount=total_price)

        # Create orders and associate with the transaction
        for drink, quantity in zip(drinks, drink_quantities.values()):
            order = Order.objects.create(drink=drink, quantity=quantity, total_price=drink.price * quantity)
            transaction.orders.add(order)

            # Deduct the ordered quantity from the available quantity for each drink
            drink.quantity_in_stock -= quantity
            drink.save()

        # Create an invoice for the transaction
        invoice = Invoice.objects.create(transaction=transaction)

        # Clear the cart after completing the transaction
        request.session['cart'] = []

        # Redirect to the view_invoice page with the invoice ID
        return redirect('view_invoice', invoice_id=invoice.pk)

    def get(self, request):
        return redirect('cart')  





class ViewInvoiceView(View):
    template_name = 'view_invoice.html'

    def get(self, request, invoice_id):
        invoice = Invoice.objects.get(pk=invoice_id)
        return render(request, self.template_name, {'invoice': invoice})
    

class AllInvoicesView(View):
    template_name = 'all_invoices.html'

    def get(self, request):
        invoices = Invoice.objects.all()
        return render(request, self.template_name, {'invoices': invoices})



class TransactionView(View):
    def post(self, request):
        # Get cart items from the session
        cart_items = request.session.get('cart', [])
        drinks = Drink.objects.filter(pk__in=cart_items)

        # Create the order and calculate the total amount
        total_amount = 0
        orders = []
        for drink in drinks:
            quantity = cart_items.count(drink.pk)
            total_price = drink.price * quantity
            order = Order(drink=drink, quantity=quantity, total_price=total_price)
            orders.append(order)
            total_amount += total_price
            # Update the drink's quantity_in_stock
            drink.quantity_in_stock -= quantity
            drink.save()

        # Create a transaction and save it to the database
        transaction = Transaction(total_amount=total_amount)
        transaction.save()
        transaction.orders.set(orders)

        # Clear the cart
        request.session['cart'] = []

        # Generate an invoice for the transaction (optional)

        return render(request, 'transaction_complete.html', {'transaction': transaction})

