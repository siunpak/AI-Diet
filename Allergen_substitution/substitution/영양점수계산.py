import pandas as pd

# 영양점수 계산

def check_nutrient_range(value, lower, upper):
    """각 영양소별 데이터가 범위 안에 놓이는지 확인"""
    return lower <= value <= upper

def nutrient_standards(age, gender):
    """영양소 기준치 반환"""
    
    if age == '3to5':
        nutrient_standards = {
            'Energy': (1260, 1540),
            'Protein': (18.75, float('inf')),
            'Total Dietary': (10, float('inf')),
            'Calcium': (450, 2500),
            'Iron': (5.25, 40),
            'Sodium': (0, 1600),
            'Vitamin A': (225, 510),
            'Vitamin B1 (Thiamine)': (0.375, float('inf')),
            'Vitamin B2 (Rivoflavin)': (0.45, float('inf')),
            'Vitamin C': (33.75, 510),
            'Linoleic Acid': (5250, float('inf')),
            'Alpha-Linolenic Acid': (675, float('inf'))
        }
    
    elif age == '6to8':
        if gender == 'boy': #68_boy
            nutrient_standards = {
                'Energy': (1530, 1870),
                'Protein': (26.25, float('inf')),
                'Total Dietary': (13, float('inf')),
                'Calcium': (525, 2500),
                'Iron': (6.75, 40),
                'Sodium': (0, 1900),
                'Vitamin A': (337.5, 1100),
                'Vitamin B1 (Thiamine)': (0.525, float('inf')),
                'Vitamin B2 (Rivoflavin)': (0.675, float('inf')),
                'Vitamin C': (37.5, 750),
                'Linoleic Acid': (6750, float('inf')),
                'Alpha-Linolenic Acid': (825, float('inf'))
            }
        else: #68_girl
            nutrient_standards = {
                'Energy': (1350, 1650),
                'Protein': (26.25, float('inf')),
                'Total Dietary': (13, float('inf')),
                'Calcium': (525, 2500),
                'Iron': (6.75, 40),
                'Sodium': (0, 1900),
                'Vitamin A': (300, 1100),
                'Vitamin B1 (Thiamine)': (0.525, float('inf')),
                'Vitamin B2 (Rivoflavin)': (0.6, float('inf')),
                'Vitamin C': (37.5, 750),
                'Linoleic Acid': (5250, float('inf')),
                'Alpha-Linolenic Acid': (600, float('inf'))
            }
    elif age == '9to12':
        if gender == 'boy': #912_boy
            nutrient_standards = {
                'Energy': (1800, 2200),
                'Protein': (37.5, float('inf')),
                'Total Dietary': (16, float('inf')),
                'Calcium': (600, 3000),
                'Iron': (8.25, 40),
                'Sodium': (0, 2300),
                'Vitamin A': (450, 1600),
                'Vitamin B1 (Thiamine)': (0.675, float('inf')),
                'Vitamin B2 (Rivoflavin)': (0.825, float('inf')),
                'Vitamin C': (52.5, 1100),
                'Linoleic Acid': (7125, float('inf')),
                'Alpha-Linolenic Acid': (975, float('inf'))
            }
        else: #912_girl
            nutrient_standards = {
                'Energy': (1620, 1980),
                'Protein': (33.75, float('inf')),
                'Total Dietary': (16, float('inf')),
                'Calcium': (600, 3000),
                'Iron': (7.5, 40),
                'Sodium': (0, 2300),
                'Vitamin A': (412.5, 1600),
                'Vitamin B1 (Thiamine)': (0.675, float('inf')),
                'Vitamin B2 (Rivoflavin)': (0.75, float('inf')),
                'Vitamin C': (52.5, 1100),
                'Linoleic Acid': (6750, float('inf')),
                'Alpha-Linolenic Acid': (825, float('inf'))
            }
    return nutrient_standards


def calculate_nutrition(db, df, age, gender):
    '''나이/성별 기준에 따른 영양점수 계산'''
    nutrient_categories = [
        'Energy', 'Protein', 'Fat', 'Carbohydrate', 'Total Dietary', 'Calcium',
        'Iron', 'Sodium', 'Vitamin A', 'Vitamin B1 (Thiamine)',
        'Vitamin B2 (Rivoflavin)', 'Vitamin C', 'Linoleic Acid',
        'Alpha-Linolenic Acid'
    ]
    nut_standard = nutrient_standards(age, gender)
    total_sum = pd.DataFrame()
    
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
        for nutrient, (lower, upper) in {**nut_standard, **ratio_standards}.items():
            is_in_range = check_nutrient_range(nutrient_values[nutrient], lower, upper)
            nutrient_values[f"{nutrient}_"] = is_in_range
            count += is_in_range
        
        nutrient_values['Total_sum'] = count
        total_sum = total_sum.append(pd.DataFrame([nutrient_values], columns=nutrient_values.keys()))
        
    return total_sum.reset_index(drop=True)