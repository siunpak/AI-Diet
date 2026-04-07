import argparse
import ast
from change import Replace_allergy_food
import time


def get_params():
    parser = argparse.ArgumentParser(description = 'receive the parameters')
        
        
    parser.add_argument('--ages', type=str, required=True, help='type: 6to8 or 9to12')
    parser.add_argument('--gender', type=str, required = True, help = 'type: boy or girl')
    parser.add_argument('--light_breakfast', type = str, required = True, help = 'type: 아침간편식 or 아침일반식')

    def arg_as_list(s):
        v = ast.literal_eval(s)
        if type(v) is not list:
            raise argparse.ArgumnentTypeError("Argument \"%s\" is not a list" % (s))
        
        return v

    parser.add_argument('--allergy_list', type=arg_as_list, default = [], required = True, help = '알레르기 list')

    ### 입력시 list 내 '' 앞에 \ 입력해주기
    ### 입력 예시: [\'콩류\', \'밀\']
    
    args = parser.parse_args()
    
    return args

def check_argument(args):
    print('ages: {}'.format(args.ages))
    print('gender: {}'.format(args.gender))
    print('light_breakfast: {}'.format(args.light_breakfast))
    
    print('allergy_list: {}'.format(args.allergy_list))


'''
Allergy_name의 설명:

식재료 알레르기표기_식품군 분류통합정리_농진청 자문.xlsx 파일 참조.

allergy_name의 argument는 다음과 같은 대표이름만 들어갈 수 있음. (띄어쓰기 금지, 괄호는 참조)
list 형태로 입력 가능

밀: 밀, 보리, 귀리, 오트밀
쌀: 쌀
메밀: 메밀
콩류: 콩류, 콩나물, 숙주, 대두유
땅콩: 땅콩
호두: 호두
잣: 잣
밤: 밤
아몬드: 아몬드
헤즐넛: 헤즐넛
캐슈넛: 캐슈넛
피칸: 피칸
피스타치오: 피스타치오
들깨: 들깨, 들깻잎, 들기름
참깨: 참깨, 검정깨
씨앗: 씨앗, 씨, 열매
돼지: 돼지, 젤라틴 (젤라틴: 젤라틴 함유 유제품)
오리: 오리
닭: 닭
기타가금류: 가금류 (닭, 오리 외 조류)
난류: 난류
우유 및 유제품: 우유
붉은살생선: 붉은살생선, 고등어, 삼치, 참치, 정어리, 꽁치, 멸치
흰살생선: 흰살생선, 대구, 갈치, 조기, 연어, 돔, 장어
기타생선: 기타생선 (흰살, 붉은 살로 구별이 불가능한 생선류)
장어: 장어
멸치: 멸치
게: 게, 어묵
새우: 새우, 어묵
가재: 가재
조개: 조개, 꼬막
굴: 굴
홍합: 홍합, 담치
오징어: 오징어, 한치, 꼴뚜기
문어: 문어, 주꾸미
낙지: 낙지
고둥: 고둥, 다슬기, 골뱅이
소라: 소라
전복: 전복, 오분자기
오이: 오이
마늘: 마늘
샐러리: 샐러리
당근: 당근
브로콜리: 브로콜리
양파: 양파
겨자: 겨자
후추: 후추
토마토: 토마토
체리류: 체리, 버찌, 아로니아, 아세로라, 앵두
자두: 자두
키위: 키위, 다래
바나나: 바나나, 으름
사과: 사과
배: 배
코코넛: 코코넛
복숭아: 복숭아
메론: 메론
수박: 수박
시트러스: 오렌지, 귤, 자몽, 레몬, 유자, 라임, 탱자
망고: 망고
아황산류: 아황산류, 절임류, 통조림, 가공식품, 김치류


'''
    
    
args = get_params()
    
if __name__ == "__main__":
    start_time = time.time()
    check_argument(args)
    print("check_argument Time : ", time.time() - start_time)
    Replace_allergy_food(args.ages, args.gender, args.light_breakfast, args.allergy_list).food_candi_per_person()
    print("replace_allergy_Food Time : ", time.time() - start_time)