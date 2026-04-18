
import json
import os

new_products = [
    # Coffee
    {"name": "Americano", "category": "Coffee", "description": "Classic espresso diluted with hot water, yielding a smooth, black coffee profile with the full-bodied spirit of espresso.", "ingredients": ["Espresso", "Hot Water"], "price": 280, "rating": 4.5, "image_path": "americano.jpg"},
    {"name": "Flat White", "category": "Coffee", "description": "A sophisticated balance of micro-foamed milk poured over a double shot of espresso for a silky texture.", "ingredients": ["Double Espresso", "Microfoam Milk"], "price": 420, "rating": 4.9, "image_path": "flat_white.jpg"},
    {"name": "Cortado", "category": "Coffee", "description": "Equal parts espresso and warm milk to reduce the acidity while maintaining the bold coffee flavor.", "ingredients": ["Espresso", "Steamed Milk"], "price": 310, "rating": 4.7, "image_path": "cortado.jpg"},
    {"name": "Macchiato", "category": "Coffee", "description": "A bold espresso 'marked' with a small dollop of frothy milk, perfect for those who like a punchy caffeine kick.", "ingredients": ["Espresso", "Milk Foam"], "price": 260, "rating": 4.4, "image_path": "macchiato.jpg"},
    {"name": "Affogato", "category": "Coffee", "description": "A blissful dessert-coffee hybrid: a scoop of premium vanilla bean gelato 'drowned' in a hot shot of espresso.", "ingredients": ["Espresso", "Vanilla Gelato"], "price": 450, "rating": 4.9, "image_path": "affogato.jpg"},

    # Cold Brew & Iced
    {"name": "Classic Cold Brew", "category": "Cold Brew", "description": "Steeped for 18 hours in small batches for an ultra-smooth, low-acid, and naturally sweet caffeine hit.", "ingredients": ["Coffee", "Water"], "price": 350, "rating": 4.8, "image_path": "cold_brew.jpg"},
    {"name": "Vanilla Cloud Cold Brew", "category": "Cold Brew", "description": "Our signature cold brew topped with a light, airy layer of vanilla-infused cold foam.", "ingredients": ["Cold Brew", "Vanilla Cold Foam"], "price": 440, "rating": 4.7, "image_path": "vanilla_cloud.jpg"},
    {"name": "Nitro Cold Brew", "category": "Cold Brew", "description": "Infused with nitrogen for a velvety, stout-like texture and a naturally creamy head.", "ingredients": ["Nitrogen-infused Cold Brew"], "price": 480, "rating": 4.9, "image_path": "nitro.jpg"},
    {"name": "Iced Caramel Macchiato", "category": "Iced Coffee", "description": "Layers of milk and espresso over ice, finished with a generous drizzle of our house caramel sauce.", "ingredients": ["Espresso", "Milk", "Caramel Sauce", "Ice"], "price": 460, "rating": 4.6, "image_path": "iced_caramel.jpg"},
    {"name": "Iced Matcha Latte", "category": "Tea", "description": "Premium ceremonial grade matcha whisked with milk and served over ice for a vibrant, earthy energy boost.", "ingredients": ["Matcha", "Milk", "Ice"], "price": 480, "rating": 4.7, "image_path": "matcha_iced.jpg"},
    {"name": "Midnight Cocoa Cold Brew", "category": "Cold Brew", "description": "A dark, intense cold brew blended with subtle hints of Peruvian cocoa for a chocolatey finish.", "ingredients": ["Cold Brew", "Cocoa Essence"], "price": 450, "rating": 4.6, "image_path": "midnight_cocoa.jpg"},

    # Seasonal Specials
    {"name": "Pumpkin Spice Latte", "category": "Seasonal", "description": "The autumn classic: espresso and steamed milk with warm spices (cinnamon, nutmeg, cloves) and real pumpkin.", "ingredients": ["Espresso", "Steamed Milk", "Pumpkin Spice", "Whipped Cream"], "price": 490, "rating": 4.8, "image_path": "psl.jpg"},
    {"name": "Peppermint Mocha", "category": "Seasonal", "description": "A winter favorite featuring bittersweet chocolate, peppermint syrup, espresso, and steamed milk.", "ingredients": ["Espresso", "Steamed Milk", "Chocolate", "Peppermint Syrup"], "price": 520, "rating": 4.7, "image_path": "peppermint_mocha.jpg"},
    {"name": "Mango Passion Iced Tea", "category": "Seasonal", "description": "Tropical bliss in a cup: hand-shaken herbal tea with mango and passion fruit pur\u00e9e.", "ingredients": ["Herbal Tea", "Mango Pur\u00e9e", "Passion Fruit", "Ice"], "price": 390, "rating": 4.5, "image_path": "mango_tea.jpg"},
    {"name": "Honey Lavender Latte", "category": "Seasonal", "description": "A fragrant, calming blend of espresso, floral lavender, and organic local honey.", "ingredients": ["Espresso", "Steamed Milk", "Lavender Syrup", "Honey"], "price": 480, "rating": 4.6, "image_path": "honey_lavender.jpg"},

    # Vegan & Healthy
    {"name": "Oat Milk Honey Latte", "category": "Healthy", "description": "Creamy oat milk perfectly paired with rich espresso and a touch of wild honey.", "ingredients": ["Espresso", "Oat Milk", "Honey"], "price": 450, "rating": 4.8, "image_path": "oat_honey.jpg"},
    {"name": "Acai Berry Bowl", "category": "Healthy", "description": "Frozen acai pur\u00e9e topped with granola, fresh berries, sliced banana, and a drizzle of honey.", "ingredients": ["Acai", "Granola", "Berries", "Banana", "Honey"], "price": 550, "rating": 4.9, "image_path": "acai_bowl.jpg"},
    {"name": "Avocado Smash Toast", "category": "Healthy", "description": "Zesty mashed avocado on sourdough bread with chili flakes, seeds, and a squeeze of lemon.", "ingredients": ["Sourdough", "Avocado", "Chili Flakes", "Seeds", "Lemon"], "price": 420, "rating": 4.7, "image_path": "avo_toast.jpg"},
    {"name": "Vegan Blueberry Muffin", "category": "Healthy", "description": "Light, moist, and bursting with fresh blueberries — made without any animal products.", "ingredients": ["Flour", "Blueberries", "Oat Milk", "Applesauce", "Sugar"], "price": 280, "rating": 4.6, "image_path": "vegan_muffin.jpg"},
    {"name": "Quinoa Veggie Salad", "category": "Healthy", "description": "A colorful mix of roasted seasonal veggies, fluffy quinoa, and a tangy balsamic vinaigrette.", "ingredients": ["Quinoa", "Roasted Veggies", "Balsamic Vinaigrette"], "price": 480, "rating": 4.5, "image_path": "quinoa_salad.jpg"},

    # Bakery
    {"name": "Blueberry Scone", "category": "Bakery", "description": "Crumbly and sweet, packed with plump blueberries and finished with a sugary glaze.", "ingredients": ["Flour", "Butter", "Blueberries", "Sugar", "Glaze"], "price": 310, "rating": 4.6, "image_path": "blueberry_scone.jpg"},
    {"name": "Spinach & Feta Swirl", "category": "Bakery", "description": "Savory puff pastry filled with creamy feta cheese and tender sautéed spinach.", "ingredients": ["Flour", "Butter", "Spinach", "Feta Cheese"], "price": 340, "rating": 4.7, "image_path": "spinach_swirl.jpg"},
    {"name": "Pain au Chocolat", "category": "Bakery", "description": "Classic French pastry with buttery layers and two bars of rich dark chocolate hidden inside.", "ingredients": ["Flour", "Butter", "Dark Chocolate", "Yeast"], "price": 360, "rating": 4.8, "image_path": "pain_au_chocolat.jpg"},
    {"name": "Berry Danish", "category": "Bakery", "description": "Sweet yeast pastry with a custard center topped with fresh seasonal berries and a honey glaze.", "ingredients": ["Flour", "Yeast", "Custard", "Berries", "Honey"], "price": 350, "rating": 4.4, "image_path": "berry_danish.jpg"},
    {"name": "Pecan Brownie", "category": "Bakery", "description": "Fudgy, dense chocolate brownie topped with crunchy toasted pecans.", "ingredients": ["Cocoa", "Sugar", "Butter", "Pecans", "Eggs"], "price": 290, "rating": 4.8, "image_path": "pecan_brownie.jpg"},
    {"name": "Banana Nut Bread", "category": "Bakery", "description": "Moist and dense loaf made with overripe bananas and crunchy walnuts.", "ingredients": ["Bananas", "Walnuts", "Flour", "Sugar", "Eggs"], "price": 260, "rating": 4.7, "image_path": "banana_bread.jpg"},
    {"name": "Lemon Poppyseed Cake", "category": "Bakery", "description": "Zesty lemon sponge cake with crunchy poppyseeds and a tart lemon icing.", "ingredients": ["Flour", "Sugar", "Lemon", "Poppyseeds", "Icing"], "price": 280, "rating": 4.6, "image_path": "lemon_cake.jpg"},
    {"name": "Cinnamon Roll", "category": "Bakery", "description": "Soft brioche dough swirled with cinnamon sugar and topped with thick cream cheese frosting.", "ingredients": ["Flour", "Cinnamon", "Sugar", "Cream Cheese"], "price": 380, "rating": 4.9, "image_path": "cinnamon_roll.jpg"},

    # Drinking Chocolate
    {"name": "White Chocolate Mocha", "category": "Drinking Chocolate", "description": "Smooth white chocolate sauce combined with espresso and perfectly steamed milk.", "ingredients": ["White Chocolate", "Espresso", "Steamed Milk"], "price": 480, "rating": 4.7, "image_path": "white_mocha.jpg"},
    {"name": "Mexican Hot Chocolate", "category": "Drinking Chocolate", "description": "A spicy twist on hot cocoa: rich chocolate with hints of cinnamon and a kick of chili.", "ingredients": ["Cocoa", "Cinnamon", "Chili", "Milk", "Sugar"], "price": 440, "rating": 4.6, "image_path": "mexican_hot_choc.jpg"},
    {"name": "Salted Caramel Cocoa", "category": "Drinking Chocolate", "description": "Velvety hot chocolate enhanced with sea salt and buttery caramel syrup.", "ingredients": ["Cocoa", "Caramel", "Sea Salt", "Milk"], "price": 460, "rating": 4.8, "image_path": "salted_caramel_cocoa.jpg"},

    # Gourmet Beans
    {"name": "Ethiopia Yirgacheffe (250g)", "category": "Beans", "description": "Single-origin beans featuring bright floral notes and a clean, citrusy acidity.", "ingredients": ["100% Arabica Beans"], "price": 950, "rating": 4.9, "image_path": "ethiopia_beans.jpg"},
    {"name": "Sumatra Mandheling (250g)", "category": "Beans", "description": "Full-bodied and low-acid beans with earthy, mossy notes and a smooth finish.", "ingredients": ["100% Arabica Beans"], "price": 880, "rating": 4.8, "image_path": "sumatra_beans.jpg"},
    {"name": "Brazil Santos (250g)", "category": "Beans", "description": "Naturally low-acid beans with nutty, chocolaty undertones and a mellow profile.", "ingredients": ["100% Arabica Beans"], "price": 820, "rating": 4.7, "image_path": "brazil_beans.jpg"},
    {"name": "House Blend (500g)", "category": "Beans", "description": "Our balanced signature blend, perfect for both espresso and filter brewing.", "ingredients": ["Multi-origin Arabica Blend"], "price": 1450, "rating": 4.9, "image_path": "house_blend.jpg"},

    # Flavours
    {"name": "Irish Cream Syrup", "category": "Flavours", "description": "Rich and creamy with hints of vanilla and cocoa, inspired by traditional Irish spirits.", "ingredients": ["Sugar", "Water", "Natural Flavours"], "price": 140, "rating": 4.5, "image_path": "irish_cream.jpg"},
    {"name": "Cinnamon Syrup", "category": "Flavours", "description": "Sweet syrup infused with the warm, woody spice of premium cinnamon bark.", "ingredients": ["Sugar", "Cinnamon Extract", "Water"], "price": 130, "rating": 4.4, "image_path": "cinnamon_syrup.jpg"},
    {"name": "Pumpkin Spice Syrup", "category": "Flavours", "description": "Warm autumn spices blended into a sweet syrup, essential for any festive drink.", "ingredients": ["Sugar", "Pumpkin Puree Extract", "Spices"], "price": 150, "rating": 4.8, "image_path": "ps_syrup.jpg"},
    {"name": "Toffee Nut Syrup", "category": "Flavours", "description": "A buttery, sweet syrup with the aroma of toasted nuts and rich toffee.", "ingredients": ["Sugar", "Toffee Flavour", "Water"], "price": 140, "rating": 4.7, "image_path": "toffee_nut.jpg"},
    {"name": "White Chocolate Sauce", "category": "Flavours", "description": "A thick, velvety sauce made with real cocoa butter for the ultimate indulgence.", "ingredients": ["Sugar", "Cocoa Butter", "Milk Solid"], "price": 180, "rating": 4.9, "image_path": "white_choc_sauce.jpg"},
]

DATA_PATH = "/Users/pandhari/Desktop/Coffee_Shop_ChatBot/backend/data/products_data/products.jsonl"

with open(DATA_PATH, "a") as f:
    for product in new_products:
        f.write(json.dumps(product) + "\n")

print(f"Successfully appended {len(new_products)} new products to {DATA_PATH}")
