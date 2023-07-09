import os
import re

import olefile
import zlib
import struct

import hanja
import pdfplumber
from jamo import h2j, j2hcj
import pdftotext
# from pykospacing import Spacing #MEMO Spacing

from utils.utils import LexRanking, Params
# from utils import LexRanking, Params

import docx2txt


class Conversion:
    def __init__(self, file_path_list): 
        
        self.file_path_list = file_path_list
        # self.spacing = Spacing()   #MEMO Spacing
        self.params = Params(f'config/config.yml')

    def get_pdf_text(self):
        pdf = pdfplumber.open(self.file_path_list)
        pages = len(pdf.pages)
        name = os.path.splitext(os.path.basename(self.file_path_list))[0] + '.txt'
        f = open(self.params.save_path + '/' + name, 'w', encoding='utf-8')

        for k in range(pages):
            try:
                de_dupe_pages = pdf.pages[k].dedupe_chars(tolerance=1)
                page = de_dupe_pages.extract_text(
                    x_tolerance=3, y_tolerance=3, layout=False, x_density=7.25, y_density=13
                )
                if page[:5] == '(cid:':
                    with open(self.file_path_list, "rb") as f:
                        page = pdftotext.PDF(self.file_path_list)[k]
                page = hanja.translate(page, 'substitution')
                f.write(page)
            except:
                page = pdf.pages[k].extract_text(
                    x_tolerance=3, y_tolerance=3, layout=False, x_density=7.25, y_density=13
                )
                if page[:5] == '(cid:':
                    with open(self.file_path_list, "rb") as f:
                        page = pdftotext.PDF(f)[k]
                page = hanja.translate(page, 'substitution')
                f.write(page)
                continue

        f.close()

    def get_docx_text(self):
        name = os.path.splitext(os.path.basename(self.file_path_list))[0] + '.txt'
        docx = docx2txt.process(self.file_path_list)
        print("==============================DOCX==============================")
        print(docx)

        with open(os.path.join(self.params.save_path, name), 'w', encoding='utf-8') as f:
            f.write(docx)


    def get_hwp_text(self):
    
        name = os.path.splitext(os.path.basename(self.file_path_list))[0] + '.txt'
        f = olefile.OleFileIO(self.file_path_list)
        dirs = f.listdir()

        # HWP 파일 검증/home/xaiplanet/new_workspace/nlp_integrate/SampleData/hwp/경기 안산 ㈜켐코 화재.hwp
        if ["FileHeader"] not in dirs or \
        ["\x05HwpSummaryInformation"] not in dirs:
            raise Exception("Not Valid HWP.")

        # 문서 포맷 압축 여부 확인
        header = f.openstream("FileHeader")
        header_data = header.read()
        is_compressed = (header_data[36] & 1) == 1

        # Body Sections 불러오기
        nums = []
        for d in dirs:
            if d[0] == "BodyText":
                nums.append(int(d[1][len("Section"):]))
        sections = ["BodyText/Section"+str(x) for x in sorted(nums)]

        # 전체 text 추출
        text = ""
        for section in sections:
            bodytext = f.openstream(section)
            data = bodytext.read()

            if is_compressed:
                unpacked_data = zlib.decompress(data, -15)
            else:
                unpacked_data = data
        
            # 각 Section 내 text 추출    
            section_text = ""
            i = 0
            size = len(unpacked_data)
            while i < size:
                header = struct.unpack_from("<I", unpacked_data, i)[0]
                rec_type = header & 0x3ff
                rec_len = (header >> 20) & 0xfff

                if rec_type in [67]:
                    rec_data = unpacked_data[i+4:i+4+rec_len]
                    section_text += rec_data.decode('utf-16')
                    section_text += "\n"

                i += 4 + rec_len

            text += section_text
            text += "\n"
            text = hanja.translate(text, 'substitution')

        with open(os.path.join(self.params.save_path, name), 'w', encoding='utf-8') as f:
            f.write(text)
            print("==============================HWP==============================")
            print(text)


        return 

    def report_prep(self, txt_file, save_path_plumber):
        dt = open(txt_file, 'r', encoding='utf-8')
        ori_text = dt.read().replace('\n', ' ')
        text = ori_text

        # 1. Add newline before bullet number
        filter1 = re.compile(r' *\([0-9]+\) +')
        filter2 = re.compile(r' +[0-9]+\) +')
        filter3 = re.compile(r' [0-9]+[.] +[^0-9]')

        index = [(m.start(0), m.end(0)) for filter in [filter1, filter2, filter3]
                for m in re.finditer(filter, ori_text)]

        for i in range(len(index)):
            rep = ori_text[index[i][0]:index[i][1]]
            text = text.replace(rep, '\n'+rep)
            text = re.sub(' +', ' ', text)

        # 2. Add newline before bullet symbol
        symbol = self.params.symbol

        # 3. Add newline before special symbol
        exception = self.params.exceptions

        r = re.compile('[^A-Za-z0-9가-힣\s]')

        txt = []
        name = os.path.basename(txt_file)
        # text = self.spacing(text)
  
        for idx, k in enumerate(text):
             # Run number 2
            if text[idx:idx+2] in symbol:
                k = '\n' + k

            # run number 3
            if r.search(k) is not None:
                word = r.search(k).group()
                if word not in exception:
                    k = k.replace(word, '\n' + word)

            if text[idx-1:idx+2] == '다. ':
                k = k + '\n'

            if idx != 0:
                last = (j2hcj(h2j(text[idx-1]))[-1], j2hcj(h2j(text[idx]))[-1])
                if last == ('ㅁ', '.') or last == ('ㅅ', '.'):
                    k = k + '\n'

            txt.append(re.sub('[^a-zA-Z0-9ㄱ-ㅣ가-힣\-.\n]',' ',k))
        
        #
        txt = ''.join(txt)
        with open(os.path.join(save_path_plumber,name+'_1'),'w', encoding='utf-8') as f :
            f.writelines('\n'.join(txt))
        #        
        
        txt_lines = LexRanking(str(txt))

        with open(os.path.join(save_path_plumber, name), 'w', encoding='utf-8') as f:
            f.writelines('\n'.join(txt_lines.summary['text']))
