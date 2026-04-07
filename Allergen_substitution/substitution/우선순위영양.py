import pandas as pd

# 영양점수 계산

def check_nutrient_range(value, lower, upper=float('inf')):
    """각 영양소별 데이터가 범위 안에 놓이는지 확인"""
    return lower <= value <= upper

def nutrient_standards(age, gender):
    """영양소 기준치 반환"""
    if age == '6to8':
        if gender == 'boy': #68_boy
            nutrient_standards = {
                'Energy': (1530, 1870),
                'Protein': (26.25,),
                'Total Dietary': (13,),
                'Vitamin A': (337.5,),
                'Vitamin B1 (Thiamine)': (0.525,),
                'Vitamin B2 (Rivoflavin)': (0.675,),
                'Vitamin C': (37.5,),
                'Calcium': (525,),
                'Iron': (6.75,),
                'Sodium': (0, 1900)
            }
        else: #68_girl
            nutrient_standards = {
                'Energy': (1350, 1650),
                'Protein': (26.25,),
                'Total Dietary': (13,),
                'Vitamin A': (300,),
                'Vitamin B1 (Thiamine)': (0.525,),
                'Vitamin B2 (Rivoflavin)': (0.6,),
                'Vitamin C': (37.5,),
                'Calcium': (525,),
                'Iron': (6.75,),
                'Sodium': (0, 1900)
            }
    elif age == '9to12':
        if gender == 'boy': #912_boy
            nutrient_standards = {
                'Energy': (1800, 2200),
                'Protein': (37.5,),
                'Total Dietary': (16,),
                'Vitamin A': (450,),
                'Vitamin B1 (Thiamine)': (0.675,),
                'Vitamin B2 (Rivoflavin)': (0.825,),
                'Vitamin C': (52.5,),
                'Calcium': (600,),
                'Iron': (8.25,),
                'Sodium': (0, 2300)
            }
        else: #912_girl
            nutrient_standards = {
                'Energy': (1620, 1980),
                'Protein': (33.75,),
                'Total Dietary': (16,),
                'Vitamin A': (412.5,),
                'Vitamin B1 (Thiamine)': (0.675,),
                'Vitamin B2 (Rivoflavin)': (0.75,),
                'Vitamin C': (52.5,),
                'Calcium': (600,),
                'Iron': (7.5,),
                'Sodium': (0, 2300)
            }
    return nutrient_standards

def calculate_nutrition_for_group(db, df, age, gender):
    nutrient_categories = [
        'Energy', 'Protein', 'Fat', 'Carbohydrate', 'Total Dietary', 'Calcium',
        'Iron', 'Sodium', 'Vitamin A', 'Vitamin B1 (Thiamine)',
        'Vitamin B2 (Rivoflavin)', 'Vitamin C', 'Linoleic Acid',
        'Alpha-Linolenic Acid'
    ]
    
    total_sum = pd.DataFrame()
    nut_standard = nutrient_standards(age, gender)
    for index in df.index:
        menu_sum = pd.DataFrame(columns=nutrient_categories)
        
        for col in df.columns:
            menu_item = db[db.name == df[col][index]]
            menu_sum = menu_sum.append(menu_item[nutrient_categories].iloc[0])
        
        menu_sum = menu_sum.sum(axis=0)
        
        carb_ratio = menu_sum['Carbohydrate'] * 4 / menu_sum['Energy']
        protein_ratio = menu_sum['Protein'] * 4 / menu_sum['Energy']
        fat_ratio = menu_sum['Fat'] * 9 / menu_sum['Energy']
        
        ratio_standards = {
            'Carbohydrate_ratio': (0.55, 0.65),
            'Protein_ratio': (0.07, 0.20),
            'Fat_ratio': (0.15, 0.30)
        }
        
        nutrient_values = {**menu_sum, 'Carbohydrate_ratio': carb_ratio, 'Protein_ratio': protein_ratio, 'Fat_ratio': fat_ratio}
        
        count = 0
        for nutrient, values in {**nut_standard, **ratio_standards}.items():
            lower = values[0]
            upper = values[1] if len(values) > 1 else float('inf')
            is_in_range = check_nutrient_range(nutrient_values[nutrient], lower, upper)
            nutrient_values[f"{nutrient}_"] = is_in_range
            count += is_in_range
        
        nutrient_values['Total_sum'] = count
        total_sum = total_sum.append(pd.DataFrame([nutrient_values], columns=nutrient_values.keys()))
        
    return total_sum.reset_index(drop=True)