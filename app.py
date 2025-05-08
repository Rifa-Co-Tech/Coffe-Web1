from flask import Flask, render_template, request, redirect, url_for
from collections import defaultdict

app = Flask(__name__)

# Data contoh
coffee_shops = [
    {
        'id': 1,
        'name': 'Kopi Kenangan',
        'rating': 4.5,
        'distance': 0.8,
        'menu': [
            {'name': 'Latte', 'price': 15000},
            {'name': 'Cappuccino', 'price': 18000}
        ]
    },
    {
        'id': 2,
        'name': 'Janji Jiwa',
        'rating': 4.7,
        'distance': 1.2,
        'menu': [
            {'name': 'Espresso', 'price': 12000},
            {'name': 'Americano', 'price': 15000}
        ]
    },
    {
        'id' : 3,
        'name' : 'Coffe Night',
        'rating' : 4.5,
        'distance' : 1.0,
        'menu' : [
            {'name' : 'Arabica', 'price' : 15000},
            {'name' : 'Arabica Gayo', 'price' : 18000 }
        ]
    }
    
]

# Merge sort untuk rating
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i]['rating'] > right[j]['rating']:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged

# Quick sort untuk harga
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr)//2]
    left = [x for x in arr if x['price'] < pivot['price']]
    middle = [x for x in arr if x['price'] == pivot['price']]
    right = [x for x in arr if x['price'] > pivot['price']]
    return quick_sort(left) + middle + quick_sort(right)

# Cart in-memory
cart = defaultdict(list)

@app.route('/')
def index():
    print("Route '/' diakses")
    sort_type = request.args.get('sort', 'rating')
    search_query = request.args.get('search', '')
    
    filtered_shops = [
        shop for shop in coffee_shops 
        if search_query.lower() in shop['name'].lower() or 
        any(search_query.lower() in item['name'].lower() for item in shop['menu'])
    ]
    
    if sort_type == 'rating':
        sorted_shops = merge_sort(filtered_shops)
    elif sort_type == 'price':
        sorted_shops = []
        for shop in filtered_shops:
            sorted_menu = quick_sort(shop['menu'])
            sorted_shops.append({**shop, 'menu': sorted_menu})
    else:
        sorted_shops = filtered_shops
        
    return render_template('index.html', 
                           shops=sorted_shops,
                           search_query=search_query,
                           sort_type=sort_type)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    shop_id = int(request.form['shop_id'])
    item_name = request.form['item_name']
    quantity = int(request.form['quantity'])

    shop = next(shop for shop in coffee_shops if shop['id'] == shop_id)
    item = next(item for item in shop['menu'] if item['name'] == item_name)

    cart[shop_id].append({
        'item': item,
        'quantity': quantity
    })
    
    return redirect(url_for('view_order'))

@app.route('/order')
def view_order():
    total = sum(
        item['item']['price'] * item['quantity']
        for items in cart.values()
        for item in items
    )
    return render_template('order.html', cart=cart, total=total)

if __name__ == '__main__':
    app.run(debug=True)
