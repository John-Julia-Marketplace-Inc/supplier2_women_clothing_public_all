import os, re
import numpy as np
import pandas as pd

filename = 'private_repo/clean_data/new_clothes_cleaned.csv'

if os.path.exists(filename):
    os.remove(filename)
    
def round_to_5_or_0(x):
    return np.round(x / 5) * 5

COLOR_CATEGORIES = {
    'Blue': ['Blue', 'Navy', 'Aqua', 'Denim', 'Indigo', 'Periwinkle', 'Cobalt', 'Sapphire', 'Sky'],
    'Black': ['Black', 'Anthracite', 'Ebony'],
    'Green': ['Green', 'Olive', 'Emerald', 'Mint', 'Forest', 'Lichen'],
    'Red': ['Red', 'Bordeaux', 'Wine', 'Burgundy', 'Garnet', 'Salmon', 'Omnibus', 'Siren'],
    'Pink': ['Pink', 'Rose', 'Blush', 'Fuxia', 'Pansy'],
    'Yellow': ['Yellow', 'Mango', 'Pale Yellow', 'Mustard', 'Mimosa'],
    'White': ['White', 'Ivory', 'Cream', 'Eggshell', 'Optic', 'Snow'],
    'Grey': ['Grey', 'Gray', 'Slate', 'Melange', 'Pewter', 'Granite'],
    'Beige': ['Beige', 'Taupe', 'Camel', 'Sand', 'Tapioca', 'Latte'],
    'Brown': ['Brown', 'Cocoa', 'Chocolate', 'Hazel', 'Tobacco', 'Toffee', 'Mahogany'],
    'Purple': ['Purple', 'Violet', 'Aubergine'],
    'Orange': ['Orange', 'Rust', 'Clay', 'Sudan'],
    'Gold': ['Gold', 'Antique Gold'],
    'Bronze': ['Bronze'],
    'Velvet': ['Velvet', 'Fuchsia'],
    'Silver': ['Silver'],
    'Butter': ['Butter']
}

COLOR_MAP = {'Blu': 'Blue', 'Gris Macadam': 'Grey Macadamia', 'Melograno': 'Pomegranate', 'Tempete': 'Dark Grey',
             'Off White': 'White', 'Lead': 'Grey', 'Toast Pigment': 'Beige', 'Avorio': 'Ivory', 'Rope': 'Beige', 'Antrachite': 'Anthracite',
             'Nero / Panama': 'Black', 'Gris Fonce': 'Dark Grey', 'Alabastro': 'Alabaster', 'Cameo': 'Pink', 'Sarrasin': 'Light Brown', 'Ecorce': 'Khaki Brown',
             'Calico': 'Ivory', 'Pink Palm': 'Pink', 'Mimetic': 'Green', 'Spelt': 'Beige', 'Loch': 'Olive Green', 'Rugby Tan': 'Pink', 'Admiral': 'Light Blue',
             'Chantilly': 'Beige', 'Prussia': 'Blue Velvet', 'Buttercream': 'Ivory', 'Otter': 'Brown', 'Biscuit': 'Light Brown', 'Vapor': 'Ice Grey',
             'Rust': 'Light Brown', 'Quartz': 'Light Grey', 'Cipria': 'Powder Pink', 'Croissant': 'Beige', 'Macadamia': 'Ivory', 'Camel': 'Light Brown',
             'Iconic Milk': 'Ivory', 'Albino': 'Light Beige', 'Craie': 'Ivory', 'Coffee': 'Brown', 'Taupe': 'Grey', 'Desert': 'Beige', 'Rock': 'Beige', 'Fuchsia': 'Velvet',
             'Cacha': 'Beige', 'Stone': 'Beige', 'Mastic': 'Beige', 'Ghost': 'White', 'Tea / Mahogany': 'Beige', 'Moonston': 'Ivory', 'Panama': 'Ivory', 'Midnight': 'Dark Blue',
             'Tan': 'Light Brown', 'Jade': 'Green', 'Pale Moon': 'Ivory', 'Mother Of Pearl': 'Light Beige', 'Kaki': 'Beige', 'Travertine': 'Beige', 'Chunky Moss': 'Melange Brown', 
             'Limestone': 'Light Beige', 'Riviera': 'Indigo Blue', 'Barolo': 'Bordeaux', 'Cord': 'Beige', 'Beaver': 'Brown', 'New Chino': 'Beige', 'Hunter': 'Light Green',
             'Night': 'Black', 'Flax': 'Beige'}


standard_sizes = ['XXXS', 'XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL', 'XXXXL', 'XXXXXL']
us_sizes = ['00', '0', '2', '4', '6', '8', '10', '12', '14', '16', '18']
it_sizes = ['34', '36', '38', '40', '42', '44', '46', '48', '50', '52', '54']
eu_sizes = ['28', '30', '32', '34', '36', '38', '40', '42', '44', '46', '48']
fr_sizes = ['30', '32', '34', '36', '38', '40', '42', '44', '46', '48', '50']
uk_sizes = ['2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22']
num_sizes = ['00', '0', '1', '2', '3', '4', '5', '6']
jeans_sizes = ['22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34']
one_size = ['OS']


def get_color(x):    
    try:
        x = x.lower().strip()
        
        if '/' in x:
            return x.title()
        
        for key, values in COLOR_CATEGORIES.items():
            for v in values:
                if v.lower() in x:
                    return key
    except:
        return x

def get_color_fabric_country(x):
    try:
        split = x.split('<br>')
    except AttributeError:
        return None, None, None

    color = fabric = country = None

    for s in split:
        s = s.lower().strip()

        # Match colors
        if 'color' in s or 'colore' in s:
            color = s.replace('colore', '').replace('color', '').replace(':', '').replace('Blu ', 'Blue ').strip().title()

            # Check if color needs mapping
            color = COLOR_MAP.get(color, color)  # If color not in map, use the original color
        
        # Match fabric
        elif '%' in s:
            fabric = s.replace(';', '').strip().title()
        
        # Match country
        elif 'made in' in s:
            country = s.replace('made in', '').strip().title()
            if country == 'Eu':
                country = 'EU'

    return color, fabric, country

def get_sizes(x):
    sizes, quantities, prices, old_prices = [], [], [], []
    
    try:
        # Split the string by ';' to separate each block for Size, Quantity, Price, and Old Price
        for row in x.split(';'):
            # Use regex to find Size, Quantity, Price, and Old Price
            size_match = re.search(r'Size:\s*([^,]+)', row)
            quantity_match = re.search(r'Quantity:\s*([^,]+)', row)
            price_match = re.search(r'Price:\s*([€\d,\.]+)', row)  # Updated to handle comma-separated numbers
            old_price_match = re.search(r'Old Price:\s*([€\d,\.]+)', row)  # Updated to handle comma-separated numbers
            
            # If matches are found, append the results to the respective lists
            if size_match:
                sizes.append(size_match.group(1).strip())
            if quantity_match:
                quantities.append(quantity_match.group(1).strip())
            if price_match:
                prices.append(price_match.group(1).strip())
            if old_price_match:
                old_prices.append(old_price_match.group(1).strip())
    
        return sizes, quantities, prices, old_prices

    except AttributeError:
        return None, None, None, None
    
def get_material(x):
    if '<br>' in x:
        for row in x.split('<br>'):
            if '%' in row:
                return row.title()
    
    if '\n' in x:
        for row in x.split('\n'):
            if '%' in row:
                return row.title()
    
    return None


def get_country(x):
    if '<br>' in x:
        for row in x.split('<br>'):
            row = row.lower()
            if 'made in' in row:
                return row.replace('made in', '').title()
    
    if '\n' in x:
        for row in x.split('\n'):
            row = row.lower()
            if 'made in' in row:
                return row.replace('made in', '').title()
    
    return None

SIZES = ['NUMERIC', 'US', 'IT', 'EU', 'DK', 'DE', 'FR', 'UK', 'AU', 'JEANS', 'ONE SIZE', 'STANDARD']

def find_size(row):
    for k in SIZES:
        if k in row:
            if k == 'ONE SIZE':
                return 'OS'
            return k
    
    return None


def get_sizing(x):
    size, fit = None, None

    try:    
        for row in x.split('<br>'):
            if 'size' in row.lower() and 'true to' not in row.lower():
                if size is None:
                    size = find_size(row)
            elif ('fit' in row.lower() or 'waist' in row.lower()) and 'true to' not in row.lower() and 'fits' not in row.lower():
                fit = row.replace('Regolar', 'Regular').title()
                
    except AttributeError:
        return None, None

    return size, fit


size_mapping = {
    "STANDARD": standard_sizes,
    "US": us_sizes,
    "IT": it_sizes,
    "EU": eu_sizes,
    "FR": fr_sizes,
    "UK": uk_sizes,
    "NUM": num_sizes,
    "JEANS": jeans_sizes,
    "ONE_SIZE": one_size
}


def find_best_size_category(sizes):
    size_counts = {key: 0 for key in size_mapping.keys()}  # Initialize counts

    # Count the matches for each size chart
    for size in sizes:
        for category, chart in size_mapping.items():
            if size in chart:
                size_counts[category] += 1

    # Find the category with the maximum match
    best_category = max(size_counts, key=size_counts.get)
    
    # If no match found (all counts are zero), return None
    if size_counts[best_category] == 0:
        return None
    
    return best_category

def fix_vendors(x):
    x = x.lower()
    
    if 'moncler basic' in x:
        x = 'moncler'
    
    if 'self portrait' in x:
        x = 'Self-Portrait'
    
    if 'mm6' in x:
        return 'MM6 Maison Margiela'

    if 't shirt' in x:
        return 'T-Shirt'
    
    if 'comme de garcons' in x:
        return 'Comme Des Garçons'
    
    if 'carhartt wip' in x:
        return 'Carhartt WIP'
    
    if x == '"' or x == "''":
        return ''
    
    if 'golden goose' in x:
        return 'Golden Goose'
    
    return x.title()

def find_color(description, color_supplier):
    color = None
    try:
        for color in COLOR_CATEGORIES.keys():
            if color.lower() in description.lower():
                return color.title()
        
        if color_supplier:
            return color_supplier
        
        return None
        
    except AttributeError:
        return None


def main():
    data = pd.read_csv('private_repo/clean_data/new_clothes.csv')

    YEAR, SEASON = None, None

    # Process each row
    for idx, row in data.iterrows():
        color_supplier, fabric, country = get_color_fabric_country(row['Details'])
        
        # If color not found in details, try description
        if not color_supplier:
            color_supplier = get_color(row['Description'])
            
        color = get_color(color_supplier)
        
        if fabric is None:
            fabric = get_material(row['Description'])
            
        if country is None:
            country = get_country(row['Description'])

        sizes, quantities, prices, old_prices = get_sizes(row['Sizes and Quantities'])
        
        if sizes:
            sizes = ','.join(sizes)
        
        if quantities:
            quantities = ','.join(quantities)
            
        sizing_standard, fit = get_sizing(row['Size and Fit'])
        
        try:
            collection = '20' + row['Collection'][-2:]
            season = ' - '.join([x.title() for x in row['Collection'][:-2].strip().split(' ')])
            
            if YEAR is None:
                YEAR = collection
                SEASON = season
        except:
            collection = None
            season = None
        
        if sizing_standard == 'OS':
            sizes = 'OS'
            # quantities = 2
            
        description = (
            ''
            if pd.isna(row['Description']) or 'color' in row['Description'] or not isinstance(row['Description'], str)
            else f"<p>{row['Description']}</p>"
        )
        
        inventory = row['Stock Status']
        
        if color is None:
            color = find_color(description, color_supplier)
            
        try:
            retail_price = float(row['Discounted Price'].replace(',', '').replace('€', ''))
            # inventory = 'In Stock'
        except AttributeError:
            retail_price = 0
            # inventory = 'OUT OF STOCK'
        except ValueError:
            retail_price = 0
            # inventory = 'OUT OF STOCK'
        
        try:
            compare_prices = float(row['Retail Price'].replace(',', '').replace('€', ''))
        except AttributeError:
            if retail_price:
                compare_prices = retail_price
            else:
                compare_prices = 0
        except ValueError:
            compare_prices = 0
            # inventory = 'OUT OF STOCK'
        
        if inventory.lower() == 'out of stock':
            qty = 0
                
        if sizing_standard is None:
            continue
        
        try:
            retail_price *= 1.08
            compare_prices *= 1.08
            unit_cost = retail_price
            
            retail_price *= 1.25
            compare_prices *= 1.45
            
            retail_price = round_to_5_or_0(retail_price)
            compare_prices = round_to_5_or_0(compare_prices)
            
            tags = '>'.join(row['Breadcrumbs'].split('>')[1:-1]).strip()
            
            pd.DataFrame({
                'Product Title': [row['Product Title']],
                'Vendor': [fix_vendors(row['Vendor']).upper()],
                'SKU': [row['SKU']],
                'Supplier Sku': [row['SKU']],
                'Retail Price': [retail_price],
                'Compare To Price': [compare_prices],
                'Unit Cost': [unit_cost],
                'Year': [collection if collection else YEAR],
                'Season': [season if season is not None else SEASON],
                'Size': [sizes],
                'Qty': [quantities if inventory.lower() == 'in stock' else 0],
                'Inventory': [inventory],
                'Product Category': [tags],
                'Tags': [', '.join([tags, 'Final Sale', 'exor'])],
                'Color detail': [color],
                'Color Supplier': [color_supplier],
                'Material': [fabric],
                'Country': [country],
                'Sizing Standard': [sizing_standard],
                'Fit': [fit],
                'Description': [description],
                'Clean Images': [row['Images']]

            }).to_csv(filename, mode='a', header=not os.path.exists(filename), index=False)
        except AttributeError:
            print('Missing price for SKU:', row['SKU'])


def fix_numeric_sizes(sizes):
    temp = []
    for s in sizes:
        if '/' in s:
            temp.append(s.strip('/')[0])
        else:
            temp.append(s)
    return temp

def additional_preprocessing():
    data = pd.read_csv('private_repo/clean_data/new_clothes_cleaned.csv')
    
    mismatched_sizes_skus = []

    data = data[~(data['Sizing Standard'].isna()) & ~(data['Size'].isna()) & (~data['Qty'].isna())].drop_duplicates()

    for idx, row in data.iterrows():
        standard = str(row['Sizing Standard']).strip().upper()
        sizes = str(row['Size']).split(',')
        qty = row['Qty'].split(',')
        sku = row['SKU']
        
        sizes = fix_numeric_sizes(sizes)
        
        size_qty = dict(zip(sizes, qty))
        template_qty = None
        
        # Select appropriate template sizes based on the standard
        if 'Jeans' in row['Product Category']:
            found_size = False
            
            for size in jeans_sizes:
                if size in sizes:
                    found_size = True
            
            if found_size:
                template_qty = dict(zip(jeans_sizes, [0] * len(jeans_sizes)))
        
        if not template_qty:
            if standard == 'IT':
                template_qty = dict(zip(it_sizes, [0] * len(it_sizes)))
            elif standard == 'STANDARD':
                template_qty = dict(zip(standard_sizes, [0] * len(standard_sizes)))
            elif standard == 'US':
                template_qty = dict(zip(us_sizes, [0] * len(us_sizes)))
            elif standard == 'FR':
                template_qty = dict(zip(fr_sizes, [0] * len(fr_sizes)))
            elif standard in ['EU', 'DE', 'DK']:
                template_qty = dict(zip(eu_sizes, [0] * len(eu_sizes)))
            elif standard == 'NUMERIC':
                template_qty = dict(zip(num_sizes, [0] * len(num_sizes)))
            elif standard == 'JEANS':
                template_qty = dict(zip(jeans_sizes, [0] * len(jeans_sizes)))
            elif standard in ['UK', 'AU']:
                template_qty = dict(zip(uk_sizes, [0] * len(uk_sizes)))
            elif standard == 'OS':
                template_qty = dict(zip(one_size, [0]))
        
        # Check for each size if it exists in template_qty
        for k, v in size_qty.items():
            if k in template_qty:
                template_qty[k] = v  # Update the template with the quantity
            else:
                # If size not found, append the SKU to mismatched list
                mismatched_sizes_skus.append(sku)
                continue
                

        if sku not in mismatched_sizes_skus:
            data.loc[idx, 'Size'] = ','.join([str(x) for x in template_qty.keys()])
            data.loc[idx, 'Qty'] = ','.join([str(x) for x in template_qty.values()])

    print(f"Total mismatched SKUs: {len(mismatched_sizes_skus)}")
    pd.DataFrame({'SKU': mismatched_sizes_skus}).to_csv('private_repo/clean_data/mismatched_skus.csv', index=False)
    data.drop(index=data[data['SKU'].isin(mismatched_sizes_skus)].index, inplace=True)
    return data


def fix_qty(row):
    if row['Qty'] == '0' or row['Qty'] == 0:
        return ','.join(['0' for _ in range(len(row['Size'].split(',')))])
    return row['Qty']


def final_preprocessing():
    data = pd.read_csv('private_repo/clean_data/new_clothes.csv')
    out_of_stock = data[data['Stock Status'] == 'OUT OF STOCK']
    out_of_stock.to_csv('private_repo/clean_data/zero_inventory2.csv')
    
    print('Number of out of stock entries:', len(out_of_stock))
    
    data.drop(index=out_of_stock.index, inplace=True)
    data.to_csv('private_repo/clean_data/new_clothes.csv')
    
    main()
    
    data = additional_preprocessing()
    all_skus = pd.read_csv('private_repo/clean_data/all_skus.csv')
    
    to_add = data[~data['SKU'].isin(all_skus['SKU'])]
    to_add.to_csv('private_repo/clean_data/to_create.csv', index=False)
    
    
    new = data[data['SKU'].isin(all_skus['SKU'])]
    old  = pd.read_csv('private_repo/clean_data/old_clothes_cleaned.csv')
    
    merged_data = pd.merge(old[['SKU', 'Qty']], new[['SKU', 'Qty']], on='SKU', suffixes=('_old', '_new'))
    diff_qty = merged_data[merged_data['Qty_old'] != merged_data['Qty_new']]
    
    new2 = new[new['SKU'].isin(diff_qty['SKU'])]
    new2.to_csv('private_repo/clean_data/to_update.csv', index=False)
    
    # update all skus to add the products that will be added
    all_skus = pd.concat([all_skus['SKU'], to_add['SKU']], ignore_index=True)
    all_skus.to_csv('private_repo/clean_data/all_skus.csv', index=False)
    
    # get the zero inventory data
    zero_inventory = all_skus[~all_skus.isin(data['SKU'])]
    zero_inventory.to_csv('private_repo/clean_data/zero_inventory.csv', index=False)
    
    data.to_csv('private_repo/clean_data/old_clothes_cleaned.csv', index=False)
    data.to_csv('private_repo/clean_data/new_clothes_cleaned.csv', index=False)
    