# ecommerce_data_generator.py
import pandas as pd
import numpy as np
import random
import csv
import string
from datetime import datetime, timedelta


random.seed(0)
np.random.seed(0)

NUM_ROWS = 100000

#Sample Data
PRODUCT_NAMES = ["Laptop", "Smartphone", "Headphones", "Smartwatch", "Backpack", "Shoes", "T-shirt", "Book", "Camera", "Gaming Console"]
CATEGORIES = {"Laptop": "Electronics", "Smartphone": "Electronics", "Headphones": "Electronics", "Smartwatch": "Electronics", "Camera": "Electronics", "Gaming Console": "Gaming", "Backpack": "Accessories", "Shoes": "Apparel", "T-shirt": "Apparel", "Book": "Books"}
PAYMENT_METHODS = ["Credit Card", "Debit Card", "PayPal", "COD", "UPI"]
FIRST_NAMES = ["John", "Jane", "Alex", "Chris", "Katie", "Mike", "Laura", "Tom", "Anna", "James"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson", "Clark", "Lewis"]

#fraudulent emails ---
DISPOSABLE_DOMAINS = ["mailinator.com", "temp-mail.org", "10minutemail.com", "guerrillamail.com"]
GIBBERISH_DOMAINS = ["xyzabc.com", "fakedomain.net", "randomsite.org"]

#helper functions
def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

def generate_gibberish(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

#data generation
rows = []
start_date = datetime.now() - timedelta(days=365)
end_date = datetime.now()

print(f"Generating {NUM_ROWS} rows of synthetic data with email fraud patterns...")

for i in range(1, NUM_ROWS + 1):
    is_fraud = random.choices([0, 1], weights=[97, 3])[0] # 3% fraud rate
    customer_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

    if is_fraud:
        fraud_type = random.choice(['disposable', 'gibberish', 'plus_address'])
        if fraud_type == 'disposable':
            customer_email = f"{generate_gibberish()}@{random.choice(DISPOSABLE_DOMAINS)}"
        elif fraud_type == 'gibberish':
            customer_email = f"{generate_gibberish()}@{random.choice(GIBBERISH_DOMAINS)}"
        else: # plus_address
            customer_email = f"john.doe+{random.randint(1, 100)}@gmail.com"
    else:
        customer_email = f"{customer_name.replace(' ', '.').lower()}@example.com"

    product_name = random.choice(PRODUCT_NAMES)
    quantity = random.randint(1, 3)
    price_per_unit = round(random.uniform(20.0, 1500.0), 2)
    total_price = round(price_per_unit * quantity, 2)
    discount = round(total_price * random.choice([0, 0.05, 0.10, 0.15, 0.20]), 2)
    cost_price_per_unit = round(price_per_unit * random.uniform(0.6, 0.85), 2)
    profit = round(total_price - discount - round(cost_price_per_unit * quantity, 2), 2)

    row = {
        "order_id": f"ORD{i:07d}",
        "order_date": random_date(start_date, end_date).strftime('%Y-%m-%d'),
        "customer_name": customer_name,
        "customer_email": customer_email,
        "product_name": product_name,
        "category": CATEGORIES[product_name],
        "quantity": quantity,
        "price_per_unit": price_per_unit,
        "total_price": total_price,
        "total_discount": discount,
        "coupon_code": random.choice(["SUMMER20", "NEWUSER10", ""]) if discount > 0 else "",
        "cost_price_per_unit": cost_price_per_unit,
        "total_cost": round(cost_price_per_unit * quantity, 2),
        "profit": profit,
        "payment_method": random.choice(PAYMENT_METHODS),
        "shipping_address": f"{random.randint(100, 999)} Main St",
        "city": "Anytown",
        "state": "CA",
        "postal_code": f"{random.randint(10000, 99999)}",
        "is_fraud": is_fraud
    }
    rows.append(row)

#to CSV
csv_filename = "synthetic_ecommerce_data_with_email_fraud.csv"
with open(csv_filename, 'w', newline='', encoding='utf-8') as output_file:
    dict_writer = csv.DictWriter(output_file, rows[0].keys())
    dict_writer.writeheader()
    dict_writer.writerows(rows)

print(f"Successfully created '{csv_filename}'.")
