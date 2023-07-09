import re
import kss


f = open("/home/xaiplanet/xai_workspace/nlp_integrate/out_puts/20181119_종로_고시원_화재.txt", "r") 


lines = f.read()
print("======아무런 처리 하지 않음=========")
print(lines)
lines = lines.replace("\n"," ")
print("========문장 맨 뒷부분 줄바꿈 없애기===============")
print(lines)
    
for sent in kss.split_sentences(lines):
    print("=========KSS이용하여 출력==========")
    print(sent)


'''

** 전처리 추가로 진행**

1. 2번 뛰어쓰기 되어있는 부분은 1번으로 변경하기 
2. 숫자 및 특수문자(온점빼고) 모두 없애기
3. 줄바꿈 잘 못 되어있는 부분 변경하기

'''

