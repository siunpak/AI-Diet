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

#total_allergy_list_68_code = subject_allergy['Code'][0:15].tolist()
#total_allergy_list_912_code = subject_allergy['Code'][15:].tolist()

class Inspect_allergy_food:
    def __init__(self, age, gender, light_breakfast, allergy_list):
        #super().__init__()
        self.age = age
        self.gender = gender
        self.light_breakfast=light_breakfast
        self.allergy_list = allergy_list
        self.calculate_nutrition_score = calculate_nutrition
        self.prior_nutrition_score = calculate_nutrition_for_group
        self.menu_ing_nut_df = get_data(age, gender, light_breakfast)[0]
        self.nutri_df = get_data(age, gender, light_breakfast)[2]
        self.embedding = get_data(age, gender, light_breakfast)[4]
        self.ingre_allergy = get_data(age, gender, light_breakfast)[5]
        self.total_menus_allergy = self.menus_allergy()
    
    def menus_allergy(self):
        # 1. (재료-알레르기DB) 알레르기 표기가 있는 식재료 추출
        # 2. (식품-재료DB) 알레르기 식재료를 포함한 식품 추출
        # 3. {'알레르기1': [식품1,식품2,...], '알레르기2': [식품1,식품2,...], ...} 형태로 정리
        allergy_list = self.ingre_allergy.columns[1:]
        total_menus_allergy = {}

        for i in allergy_list:
            ingredient_allergy = list(self.ingre_allergy[self.ingre_allergy[i] == 1]['name'])   # 1
            menus_containing_ingres = []
            for j in ingredient_allergy:
                try:
                    menus_containing_ingre = self.menu_ing_nut_df.index[self.menu_ing_nut_df[j]==1].tolist()   # 2
                    menus_containing_ingres = menus_containing_ingres + menus_containing_ingre
                except Exception as e:
                    #print('예외가 발생했습니다.', e)
                    pass
            menus_containing_ingres = list(set(menus_containing_ingres))
            total_menus_allergy[i] = menus_containing_ingres
        return total_menus_allergy


    def get_allergy_food(self):
        # subject마다 알레르기 포함 식품들 모두 정리
        allergy_foods = []
        for allergies in self.allergy_list:
            allergy_food = self.total_menus_allergy[allergies]
            allergy_foods = allergy_foods + allergy_food
        return allergy_foods
    
    
    def wrong_place_food(self, j, food, nutri, light_breakfast):
        cat_df = nutri[['name','snack1', 'snack2', 'snack3', 'rice', 'soup', 'side_dish1', 'side_dish2', 'breakfast1', 'breakfast2', 'breakfast3', 'kimchi', 'special', 'empty']]
        food_cat = cat_df.columns[cat_df[cat_df.name == food].iloc[0]==1][0]
        place_wrong = False
        
        if light_breakfast == '아침간편식': 
            if ((j == 5) or (j == 12)) and ((food_cat != 'rice') and (food_cat != 'special')):
                place_wrong = True
            elif (j == 0) and (food_cat != 'breakfast1'):
                place_wrong = True
            elif (j == 1) and (food_cat != 'breakfast2'):
                place_wrong = True
            elif (j == 2) and (food_cat != 'breakfast3'):
                place_wrong = True  
            elif ((j == 3) or (j == 4)) and ((food_cat != 'snack3')):
                place_wrong = True 
            elif ((j == 6) or (j == 13)) and (food_cat != 'soup'):
                place_wrong = True
            elif ((j == 7) or (j == 14)) and (food_cat != 'side_dish1'):
                place_wrong = True
            elif ((j == 8) or (j == 15)) and (food_cat != 'side_dish2'):
                place_wrong = True   
            elif ((j == 9) or (j == 16)) and (food_cat != 'kimchi'):
                place_wrong = True
            elif (j == 10) and (food_cat != 'snack1'):
                place_wrong = True
            elif (j == 11) and (food_cat != 'snack2'):
                place_wrong = True
        else:
            if ((j == 0) or (j == 5) or (j == 12)) and ((food_cat != 'rice') and (food_cat != 'special')):
                place_wrong = True
            elif ((j == 3) or (j == 4)) and (food_cat != 'snack3'):
                place_wrong = True 
            elif ((j == 1) or (j == 6)) or (j == 13) and (food_cat != 'soup'):
                place_wrong = True
            elif ((j == 7) or (j == 14)) and (food_cat != 'side_dish1'):
                place_wrong = True
            elif ((j == 3) or (j == 8)) or (j == 15) and (food_cat != 'side_dish2'):
                place_wrong = True   
            elif ((j == 9) or (j == 16)) and (food_cat != 'kimchi'):
                place_wrong = True
            elif (j == 10) and (food_cat != 'snack1'):
                place_wrong = True
            elif (j == 11) and (food_cat != 'snack2'):
                place_wrong = True
        
        return place_wrong
    

    def need_change_food(self, diets):
        # subject마다 식단 내에서 바꿔야하는 식품 모두 정리
        # {'subject1': {'diet_idx1': [알레르기식품1, 알레르기식품2,...]},
        #              {'diet_idx2': [알레르기식품1, ...]},
        #                   ...
        # {'subject2': {'diet_idx1': [알레르기식품1, 알레르기식품2,...]},
        #              {'diet_idx2': [알레르기식품1, 알레르기식품2, 알레르기식품3, ...]},
        #  ...
        #  }
        allergy_foods = self.get_allergy_food()
        change_foods_per_diet = {}
        change_foods_idx_diet = {}

        for i in range(len(diets)):
            change_foods = []
            change_foods_idx = []
                
            temp = list(diets.iloc[i])
            for j in range(len(temp)):
                if temp[j] in allergy_foods:
                    change_foods.append(temp[j])
                    change_foods_idx.append(j)
                    
                    ## 위치 안맞는 식품 제거
                elif self.wrong_place_food(j, temp[j], self.nutri_df, self.light_breakfast) == True: 
                    change_foods.append(temp[j])
                    change_foods_idx.append(j)
                              
            change_foods_per_diet[i] = list(change_foods)
            change_foods_idx_diet[i] = list(change_foods_idx)
        need_change_foods = change_foods_per_diet
        need_change_foods_idx = change_foods_idx_diet
        return need_change_foods, need_change_foods_idx

### Allergy 대체

class Replace_allergy_food(Inspect_allergy_food):
    def __init__(self, age, gender, light_breakfast, allergy_list):
        super().__init__(age, gender, light_breakfast, allergy_list)
        self.get_allergy_foods = self.get_allergy_food()
        self.light_breakfast = light_breakfast

        #####################
        # params
        # roop 횟수 : max_append
        # 식단 1개당 출력 횟수 : outputs
        #####################
        self.max_append = 50
        self.outputs = 3
        
        if self.light_breakfast == '아침간편식':
            self.non_include_idx = [5,12]
                                    
        elif self.light_breakfast == '아침일반식':
            self.non_include_idx = [0,5,12]
        
    def createFolder(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    @staticmethod
    def food_cat(j, light_breakfast):
        '''
        음식의 위치를 잡아주는 함수
        '''
        food_cat = ['empty']
        if light_breakfast == '아침간편식':
            if (j == 5) or (j == 12):
                food_cat = ['rice']
            elif (j == 0):
                food_cat = ['breakfast1']
            elif (j == 1):
                food_cat = ['breakfast2']
            elif (j == 2):
                food_cat = ['breakfast3']
            elif (j == 3) or (j == 4):
                food_cat = ['snack3']
            elif (j == 6) or (j == 13):
                food_cat = ['soup']
            elif (j == 7) or (j == 14):
                food_cat = ['side_dish1']
            elif (j == 8) or (j == 15):
                food_cat = ['side_dish2']
            elif (j == 9) or (j == 16) :
                food_cat = ['kimchi']
            elif (j == 10):
                food_cat = ['snack1']
            elif (j == 11) :
                food_cat = ['snack2']
        elif light_breakfast == '아침일반식':
            if (j == 0) or (j == 5) or (j == 12):
                food_cat = ['special']
            elif (j == 3) or (j == 4):
                food_cat = ['snack3']
            elif (j == 1) or (j == 6) or (j == 13):
                food_cat = ['soup']
            elif (j == 7) or (j == 14):
                food_cat = ['side_dish1']
            elif (j == 2) or (j == 8) or (j == 15):
                food_cat = ['side_dish2']
            elif (j == 9) or (j == 16) :
                food_cat = ['kimchi']
            elif (j == 10):
                food_cat = ['snack1']
            elif (j == 11) :
                food_cat = ['snack2']
                
        return food_cat
    
    # food_candi 처리용 함수 : allergy free menu에 없는 menu name 반환
    def is_allergy_free(self, menu_name):
        return menu_name not in self.get_allergy_foods

    # food_candi 처리용 함수 2 : matching 여부 확인
    def has_matching_category(self, menu_name, cat_df, food_cat):
        filtered_df = cat_df[cat_df.name == menu_name]
        if filtered_df.empty:
            return False
        first_row = filtered_df.iloc[0]
        columns_with_value_one = cat_df.columns[first_row == 1].tolist()
        return columns_with_value_one == food_cat
    
    def food_candi(self, food, food_idx):
        # allergy-free하면서 category 동일한 후보군 추출
        cat_df = self.nutri_df[['name','snack1', 'snack2', 'snack3', 'rice', 'soup', 'side_dish1', 'side_dish2', 'breakfast1', 'breakfast2', 'breakfast3', 'kimchi', 'special', 'empty']]
        food_cat = self.food_cat(food_idx, self.light_breakfast)
        
        if (food == '종료') or (food == 'empty') or (food == 'Empty'):
            sim_menu_list = random.sample(list(cat_df[cat_df[food_cat[0]] == 1]['name']), len(list(cat_df[cat_df[food_cat[0]] == 1]['name'])))
            
            allergy_free_menus = [sim_m for sim_m in sim_menu_list if (sim_m not in self.get_allergy_foods)][:20]
            
        else:
            #old_food_cat = cat_df.columns[cat_df[cat_df.name == food].iloc[0]==1].tolist()
            emb = cosine_similarity(self.embedding, self.embedding)
            menu_idx = list(self.embedding.index).index(food)
            sim_scores = list(enumerate(emb[menu_idx]))
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
                if self.is_allergy_free(sim_m) and self.has_matching_category(sim_m, cat_df, food_cat):
                    allergy_free_menus.append(sim_m)
                    if len(allergy_free_menus) >= 20:
                        break
                    
        return allergy_free_menus
    
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
                if db[db.name == temp_diet[11]].snack.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[12]].snack.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[4]].snack.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[5]].snack.values[0] == 0:
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
                if db[db.name == temp_diet[3]].side_dish2.values[0] == 0:
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
                if db[db.name == temp_diet[11]].snack.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[12]].snack.values[0] == 0:
                    total_mis += 1 
                if db[db.name == temp_diet[4]].snack.values[0] == 0:
                    total_mis += 1
                if db[db.name == temp_diet[5]].snack.values[0] == 0:
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
    

    def food_candi_per_person(self, diets):
        diets_df = diets.reset_index(drop=True)
        self.need_change_foods, self.need_change_foods_idx = self.need_change_food(diets_df)
        # 식단 sequence마다 -> diet_idx_df : 식단 1개

        # 변수 선언
        final_df = pd.DataFrame(columns=range(0,17))
        final_df_index = 0

        diet_df = diets_df
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
                #print(need_change_foods_for_diet_idx)
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
                food_candi[change_food] = [allergy_free_menus[i] for i in highest_score_idx]  # 알레르기 교체 필요한 음식마다 후보 5개씩 저장
                
                    #diet_idx_df.replace(change_food, allergy_free_menus[candi], inplace = True)
                    #candidates.append(diet_idx_df) # 알레르기 교체 필요한 음식마다 후보 5개씩 저장

            append_count = 1
            while True:
                new_diet = diets_df.iloc[[0]]
                for candi in food_candi:
                    change_diet = new_diet.values.tolist()[0]
                    idx = list(i for i, val in enumerate(change_diet) if val == candi)

                    food_list = food_candi[candi]
                    len_food_list = len(food_list)
                    # food_candi list가 빈 리스트인 경우 에러 발생
                    if len_food_list == 0:
                        raise Exception("Error!!!")
                    
                    if idx[0] in self.non_include_idx:
                        new_diet.replace(candi, food_list[random.sample(range(len_food_list), 1)[0]], inplace = True) 

                    elif (len(idx) > 1) and (idx[0] not in self.non_include_idx) :  
                        for j in idx:
                            change_food = change_diet[j]
                            while change_food in change_diet:
                                change_food = random.sample(food_list, 1)[0]
                            change_diet[j] = change_food
                        new_diet.loc[0] = change_diet

                    else:
                        change_food = change_diet[idx[0]]
                        #print(change_food)
                        while change_food in change_diet:
                            change_food = random.sample(food_list, 1)[0]
                        change_diet[idx[0]] = change_food
                        new_diet.loc[0] = change_diet

                candidates.append(new_diet)
                append_count += 1
                if append_count == self.max_append:
                    break

            #prior_score_list = []
            for candi in candidates:
                new_score = int(self.prior_nutrition_score(self.nutri_df, candi, self.age, self.gender)['Total_sum'])
                score_candi.append(new_score)
            highest_candi = np.argsort(score_candi)[::-1][:self.outputs]


            # output이 1개이기 때문에 해당 code deprecate
            for replace_food in highest_candi:
                #print(list(candidates[replace_food].iloc[0]))
                final_df.loc[final_df_index] = list(candidates[replace_food].iloc[0])
                final_df_index += 1
            final_df.loc[final_df_index] = list(candidates[highest_candi[0]].iloc[0])
        
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
        target_list = ['Energy', 'Protein', 'Total Dietary', 'Calcium', 'Iron', 'Sodium', 'Vitamin A',
                       'Vitamin B1 (Thiamine)', 'Vitamin B2 (Rivoflavin)', 'Vitamin C', 'Linoleic Acid',
                       'Alpha-Linolenic Acid', 'Carbohydrate_ratio', 'Protein_ratio', 'Fat_ratio']
        rr = self.calculate_nutrition_score(self.nutri_df, final_df, self.age, self.gender)


        RDI_score = rr['Total_sum'].to_list()
        mispos = self.mispos_cal(self.nutri_df, final_df, self.light_breakfast)
        #allergy_score = self.allergy_scores(final_df, self.get_allergy_foods)
        
        final_df['RDI_score'] = RDI_score
        final_df['mispos'] = mispos
        #final_df['allergy_score'] = allergy_score
        for target in target_list:
            final_df[target] = rr[target]

        # filtering : mispos 비율이 가장 낮은 상태에서 RDI_score가 가장 높은것을 추출
        final_df.sort_values(['mispos', 'RDI_score'], ascending=[True, False], inplace=True)
        final_df = pd.DataFrame(final_df[[x for x in range (1,18)]].iloc[0:1])
        #print(final_df)
        
        return final_df 