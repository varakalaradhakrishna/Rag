"""
Synthetic Dataset Generator for BBD E-Commerce Sales Platform.
Generates realistic e-commerce datasets reflecting festive season trends
(Electronics, Mobiles, Fashion, Home & Kitchen, Beauty & Grooming, Appliances).
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Reproducibility
random.seed(42)
np.random.seed(42)

CATEGORIES_PRODUCTS = {
    "Mobiles": [
        ("Apple iPhone 15 (128GB)", "Apple", 79900, 0.15),
        ("Samsung Galaxy S24 5G", "Samsung", 74999, 0.18),
        ("OnePlus 12R", "OnePlus", 39999, 0.12),
        ("Realme 12 Pro+ 5G", "Realme", 29999, 0.20),
        ("Xiaomi Redmi Note 13 Pro", "Xiaomi", 25999, 0.22),
        ("Google Pixel 8a", "Google", 52999, 0.15),
        ("Motorola Edge 50 Fusion", "Motorola", 22999, 0.18),
        ("POCO X6 Pro 5G", "POCO", 24999, 0.25)
    ],
    "Electronics": [
        ("Sony WH-1000XM5 Headphones", "Sony", 29990, 0.20),
        ("Boat Nirvana Ion Earbuds", "boAt", 4990, 0.60),
        ("Apple iPad 10th Gen", "Apple", 39900, 0.12),
        ("Dell Inspiron 15 Laptop", "Dell", 56990, 0.18),
        ("HP Pavilion Gaming Laptop", "HP", 68990, 0.22),
        ("Samsung 55-inch 4K Smart TV", "Samsung", 54990, 0.35),
        ("LG 43-inch UHD Smart TV", "LG", 38990, 0.30),
        ("Noise ColorFit Pro 5 Smartwatch", "Noise", 3999, 0.55),
        ("JBL Flip 6 Bluetooth Speaker", "JBL", 11999, 0.25)
    ],
    "Fashion": [
        ("Levi's 511 Slim Fit Jeans", "Levi's", 3999, 0.40),
        ("Puma Men Motorsport Sneakers", "Puma", 5499, 0.45),
        ("Nike Air Max Impact Shoes", "Nike", 7995, 0.30),
        ("Adidas Originals Trefoil Hoodie", "Adidas", 4599, 0.35),
        ("Zara Textured Casual Shirt", "Zara", 2990, 0.25),
        ("Allen Solly Formal Trousers", "Allen Solly", 2499, 0.35),
        ("Biba Women Embroidered Kurta", "Biba", 3299, 0.50),
        ("FabIndia Cotton Printed Saree", "FabIndia", 4990, 0.30)
    ],
    "Home & Kitchen": [
        ("Philips Digital Air Fryer", "Philips", 10995, 0.35),
        ("Prestige Iris 750W Mixer Grinder", "Prestige", 4295, 0.40),
        ("Milton Thermosteel 1L Flask", "Milton", 1150, 0.20),
        ("Wakefit Orthopedic Memory Mattress", "Wakefit", 12499, 0.30),
        ("Bajaj New Shakti Neo Water Heater", "Bajaj", 6999, 0.32),
        ("Kent Grand Plus RO Water Purifier", "Kent", 18500, 0.22)
    ],
    "Beauty & Grooming": [
        ("Philips Series 3000 Beard Trimmer", "Philips", 1895, 0.25),
        ("Minimalist 10% Niacinamide Serum", "Minimalist", 599, 0.10),
        ("The Derma Co 1% Hyaluronic Sunscreen", "The Derma Co", 499, 0.15),
        ("Maybelline New York Matte Lipstick", "Maybelline", 449, 0.30),
        ("L'Oreal Paris Total Repair Hair Mask", "L'Oreal", 499, 0.20),
        ("Bombay Shaving Co Grooming Kit", "Bombay Shaving Co", 1499, 0.40)
    ],
    "Appliances": [
        ("LG 8kg Front Load Washing Machine", "LG", 41990, 0.28),
        ("Whirlpool 265L Frost Free Refrigerator", "Whirlpool", 32490, 0.25),
        ("Daikin 1.5 Ton 5 Star Inverter AC", "Daikin", 45990, 0.22),
        ("Godrej 190L Direct Cool Refrigerator", "Godrej", 16990, 0.20),
        ("IFB 6.5kg Top Load Washer", "IFB", 21990, 0.24)
    ]
}

GEOGRAPHY = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore"],
    "Delhi": ["New Delhi", "North Delhi", "South Delhi", "West Delhi"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad"],
    "Uttar Pradesh": ["Lucknow", "Noida", "Kanpur", "Varanasi", "Agra"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
    "West Bengal": ["Kolkata", "Howrah", "Siliguri", "Durgapur"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota"],
    "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode"],
    "Haryana": ["Gurgaon", "Faridabad", "Panipat"]
}

PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash on Delivery", "EMI"]
PAYMENT_WEIGHTS = [0.45, 0.25, 0.12, 0.05, 0.08, 0.05]

def generate_order_records(start_order_num: int, count: int, start_date: datetime, end_date: datetime) -> list:
    records = []
    days_span = (end_date - start_date).days
    
    # Pre-generate 3000 unique customer IDs
    customers = [f"CUST-{random.randint(10000, 99999)}" for _ in range(3500)]
    
    for i in range(count):
        order_id = f"BBD-{start_order_num + i:07d}"
        
        # Date distribution: spike around Big Billion Days (late Sept - early Oct)
        day_offset = random.randint(0, max(1, days_span))
        order_date = start_date + timedelta(days=day_offset, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        customer_id = random.choice(customers)
        
        category = random.choices(
            list(CATEGORIES_PRODUCTS.keys()),
            weights=[0.30, 0.25, 0.20, 0.12, 0.08, 0.05]
        )[0]
        
        product_info = random.choice(CATEGORIES_PRODUCTS[category])
        product_name, brand, base_mrp, typical_discount = product_info
        product_id = f"PROD-{abs(hash(product_name)) % 10000:04d}"
        
        # Introduce variation in discount during sale events
        discount_var = random.uniform(-0.06, 0.12)
        discount_percent = round(min(0.75, max(0.05, typical_discount + discount_var)) * 100, 1)
        
        mrp = float(base_mrp)
        sale_price = round(mrp * (1.0 - (discount_percent / 100.0)), 2)
        
        # Quantity
        if category in ["Mobiles", "Appliances"]:
            quantity = random.choices([1, 2], weights=[0.92, 0.08])[0]
        elif category in ["Electronics", "Home & Kitchen"]:
            quantity = random.choices([1, 2, 3], weights=[0.80, 0.15, 0.05])[0]
        else:
            quantity = random.choices([1, 2, 3, 4], weights=[0.60, 0.25, 0.10, 0.05])[0]
            
        revenue = round(sale_price * quantity, 2)
        
        # Profit modeling: Margin typically 8% to 28% depending on category and discount depth
        base_cost_margin = {
            "Mobiles": 0.07,
            "Electronics": 0.14,
            "Fashion": 0.32,
            "Home & Kitchen": 0.22,
            "Beauty & Grooming": 0.35,
            "Appliances": 0.12
        }[category]
        
        margin_impact = (discount_percent / 100.0) * 0.20
        effective_margin = max(0.02, base_cost_margin - margin_impact + random.uniform(-0.02, 0.04))
        profit = round(revenue * effective_margin, 2)
        
        state = random.choice(list(GEOGRAPHY.keys()))
        city = random.choice(GEOGRAPHY[state])
        payment_method = random.choices(PAYMENT_METHODS, weights=PAYMENT_WEIGHTS)[0]
        
        # Rating (1.0 to 5.0)
        rating = round(random.choices(
            [5.0, 4.5, 4.0, 3.5, 3.0, 2.0, 1.0],
            weights=[0.45, 0.25, 0.15, 0.08, 0.04, 0.02, 0.01]
        )[0], 1)
        
        delivery_days = random.choices([1, 2, 3, 4, 5, 6, 7], weights=[0.20, 0.35, 0.25, 0.10, 0.05, 0.03, 0.02])[0]
        
        # Return flag: Higher in Fashion (12-18%), lower in Mobiles (3-5%)
        base_return_rate = {
            "Fashion": 0.16,
            "Home & Kitchen": 0.08,
            "Beauty & Grooming": 0.04,
            "Electronics": 0.06,
            "Mobiles": 0.03,
            "Appliances": 0.05
        }[category]
        return_flag = 1 if random.random() < base_return_rate else 0
        
        records.append({
            "Order_ID": order_id,
            "Order_Date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "Customer_ID": customer_id,
            "Product_ID": product_id,
            "Product_Name": product_name,
            "Category": category,
            "Brand": brand,
            "MRP": mrp,
            "Discount_Percent": discount_percent,
            "Sale_Price": sale_price,
            "Quantity": quantity,
            "Revenue": revenue,
            "Profit": profit,
            "State": state,
            "City": city,
            "Payment_Method": payment_method,
            "Rating": rating,
            "Delivery_Days": delivery_days,
            "Return_Flag": return_flag
        })
        
    return records

def main():
    target_dir = os.path.join(os.path.dirname(__file__), "sample")
    os.makedirs(target_dir, exist_ok=True)
    
    print("Generating Initial BBD Dataset (10,500 records)...")
    initial_records = generate_order_records(
        start_order_num=100000,
        count=10500,
        start_date=datetime(2025, 8, 1),
        end_date=datetime(2025, 10, 15)
    )
    df_initial = pd.DataFrame(initial_records)
    initial_csv_path = os.path.join(target_dir, "bbd_initial_sales_dataset.csv")
    df_initial.to_csv(initial_csv_path, index=False)
    print(f"Saved: {initial_csv_path} (Shape: {df_initial.shape})")
    
    print("\nGenerating Secondary Batch (3,000 new records for late October / November)...")
    batch2_records = generate_order_records(
        start_order_num=110500,
        count=3000,
        start_date=datetime(2025, 10, 16),
        end_date=datetime(2025, 11, 20)
    )
    df_batch2 = pd.DataFrame(batch2_records)
    batch2_csv_path = os.path.join(target_dir, "bbd_batch2_october_sales.csv")
    df_batch2.to_csv(batch2_csv_path, index=False)
    print(f"Saved: {batch2_csv_path} (Shape: {df_batch2.shape})")
    
    print("\nGenerating Batch 3 XLSX with 500 duplicates and 1,000 new records...")
    # Take 500 from batch 2 as duplicates
    duplicate_records = batch2_records[:500]
    new_records = generate_order_records(
        start_order_num=113500,
        count=1000,
        start_date=datetime(2025, 11, 21),
        end_date=datetime(2025, 12, 15)
    )
    combined_batch3 = duplicate_records + new_records
    random.shuffle(combined_batch3)
    df_batch3 = pd.DataFrame(combined_batch3)
    batch3_xlsx_path = os.path.join(target_dir, "bbd_batch3_with_duplicates.xlsx")
    df_batch3.to_excel(batch3_xlsx_path, index=False)
    print(f"Saved: {batch3_xlsx_path} (Shape: {df_batch3.shape})")

if __name__ == "__main__":
    main()
