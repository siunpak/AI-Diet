from .data import get_data
from .우선순위영양 import calculate_nutrition_for_group
from .영양점수계산 import calculate_nutrition

import numpy as np
import pandas as pd
import os
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')
import random

class Inspect_allergy_food:
    def __init__(self, age, gender, light_breakfast, allergy_list, season_info):
        self.age = age
        self.gender = gender
        self.light_breakfast=light_breakfast
        self.allergy_list = allergy_list
        self.season_info = season_info
        self.calculate_nutrition_score = calculate_nutrition
        self.prior_nutrition_score = calculate_nutrition_for_group
        #self.menu_ing_nut_df = get_data(age, gender, light_breakfast)[0]
        self.nutri_df = get_data(age, gender, light_breakfast)[0].drop_duplicates('name')
        self.embedding = get_data(age, gender, light_breakfast)[2]
        self.ingre_allergy = get_data(age, gender, light_breakfast)[3].columns[1:]
        self.total_menus_allergy = self.menus_allergy()
        #self.diets = get_data(age, gender, light_breakfast)[1]
        self.data_slicing()
        self.emb = cosine_similarity(self.embedding, self.embedding) 
    
    def data_slicing(self):
        self.cat_df = self.embedding[['name', 'vegitable_soup', 'nonvegitable_soup', 'morning_soup_comb1', 'morning_soup_comb2', 'morning_soup_comb3']]
        self.cat_df_special = self.embedding[['name', 'special_soup_needed', 'special_soup_notneeded', 'possible_with_special', 'empty', 'soup']]
        self.embedding = self.embedding[['name','0_x', '1_x', '2_x', '3_x', '4_x', '5_x', '6_x', '7_x', '8_x', '9_x', '10_x', '11_x', '12_x', '13_x', '14_x', '15_x', '16_x', '17_x', '18_x', '19_x', '20_x', '21_x', '22_x', '23_x', '24_x', '25_x', '26_x', '27_x', '28_x', '29_x', '30_x', '31_x', '0_y', '1_y', '2_y', '3_y', '4_y', '5_y', '6_y', '7_y', '8_y', '9_y', '10_y', '11_y', '12_y', '13_y', '14_y', '15_y', '16_y', '17_y', '18_y', '19_y', '20_y', '21_y', '22_y', '23_y', '24_y', '25_y', '26_y', '27_y', '28_y', '29_y', '30_y', '31_y']]
        self.embedding.set_index('name', inplace=True)
        self.cat_df_for_vegi_soup = self.nutri_df[['name', 'vegitable_soup', 'nonvegitable_soup', 'morning_soup_comb1', 'morning_soup_comb2', 'morning_soup_comb3']]
        self.cat_df_for_special_soup = self.nutri_df[['name', 'special_soup_needed', 'special_soup_notneeded', 'possible_with_special', 'empty']]
        self.special_food_list = list(self.nutri_df[self.nutri_df.special == 1].name)
        self.wrong_cat_df = self.nutri_df[['name', 'snack1', 'snack2', 'snack3', 'snack4', 'rice', 'soup', 'side_dish1', 'side_dish2', 'breakfast1', 'breakfast2', 'breakfast3', 'kimchi', 'special', 'empty']]

    '''
    nutri 데이터 내에 메뉴별 알러지가 정리되어 있음
    nutri 데이터 포함 내용
     - 이름
     - weight
     - 영양소 15종 정보
     - 식단 시퀀스 위치 정보
     - 알레르기 정보
     - 계절 정보
    '''
    def menus_allergy(self):
        total_menus_allergy = {}
        for i in self.ingre_allergy:
            total_menus_allergy[i] = list(self.nutri_df[self.nutri_df[i] == 1].name)

        return total_menus_allergy

    def get_allergy_food(self):
        # subject마다 알레르기 포함 식품들 모두 정리
        allergy_foods = []
        for allergies in self.allergy_list:
            allergy_food = self.total_menus_allergy[allergies]
            allergy_foods = allergy_foods + allergy_food
        return allergy_foods
    
    def get_season_food(self):
        
        if self.season_info == '없음':
            seasons = []
            season_foods = []
            
        else: 
            seasons = [self.season_info , '연중']
            season_foods = list(self.nutri_df[(self.nutri_df[seasons[0]] == 1) | (self.nutri_df[seasons[1]] == 1)])
    
        return season_foods
    
    # 새롭게 추가된 조건
    '''
    간편식: 아침1-아침2-아침3-간식1-간식2-밥-국-반찬1-반찬2-김치-간식3-간식4-밥-국-반찬1-반찬2-김치
    일반식:  밥 -  국 -반찬2-간식1-간식2-밥-국-반찬1-반찬2-김치-간식3-간식4-밥-국-반찬1-반찬2-김치
           0  -  1 -  2 -  3 - 4  -5- 6- 7  - 8 - 9 - 10 - 11 -12-13- 14- 15 - 16
    '''
    
    # Refactoring 완료
    def wrong_place_food(self, j, food, light_breakfast):
        if food == '종료':
            return True  # 종료가 등장한 경우 잘못된 위치로 간주

        # 해당 음식이 있는 행 찾기
        food_row = self.wrong_cat_df[self.wrong_cat_df.name == food]
        if food_row.empty:
            return True  # 음식이 목록에 없으면 잘못된 위치로 간주
        
        food_cat = self.wrong_cat_df.columns[food_row.iloc[0] == 1][0]

        # 아침간편식 여부에 따라 검사 조건을 달리 함
        if light_breakfast == '아침간편식':
            condition_map = {
                0: 'breakfast1', 1: 'breakfast2', 2: 'breakfast3',
                3: 'snack1', 4: 'snack2', 5: 'rice', 6: 'soup',
                7: 'side_dish1', 8: 'side_dish2', 9: 'kimchi',
                10: 'snack3', 11: 'snack4', 12: 'rice', 13: 'soup',
                14: 'side_dish1', 15: 'side_dish2', 16: 'kimchi'
            }
        else:
            condition_map = {
                0: 'rice', 1: 'soup', 2: 'side_dish1',
                3: 'snack1', 4: 'snack2', 5: 'rice', 6: 'soup',
                7: 'side_dish1', 8: 'side_dish2', 9: 'kimchi',
                10: 'snack3', 11: 'snack4', 12: 'rice', 13: 'soup',
                14: 'side_dish1', 15: 'side_dish2', 16: 'kimchi'
            }

        # j 인덱스에 해당하는 카테고리와 음식의 카테고리가 일치하는지 확인
        return condition_map.get(j, None) != food_cat

    # need_change_food 함수를 is_invalid_morning_com함수와 is_invalid_special_com함수로 분리
    def need_change_food(self, diets, light_breakfast):
        # subject마다 식단 내에서 바꿔야하는 식품 모두 정리
        # {'subject1': {'diet_idx1': [알레르기식품1, 알레르기식품2,...]},
        #              {'diet_idx2': [알레르기식품1, ...]},
        #                   ...
        # {'subject2': {'diet_idx1': [알레르기식품1, 알레르기식품2,...]},
        #              {'diet_idx2': [알레르기식품1, 알레르기식품2, 알레르기식품3, ...]},
        #  ...
        #  }
        allergy_foods = self.get_allergy_food()
        #season_foods = self.get_season_food()
        change_foods_per_diet = {}
        change_foods_idx_diet = {}

        for i, diet in diets.iterrows():
            change_foods, change_foods_idx = [], []

            for j, food in enumerate(diet):
                if food in allergy_foods or self.wrong_place_food(j, food, self.light_breakfast):
                    change_foods.append(food)
                    change_foods_idx.append(j)
                    continue

                if light_breakfast == '아침일반식' and j == 1:
                    if self.is_invalid_morning_com(food, diet[j + 1]):
                        change_foods.append(food)
                        change_foods_idx.append(j)
                        continue

                if food in self.special_food_list:
                    if self.is_invalid_special_com(food, diet[j + 1]):
                        change_foods.append(food)
                        change_foods_idx.append(j)

            change_foods_per_diet[i] = change_foods
            change_foods_idx_diet[i] = change_foods_idx

        return change_foods_per_diet, change_foods_idx_diet

    # is_invalid_morning_com: 아침 국 조합 이상한 경우 확인하는 함수
    def is_invalid_morning_com(self, soup, dish):
        soup_cat = self.cat_df.columns[self.cat_df[self.cat_df.name == soup].iloc[0] == 1].tolist()
        dish_cat = self.cat_df.columns[self.cat_df[self.cat_df.name == dish].iloc[0] == 1].tolist()

        if soup_cat[0] == 'vegitable_soup':
            return dish_cat[0] not in ['morning_soup_comb1', 'morning_soup_comb3']
        elif soup_cat[0] == 'nonvegitable_soup':
            return dish_cat[0] != 'morning_soup_comb2'
        return False

    # is_invalid_special_com: 일품 조합 이상한 경우 확인하는 함수
    def is_invalid_special_com(self, special, soup):
        special_cat = self.cat_df_special.columns[self.cat_df_special[self.cat_df_special.name == special].iloc[0] == 1].tolist()
        soup_cat = self.cat_df_special.columns[self.cat_df_special[self.cat_df_special.name == soup].iloc[0] == 1].tolist()

        if special_cat[0] == 'special_soup_needed':
            return soup_cat[0] != 'possible_with_special'
        elif special_cat[0] == 'special_soup_notneeded':
            return soup_cat[0] != 'empty'
        return False

### Allergy 대체

class Replace_allergy_food(Inspect_allergy_food):
    def __init__(self, age, gender, light_breakfast, allergy_list, season_info):
        super().__init__(age, gender, light_breakfast, allergy_list, season_info)
        self.get_allergy_foods = self.get_allergy_food()
        self.get_season_foods = self.get_season_food()
        self.light_breakfast = light_breakfast

        #####################
        # params
        # roop 횟수 : max_append
        # 식단 1개당 출력 횟수 : outputs
        #####################
        self.max_append = 30
        self.outputs = 5
        
        if self.light_breakfast == '아침간편식':
            self.non_include_idx = [5,12]
                                    
        elif self.light_breakfast == '아침일반식':
            self.non_include_idx = [0,5,12]
        
    def createFolder(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    '''
    3~5세 columns -> 데이터마다 column 통일할 필요가 있음
    'name', 'snack1', 'snack2', 'snack3', 'snack4', 
    'rice', 'soup', 'side_dish1', 'side_dish2', 'breakfast1', 'breakfast2', 
    'breakfast3', 'kimchi', 'special', 'empty'
    '''
    
    # Refactoring 완료
    @staticmethod
    def food_cat(j, light_breakfast):
        '''
        음식의 위치를 잡아주는 함수
        '''
        category_mapping = {
            '아침간편식': {
                0: ['breakfast1'], 1: ['breakfast2'], 2: ['breakfast3'],
                3: ['snack1'], 4: ['snack2'], 5: ['rice', 'special'],
                6: ['soup'], 7: ['side_dish1'], 8: ['side_dish2'],
                9: ['kimchi'], 10: ['snack3'], 11: ['snack4'],
                12: ['rice'], 13: ['soup'], 14: ['side_dish1'],
                15: ['side_dish2'], 16: ['kimchi']
            },
            '아침일반식': {
                0: ['rice'], 1: ['soup'], 2: ['side_dish1', 'side_dish2'],
                3: ['snack1'], 4: ['snack2'], 5: ['rice', 'special'],
                6: ['soup'], 7: ['side_dish1'], 8: ['side_dish2'],
                9: ['kimchi'], 10: ['snack3'], 11: ['snack4'],
                12: ['rice'], 13: ['soup'], 14: ['side_dish1'],
                15: ['side_dish2'], 16: ['kimchi']
            }
        }

        return category_mapping.get(light_breakfast, {}).get(j, ['empty'])

    #@staticmethod
    #def food_cat(j, light_breakfast):
    #    '''
    #    음식의 위치를 잡아주는 함수
    #    '''
    #    food_cat = ['empty']
    #    if light_breakfast == '아침간편식':
    #        if (j == 5):
    #            food_cat = ['rice', 'special']
    #        elif (j == 12):
    #            food_cat = ['rice']
    #        elif (j == 0):
    #            food_cat = ['breakfast1']
    #        elif (j == 1):
    #            food_cat = ['breakfast2']
    #        elif (j == 2):
    #            food_cat = ['breakfast3']
    #        elif (j == 3):
    #            food_cat = ['snack1']
    #        elif (j == 4):
    #            food_cat = ['snack2']
    #        elif (j == 6) or (j == 13):
    #            food_cat = ['soup']
    #        elif (j == 7) or (j == 14):
    #            food_cat = ['side_dish1']
    #        elif (j == 8) or (j == 15):
    #            food_cat = ['side_dish2']
    #        elif (j == 9) or (j == 16) :
    #            food_cat = ['kimchi']
    #        elif (j == 10):
    #            food_cat = ['snack3']
    #        elif (j == 11) :
    #            food_cat = ['snack4']
    #            
    #    elif light_breakfast == '아침일반식':
    #        if (j == 0) or (j == 12):
    #            food_cat = ['rice']
    #        elif (j == 5):
    #            food_cat = ['rice', 'special']
    #        elif (j == 3):
    #            food_cat = ['snack1']
    #        elif (j == 4):
    #            food_cat = ['snack2']
    #        elif (j == 1) or (j == 6) or (j == 13):
    #            food_cat = ['soup']
    #        elif (j == 7) or (j == 14):
    #            food_cat = ['side_dish1']
    #        elif (j == 8) or (j == 15):
    #            food_cat = ['side_dish2']
    #        elif (j == 2):
    #            food_cat = ['side_dish1', 'side_dish2']
    #        elif (j == 9) or (j == 16) :
    #            food_cat = ['kimchi']
    #        elif (j == 10):
    #            food_cat = ['snack3']
    #        elif (j == 11) :
    #            food_cat = ['snack4']
    #            
    #    return food_cat
    
    # food_candi 처리용 함수 : allergy free menu에 없는 menu name 반환
    def is_allergy_free(self, menu_name):
        return menu_name not in self.get_allergy_foods
    
    def is_season_free(self, menu_name):
        return menu_name in self.get_season_foods
    

    # food_candi 처리용 함수 2 : matching 여부 확인
    def has_matching_category(self, menu_name, food_cat):
        filtered_df = self.wrong_cat_df[self.wrong_cat_df.name == menu_name]
        if filtered_df.empty:
            return False
        first_row = filtered_df.iloc[0]
        columns_with_value_one = self.wrong_cat_df.columns[first_row == 1].tolist()
        return food_cat[0] in columns_with_value_one
        
        
    def food_candi(self, food, food_idx):
        # allergy-free하면서 category 동일한 후보군 추출
        food_cat = self.food_cat(food_idx, self.light_breakfast)
        if (food == '종료') or (food == 'empty'):
            sim_menu_list = random.sample(list(self.wrong_cat_df[self.wrong_cat_df[food_cat[0]] == 1]['name']), len(list(self.wrong_cat_df[self.wrong_cat_df[food_cat[0]] == 1]['name'])))
            allergy_free_menus = [sim_m for sim_m in sim_menu_list if (sim_m not in self.get_allergy_foods)][:20]
            
        else:
            #old_food_cat = cat_df.columns[cat_df[cat_df.name == food].iloc[0]==1].tolist()
            menu_idx = list(self.embedding.index).index(food)
            sim_scores = list(enumerate(self.emb[menu_idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse= True)
            menu_indices = [idx[0] for idx in sim_scores]
            sim_menu_list = self.embedding.index[menu_indices][1:].to_list()
            
            # 기존 코드
            #if old_food_cat == food_cat:
            #    
            #    print(old_food_cat)
            #    print(len(sim_menu_list))
            #    print(sim_menu_list[0] not in self.get_allergy_foods)
            #    print(cat_df.columns[cat_df[cat_df.name == sim_menu_list[0]].iloc[0] == 1])
            #  
            #    allergy_free_menus = [sim_m for sim_m in sim_menu_list if (sim_m not in self.get_allergy_foods) and (cat_df.columns[cat_df[cat_df.name == sim_m].iloc[0]==1].tolist()==old_food_cat)][:20]
            #    
            #else:
            #    allergy_free_menus = [sim_m for sim_m in sim_menu_list if (sim_m not in self.get_allergy_foods) and (cat_df.columns[cat_df[cat_df.name == sim_m].iloc[0]==1].tolist()==food_cat)][:20]
            #allergy_free_menus = [sim_m for sim_m in sim_menu_list if (sim_m not in self.get_allergy_foods) and (cat_df.columns[cat_df[cat_df.name == sim_m].iloc[0]==1].tolist()==food_cat)][:20]
            
            # 변경
            allergy_free_menus = []
            for sim_m in sim_menu_list:
                if self.is_allergy_free(sim_m) and self.has_matching_category(sim_m, food_cat):
                # season 반영 이후 적용
                #if self.is_allergy_free(sim_m) and self.has_matching_category(sim_m, food_cat) and self.is_season_free(sim_m):
                    allergy_free_menus.append(sim_m)
                    if len(allergy_free_menus) >= 20:
                        break
        return allergy_free_menus
    
    '''
    1. Allergy-free
    2. 식단 내 위치
    3. 계절식 여부 
    를 만족한 후보군 식품 
    '''
    
    ## 아침 간편식:

    ## 아침 간편식 위치: 0,1,2
    ## 밥 위치: 5, 12
    ## 국 위치: 6, 13
    ## 주찬 위치: 7, 14
    ## 부찬 위치: 8, 15
    ## 김치 위치: 9,16
    ## 주간식 위치: 10
    ## 간식2 위치: 11
    ## 간식3 위치: 3,4


    ## 아침 일반식:
    ## 밥 위치: 0, 5, 12
    ## 국 위치: 1, 6, 13
    ## 주찬 위치: 7, 14
    ## 부찬 위치: 2, 8, 15
    ## 김치 위치: 9,16
    ## 주간식 위치: 10
    ## 간식2 위치: 11
    ## 간식3 위치: 3,4

    @staticmethod
    def mispos_cal(db:pd.DataFrame, df, light_breakfast):
        '''
        mispositioning 비율을 계산하는 함수
        '''
        mispos = []

        for i in range(len(df)):
            total_mis = 0
            temp_diet = df.iloc[i]
            
            
            if light_breakfast == '아침간편식':

                # 아침간편식
                if db[db.name == temp_diet[1]].breakfast1.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[2]].breakfast2.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[3]].breakfast3.values[0] == 0:
                    total_mis += 1
                
                # 밥
                if db[db.name == temp_diet[6]].rice.values[0] == 0 and db[db.name == temp_diet[6]].special.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[13]].rice.values[0] == 0 and db[db.name == temp_diet[13]].special.values[0] == 0 == 0:
                    total_mis += 1   

                # 국
                if db[db.name == temp_diet[7]].soup.values[0] == 0:
                    total_mis += 1

                if db[db.name == temp_diet[14]].soup.values[0] == 0:
                    total_mis += 1
                    
                # 주찬
                if db[db.name == temp_diet[8]].side_dish1.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[15]].side_dish1.values[0] == 0:
                    total_mis += 1    
                    
                # 부찬
                if db[db.name == temp_diet[9]].side_dish2.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[16]].side_dish2.values[0] == 0:
                    total_mis += 1
    
                    
                # 김치
                if db[db.name == temp_diet[10]].kimchi.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[17]].kimchi.values[0] == 0:
                    total_mis += 1
    
                    
                # 간식1
                if db[db.name == temp_diet[11]].snack3.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[12]].snack4.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[4]].snack1.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[5]].snack2.values[0] == 0:
                    total_mis += 1
                mispos.append(total_mis)
                
            else:
                # 밥
                if db[db.name == temp_diet[1]].rice.values[0] == 0 and db[db.name == temp_diet[1]].special.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[6]].rice.values[0] == 0 and db[db.name == temp_diet[6]].special.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[13]].rice.values[0] == 0 and db[db.name == temp_diet[13]].special.values[0] == 0:
                    total_mis += 1
                    
                # 국
                if db[db.name == temp_diet[2]].soup.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[7]].soup.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[14]].soup.values[0] == 0:
                    total_mis += 1
                    
                # 주찬

                if db[db.name == temp_diet[8]].side_dish1.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[15]].side_dish1.values[0] == 0:
                    total_mis += 1
                    
                # 부찬
                if db[db.name == temp_diet[3]].side_dish1.values[0] == 0 and db[db.name == temp_diet[3]].side_dish2.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[9]].side_dish2.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[16]].side_dish2.values[0] == 0:
                    total_mis += 1
                    
                # 김치
                if db[db.name == temp_diet[10]].kimchi.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[17]].kimchi.values[0] == 0:
                    total_mis += 1
                    
                # 간식1
                if db[db.name == temp_diet[11]].snack3.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[12]].snack4.values[0] == 0:
                    total_mis += 1 
                if db[db.name == temp_diet[4]].snack1.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[5]].snack2.values[0] == 0:
                    total_mis += 1 
                mispos.append(total_mis)
        
        return mispos

    ### Allergy 비율 점수
    @staticmethod
    def allergy_scores(df, allergy_food):
        allergy_score = []
        for i in range(len(df)):
            allergy_count = 0
            temp_diet = df.iloc[i]
            
            for j in range(len(temp_diet)):
                if temp_diet[j+1] in allergy_food:
                    allergy_count += 1
                    
            allergy_score.append(allergy_count)
        return allergy_score
    
    
    # cat_df_for_vegi_soup = self.nutri_df[['name', 'vegitable_soup', 'nonvegitable_soup', 'morning_soup_comb1', 'morning_soup_comb2', 'morning_soup_comb3']]
    # cat_df_for_special_soup = self.nutri_df[['name', 'special_soup_needed', 'special_soup_notneeded', 'possible_with_special']]
    #     # food_candi 처리용 함수 3 : vegi soup 여부 확인

    # def is_matching_vegi_soup(self, menu_name, cat_df_for_vegi_soup, food_idx):
    #     filtered_df = cat_df_for_vegi_soup[cat_df_for_vegi_soup.name == menu_name]
    #     if filtered_df.empty:
    #         return False
        
    #     first_row = filtered_df.iloc[0]

    '''
    일반식에서 반찬 조건:
    아침국이 채소국인 경우(vegitable_soup == 1): morning_soup_comb1 또는 morning_soup_comb3
    아침국이 채소국이 아닌 경우(nonvegitable_soup == 1): morning_soup_comb2
    '''
    
    '''
    일품 장국 조건:
    일품 요리가 국이 필요한 경우(special_soup_needed == 1): possible_with_special 국과 함께
    일품 요리가 국이 필요 없는 경우(special_soup_notneeded == 1): empty와 함께
    
    '''
    
    # Refactoring 진행 완료
    # category 가지고 오기
    def get_category(self, df, item_name):
        row = df[df['name'] == item_name]
        if not row.empty:
            return row.columns[row.iloc[0] == 1].tolist()[0]
        return None

    def is_matching_vegi_soup(self, changed_diet):
        soup_name = changed_diet[2][0]
        dish_name = changed_diet[3][0]
        soup_cat, side_cat = None, None

        # DataFrame에서 category 받아오기
        soup_cat = self.get_category(self.cat_df_for_vegi_soup, soup_name)
        side_cat = self.get_category(self.cat_df_for_vegi_soup, dish_name)

        # 수프와 반찬의 매칭 여부를 판단
        if soup_cat == 'vegitable_soup' and side_cat in ['morning_soup_comb3', 'morning_soup_comb1']:
            return True
        elif soup_cat == 'nonvegitable_soup' and side_cat == 'morning_soup_comb2':
            return True

        return False

    #def is_matching_vegi_soup(self, changed_diet):
    #
    #    soup_name = changed_diet[2]
    #    dish_name = changed_diet[3]
    #    filtered_soup = self.cat_df_for_vegi_soup[self.cat_df_for_vegi_soup.name == soup_name]
    #    filtered_dish = self.cat_df_for_vegi_soup[self.cat_df_for_vegi_soup.name == dish_name]
    #    
    #    soup_cat = self.cat_df_for_vegi_soup.columns[filtered_soup.iloc[0] == 1].tolist()
    #    side_cat = self.cat_df_for_vegi_soup.columns[filtered_dish.iloc[0] == 1].tolist()
    #    
    #    if soup_cat[0] == 'vegitable_soup':
    #        if side_cat[0] == 'morning_soup_comb3' or side_cat[0] == 'morning_soup_comb1':
    #            return True
    #        
    #    elif soup_cat[0] == 'nonvegitable_soup':
    #        if side_cat[0] == 'morning_soup_comb2':
    #            return True
    
    # Refacoring 진행 완료
    def is_special_soup(self, changed_diet):
        # special_soup 조건 dict 생성
        special_soup_dict = self.cat_df_for_special_soup.set_index('name').to_dict('index')

        # Check for special soup conditions
        for idx, food in enumerate(changed_diet):
            if special_soup_dict.get(food, {}).get('special', 0) == 1:
                next_food = changed_diet[idx + 1] if idx + 1 < len(changed_diet) else None
                next_next_food = changed_diet[idx + 2] if idx + 2 < len(changed_diet) else None

                special_cat = set(special_soup_dict.get(next_food, {}).keys()) & {'special_soup_needed', 'special_soup_notneeded'}
                soup_cat = set(special_soup_dict.get(next_next_food, {}).keys()) & {'possible_with_special', 'empty'}

                if 'special_soup_needed' in special_cat and 'possible_with_special' not in soup_cat:
                    return False
                elif 'special_soup_notneeded' in special_cat and 'empty' not in soup_cat:
                    return False

        return True
    
    #def is_special_soup(self, changed_diet):
    #    special_food_idx = [idx for idx,i in enumerate(changed_diet) if self.nutri_df[self.nutri_df.name == i].iloc[0]['special']==1]
    #    trues = []
    #    for i in special_food_idx:
    #        
    #        filtered_special = self.cat_df_for_special_soup[self.cat_df_for_special_soup.name == changed_diet[i+1]]
    #        special_cat = self.cat_df_for_special_soup.columns[filtered_special.iloc[0] == 1].tolist()
    #        
    #        filtered_soup = self.cat_df_for_special_soup[self.cat_df_for_special_soup.name == changed_diet[i+2]]
    #        soup_cat = self.cat_df_for_special_soup.columns[filtered_soup.iloc[0] == 1].tolist()
    #        
    #        if special_cat[0] == 'special_soup_needed':
    #            if soup_cat[0] == 'possible_with_special':
    #                trues.append(True)
    #            else:
    #                trues.append(False)
    #            
    #        elif special_cat[0] == 'special_soup_notneeded':
    #            if soup_cat[0] == 'empty':
    #                trues.append(True)
    #            else:
    #                trues.append(False)
    #    
    #    if len(trues) > 1:    
    #        if False in trues:
    #            return False
    #        
    #    else:
    #        return True
    #            
                
    def food_candi_per_person(self, diets):

        diets_df = diets.reset_index(drop=True)
        self.need_change_foods, self.need_change_foods_idx = self.need_change_food(diets_df, self.light_breakfast)
        # 식단 sequence마다 -> diet_idx_df : 식단 1개

        # 변수 선언
        final_df = pd.DataFrame(columns=range(0,17))
        final_df_index = 0
        diet_df = diets_df.copy()
        need_change_foods_for_diet_idx = self.need_change_foods[0]
        food_idx_in_diet = self.need_change_foods_idx[0]
        # 식단 sequence 내 allergy 유발 식품마다
        len_need_change_foods = len(need_change_foods_for_diet_idx)
        if len_need_change_foods > 0:
            candidates = []
            score_candi = []
            food_candi = {}

            for i in range(len_need_change_foods):
                change_food = need_change_foods_for_diet_idx[i]
                change_food_idx = food_idx_in_diet[i]
                allergy_free_menus_ = self.food_candi(change_food, change_food_idx)
                allergy_free_menus = list(set(allergy_free_menus_) - set(diet_df[diet_df.columns.difference([0,6,13])].values.tolist()[0]))
                # 대체가능한 식품들 중 영양 점수가 가장 높은 식품으로 대체
                new_score_list = []
                for new_menu in allergy_free_menus:
                    new_score = int(self.calculate_nutrition_score(self.nutri_df, diet_df.replace(change_food, new_menu), self.age, self.gender)['Total_sum'])
                    new_score_list.append(new_score)
                    #highest_score_idx = new_score_list.index(max(new_score_list))
                highest_score_idx = np.argsort(new_score_list)[::-1][:10]
                food_candi[change_food] = [allergy_free_menus[i] for i in highest_score_idx]  # 알레르기 교체 필요한 음식마다 후보 10개씩 저장
                
                    #diet_idx_df.replace(change_food, allergy_free_menus[candi], inplace = True)
                    #candidates.append(diet_idx_df) # 알레르기 교체 필요한 음식마다 후보 5개씩 저장

            append_count = 0
            
            ### 코드 질문
            
            while True:
                while True:
                    new_diet = diets_df.copy()
                    for candi in food_candi:
                        food_candi_candi = food_candi[candi]
                        change_diet = new_diet.values.tolist()[0]
                        idx = list(i for i, val in enumerate(change_diet) if val == candi) #식품 위치
                        
                        #밥 통일 케이스에 대해서
                        if idx[0] in self.non_include_idx: #idx값이 밥 통일인 경우
                            new_diet.replace(candi, food_candi_candi[random.sample(range(len(food_candi_candi)), 1)[0]], inplace = True) 

                        elif (len(idx) > 1) and (idx[0] not in self.non_include_idx) :  #식품 하나보다 많은 값이 나오는데, non-included-idx가 아닐때,
                            for j in idx:
                                change_food = change_diet[j]
                                while change_food in change_diet:
                                    change_food = random.sample(food_candi_candi, 1)[0]
                                change_diet[j] = change_food
                            new_diet.loc[0] = change_diet

                        else:
                            change_food = change_diet[idx[0]]
                            while change_food in change_diet:
                                change_food = random.sample(food_candi_candi, 1)[0]
                            change_diet[idx[0]] = change_food
                            new_diet.loc[0] = change_diet
                    '''
                    체크
                    '''
                    if self.light_breakfast == '아침일반식':
                        if self.is_matching_vegi_soup(new_diet) and self.is_special_soup(new_diet):
                            break
                    elif self.light_breakfast == '아침간편식':
                        if self.is_special_soup(new_diet):
                            break
                candidates.append(new_diet)
                append_count += 1
                if append_count == self.max_append:
                    break
            
            #prior_score_list = []
            # candi에서 mispos가 가장 적고 score가 가장 높은 식단 바로 뽑기
            for candi in candidates:
                new_score = int(self.calculate_nutrition_score(self.nutri_df, candi, self.age, self.gender)['Total_sum'])
                new_pos_score = self.mispos_cal(self.nutri_df, candi, self.light_breakfast)[0]
                score_candi.append((new_score, new_pos_score))
            min_new_pos_score = min(score[1] for score in score_candi)
            filtered_candidates = [score for score in score_candi if score[1] == min_new_pos_score]
            best_candidate_index = max(range(len(filtered_candidates)), key=lambda i: filtered_candidates[i][0])
            original_index_of_best = score_candi.index(filtered_candidates[best_candidate_index])
            final_df = candidates[original_index_of_best]
            #highest_candi = np.argsort(score_candi)[::-1][:self.outputs]
            #final_df.loc[final_df_index] = list(candidates[highest_candi[0]].iloc[0])
            
            # output이 2개이상인 경우
            #for replace_food in highest_candi:
            #    #print(list(candidates[replace_food].iloc[0]))
            #    final_df.loc[final_df_index] = list(candidates[replace_food].iloc[0])
            #    final_df_index += 1
            
        
                    #diet_idx_df.replace(change_food, allergy_free_menus[highest_score_idx], inplace=True)
                    #final_df.loc[diet_idx] = diet_idx_df.values.tolist()[0]
                #print('          ', '최종점수는 {}점입니다.'.format(max(new_score_list)))
        else:
            final_df.loc[final_df_index] = diet_df.values.tolist()[0]
                #except:
                #    final_df.loc[final_df_index] = [0]*17
                #    final_df_index += 1
                #    gen_diet_idx.append(diet_idx)

        # 파일 생성 x
        #self.createFolder('./{0}'.format(str(self.age)))
        #self.createFolder('./{0}/{1}/'.format(str(self.age), str(self.gender)))
        
        '''
        Checking the nutrition scores
        1. RDI값
        2. Mispositioning 비율 출력
        3. 알러지 식품 포함 비율
        '''
        
        final_df.columns = range(1,18)
        #target_list = ['Energy', 'Protein', 'Total Dietary', 'Calcium', 'Iron', 'Sodium', 'Vitamin A',
        #               'Vitamin B1 (Thiamine)', 'Vitamin B2 (Rivoflavin)', 'Vitamin C', 'Linoleic Acid',
        #               'Alpha-Linolenic Acid', 'Carbohydrate_ratio', 'Protein_ratio', 'Fat_ratio']
        rr = self.calculate_nutrition_score(self.nutri_df, final_df, self.age, self.gender)

        
        RDI_score = rr['Total_sum'].to_list()
        mispos = self.mispos_cal(self.nutri_df, final_df, self.light_breakfast)
        #allergy_score = self.allergy_scores(final_df, self.get_allergy_foods)
        
        final_df['RDI_score'] = RDI_score
        final_df['mispos'] = mispos
        #final_df['allergy_score'] = allergy_score
        #for target in target_list:
        #    final_df[target] = rr[target]

        # filtering : mispos 비율이 가장 낮은 상태에서 RDI_score가 가장 높은것을 추출
        final_df.sort_values(['mispos', 'RDI_score'], ascending=[True, False], inplace=True)
        final_df = pd.DataFrame(final_df.iloc[0:1])
        
        return final_df
    