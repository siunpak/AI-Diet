import numpy as np
import pandas as pd
import os
from tqdm import tqdm
import time
import warnings
warnings.filterwarnings('ignore')

## load ingredient and nutrient data


def get_data(ages, gender, light_breakfast):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    ingre_allergy = pd.read_csv(os.path.join(current_directory, 'data2(allergy-related)/식재료_알레르기표기(업데이트).csv'), encoding = 'cp949').drop(columns = ['기타'], axis = 1)
    ingre_allergy.rename(columns = {'Unnamed: 0': 'name'}, inplace = True)
    
    if ages == '3to5':
        nutri = pd.read_csv(os.path.join(current_directory, 'data1(menu-related)/updated_nutrition_db(3~5)_계절,알러지포함.csv'), encoding = 'cp949', index_col=False)
        
        if light_breakfast == '아침간편식':
            embedding = pd.read_csv(os.path.join(current_directory,'data1(menu-related)/diet35_morning_final_embedding.csv'), encoding = 'cp949', index_col = 0).fillna(0)
            meal = pd.read_excel(os.path.join(current_directory,'data2(allergy-related)/3~5세,0116생성,간편식_buffer60_change20_epoch=30000_lr=0.0005_beta14_syn15.xlsx'), index_col = 0).reset_index(drop = True).iloc[:,:-1]
            
        else:
            embedding = pd.read_csv(os.path.join(current_directory,'data1(menu-related)/diet35_final_embedding.csv'), encoding = 'cp949', index_col = 0).fillna(0)
            meal = pd.read_excel(os.path.join(current_directory,'data2(allergy-related)/3~5세,0116생성,일반식_buffer60_change20_epoch=30000_lr=0.0005_beta14_syn15.xlsx'), index_col = 0).reset_index(drop = True).iloc[:,:-1]
    
    elif ages == '6to8':
        #ingre = pd.read_csv(os.path.join(current_directory, 'data1(menu-related)/ingredient_db(6~8)_전체.csv'), encoding = 'utf-8').drop(columns = '음식명_2')
        nutri = pd.read_excel(os.path.join(current_directory,'data1(menu-related)/updated_nutrition_db(6~8)_label_updated_23.12.20.xlsx'), index_col = 0)
        #ingre.rename(columns = {'음식명_1': 'name', '식재료': 'ingredient', '중량': 'weight'}, inplace = True)
        #ingre['name'].ffill(inplace=True)

        #menu_ing_nut_df = pd.read_csv(os.path.join(current_directory,'data1(menu-related)/ver2_menu_ing_nut_6to8(이름변경X).csv'), encoding='cp949').set_index('Unnamed: 0').loc[:,:'짜장 소스, 레토르트']
        
        if light_breakfast == '아침간편식':
            embedding = pd.read_csv(os.path.join(current_directory,'data1(menu-related)/diet68_morning_final_embedding.csv'), encoding = 'cp949', index_col = 0).fillna(0)
            
            if gender == 'boy':
                meal = pd.read_excel(os.path.join(current_directory,'data2(allergy-related)/6~8세, 남, 간편식_buffer60_epoch=30000_lr=0.0005_synthetic허용.xlsx'), index_col = 0).reset_index(drop = True).iloc[:,:-1]
            
            else:
                meal = pd.read_excel(os.path.join(current_directory,'data2(allergy-related)/6~8세, 여, 간편식_buffer60_epoch=30000_lr=0.0005_synthetic허용.xlsx'), index_col = 0).reset_index(drop = True).iloc[:,:-1]
        
        else:
            embedding = pd.read_csv(os.path.join(current_directory,'data1(menu-related)/diet68_final_embedding.csv'), encoding = 'cp949', index_col = 0).fillna(0)
            
            if gender == 'boy':
                meal = pd.read_excel(os.path.join(current_directory,'data2(allergy-related)/6~8세, 남, 일반식_buffer60_epoch=30000_lr=0.0005_synthetic허용.xlsx'), index_col = 0).reset_index(drop = True).iloc[:,:-1]
            
            else:
                meal = pd.read_excel(os.path.join(current_directory,'data2(allergy-related)/6~8세, 여, 일반식_buffer60_epoch=30000_lr=0.0005_synthetic허용.xlsx'), index_col = 0).reset_index(drop = True).iloc[:,:-1]
        nutri.reset_index(names='name', inplace=True)

    elif ages == '9to12':
        #ingre = pd.read_csv(os.path.join(current_directory,'data1(menu-related)/ingredient_db(9~12)_전체.csv'), encoding = 'utf-8').drop(columns = ['음식명_2', '식품군 분류', '식품군별번호'],axis = 1)
        nutri = pd.read_excel(os.path.join(current_directory,'data1(menu-related)/updated_nutrition_db(9~12)_label_updated_23.12.20.xlsx'), index_col = 0)
        #ingre.rename(columns = {'음식명_1': 'name', '식재료': 'ingredient', '중량': 'weight'}, inplace = True)
        #ingre['name'].ffill(inplace=True)

        #menu_ing_nut_df = pd.read_csv(os.path.join(current_directory,'data1(menu-related)/ver2_menu_ing_nut_9to12(이름변경X).csv'), encoding='cp949').set_index('Unnamed: 0').loc[:,:'짜장 소스, 레토르트']
        
        if light_breakfast == '아침간편식':
            embedding = pd.read_csv(os.path.join(current_directory,'data1(menu-related)/diet912_morning_final_embedding.csv'), encoding = 'cp949', index_col = 0).fillna(0)
            
            if gender == 'boy':
                meal = pd.read_excel(os.path.join(current_directory,'data2(allergy-related)/9~12세, 남, 간편식_buffer60_epoch=30000_lr=0.0005_synthetic허용.xlsx'), index_col = 0).reset_index(drop = True).iloc[:,:-1]
            
            else:
                meal = pd.read_excel(os.path.join(current_directory,'data2(allergy-related)/9~12세, 여, 간편식_buffer60_epoch=30000_lr=0.0005_synthetic허용.xlsx'), index_col = 0).reset_index(drop = True).iloc[:,:-1]
        
        else:
            embedding = pd.read_csv(os.path.join(current_directory,'data1(menu-related)/diet912_final_embedding.csv'), encoding = 'cp949', index_col = 0).fillna(0)
            
            if gender == 'boy':
                meal = pd.read_excel(os.path.join(current_directory,'data2(allergy-related)/9~12세, 남, 일반식_buffer60_epoch=30000_lr=0.0005_synthetic허용.xlsx'), index_col = 0).reset_index(drop = True).iloc[:,:-1]
            
            else:
                meal = pd.read_excel(os.path.join(current_directory,'data2(allergy-related)/9~12세, 여, 일반식_buffer60_epoch=30000_lr=0.0005_synthetic허용.xlsx'), index_col = 0).reset_index(drop = True).iloc[:,:-1]
        nutri.reset_index(names='name', inplace=True)
    embedding.reset_index(names='name', inplace=True)
    return nutri, meal, embedding, ingre_allergy