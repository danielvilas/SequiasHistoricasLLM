import re
from typing import List, Optional

class PdfFileInfo:
    def __init__(self, path:str, year:int, month:Optional[int]=None, day:Optional[int]=None, page:Optional[int]=None,coherent_path:Optional[bool]=None):
        self.path = path
        self.year = year
        self.month = month
        self.day = day
        self.page = page
        self.coherent_path = coherent_path
    pass

month_map = {
        'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4,
        'may': 5, 'jun': 6, 'jul': 7, 'ago': 8,
        'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12
    }

def coherent_path(range_start:int,  range_end:int,
                  year_folder:int, month:Optional[int],
                  filename:str,
                  year_2:Optional[int]=None,
                  day:Optional[int]=None,
                  month_2:Optional[int]=None
                  ) -> bool:

    if not (range_start <= year_folder <= range_end):
        #print(f"Year folder {year_folder} not in range {range_start}-{range_end}")
        return False
    if year_2 is not None and year_folder != year_2:
        #print(f"Year folder {year_folder} does not match year_2 {year_2}")
        return False
    year_file = int(filename[0:4])
    if year_file != year_folder:
        #print(f"Year file {year_file} ({filename}) does not match year folder {year_folder}")
        return False
    
    if month_2 is not None and month is not None and month != month_2:
        #print(f"Month {month} does not match month_2 {month_2}")
        return False

    if month:
        month_file = int(filename[4:6])
        if month_file != month:
            return False
    if day:
        day_file = int(filename[6:8])
        if day_file != day:
            return False
    return True

def cb_range_day(match, path=None):
    #./1965-1974/1972/1972/08/08/19720808.pdf
    year_start = int(match.group(1))
    year_end = int(match.group(2))
    year_1 = int(match.group(3))
    year = int(match.group(4))
    month = int(match.group(5))
    day = int(match.group(6))
    filename = match.group(7)[0:8]
    if path is None:
        path = match.group(0)
    coherent = coherent_path(range_start=year_start, range_end=year_end,
                              year_folder=year_1, month=month,
                              filename=filename, year_2=year, day=day)
    
    return PdfFileInfo(path=path, year=year, month=month, day=day, coherent_path=coherent)
def cb_range_day4(match, path=None):
    #./1980-1985/1984/08/08/19840808.pdf
    year_start = int(match.group(1))
    year_end = int(match.group(2))
    year = int(match.group(3))
    month = int(match.group(4))
    day = int(match.group(5))
    filename = match.group(6)[0:8]
    coherent = coherent_path(range_start=year_start, range_end=year_end,
                              year_folder=year, month=month,
                              filename=filename, day=day)
    if path is None:
        path = match.group(0)
    return PdfFileInfo(path=path, year=year, month=month, day=day, coherent_path=coherent)

def cb_range_page(match, path=None):
    #./1965-1974/1972/1972/08/08/19720808_0001.pdf
    
    year_start = int(match.group(1))
    year_end = int(match.group(2))
    year = int(match.group(3))
    year2 = int(match.group(4))
    month = int(match.group(5))
    day = int(match.group(6))
    page = int(match.group(8))
    filename = match.group(7)[0:8]
    if path is None:
        path = match.group(0)
    coherent = coherent_path(range_start=year_start, range_end=year_end,
                              year_folder=year, month=month,
                              filename=filename, year_2=year2, day=day)
    return PdfFileInfo(path=path, year=year, month=month, day=day, page=page,coherent_path=coherent)

def cb_range_page2(match, path=None):
    #./1980-1985/1984/08/08/PDF/19840808_0012.pdf
    year_start = int(match.group(1))
    year_end = int(match.group(2))
    year = int(match.group(3))
    month = int(match.group(4))
    day = int(match.group(5))
    filename = match.group(6)[0:8]
    coherent = coherent_path(range_start=year_start, range_end=year_end,
                              year_folder=year, month=month,
                              filename=filename, day=day)
    page = int(match.group(7))
    if path is None:
        path = match.group(0)   
    return PdfFileInfo(path=path, year=year, month=month, day=day, page=page, coherent_path=coherent)

def cb_month_abbr(match, path=None):
    #./1965-1974/1972/oct_1972.pdf
    year_start = int(match.group(1))
    year_end = int(match.group(2))
    year = int(match.group(3))
    month_abbr = match.group(4).lower()
    
    filename = match.group(5)
    coherent = coherent_path(range_start=year_start, range_end=year_end,
                              year_folder=year, month=None, day=None,
                              filename=filename, year_2=year)
    month = month_map.get(month_abbr, None)
    if month == None:
        print(f"Unknown month abbreviation: {month_abbr} in file {path}")

    if path is None:
        path = match.group(0)
    return PdfFileInfo(path=path, year=year, month=month, coherent_path=coherent)

def cb_month_abbr2(match, path=None):
    #./1975-1979/1978/1978/nov_1978.pdf
    year_start = int(match.group(1))
    year_end = int(match.group(2))
    year= int(match.group(3))
    year2= int(match.group(4))
    filename = match.group(6)
    month_abbr = match.group(5).lower()
    month = month_map.get(month_abbr, None)
    coherent = coherent_path(range_start=year_start, range_end=year_end,
                              year_folder=year, month=None, day=None,
                              filename=filename, year_2=year2)
    if path is None:
        path = match.group(0)
    return PdfFileInfo(path=path, year=year, month=month, coherent_path=coherent)

def cb_month_abbr3(match, path=None):
    #./1975-1979/1979/04/abr_1979.pdf
    year_start = int(match.group(1))
    year_end = int(match.group(2))
    year = int(match.group(3))
    month_folder = int(match.group(4))
    month_abbr = match.group(5).lower()
    filename = match.group(6)
    month = month_map.get(month_abbr, None)
    if month == None:
        print(f"Unknown month abbreviation: {month_abbr} in file {path}")
    if month != month_folder:
        print(f"Month folder {month_folder} does not match month abbr '{month_abbr}' ({month})")
        coherent = False
    else:
        coherent = coherent_path(range_start=year_start, range_end=year_end,
                                  year_folder=year, month=None, day=None,
                                  filename=filename)
    if path is None:
        path = match.group(0)
    return PdfFileInfo(path=path, year=year, month=month, coherent_path=coherent)

def cb_range_day2(match, path=None):
    #./1965-1974/1965/1965/19650209.pdf
    year_start = int(match.group(1))
    year_end = int(match.group(2))
    year = int(match.group(3))
    year_2 = int(match.group(4))
    month = int(match.group(5)[4:6])
    day = int(match.group(5)[6:8])
    filename = match.group(5)[0:8]
    coherent = coherent_path(range_start=year_start, range_end=year_end,
                                  year_folder=year, month=month,
                                  filename=filename, year_2=year_2, day=day)
    if path is None:
        path = match.group(0)
    return PdfFileInfo(path=path, year=year, month=month, day=day,coherent_path=coherent)

def cb_range_day3(match, path=None):
    #./1980-1985/1985/19851108.pdf
    year_start = int(match.group(1))
    year_end = int(match.group(2))
    year = int(match.group(3))
    filename = match.group(4)[0:8]
    month = int(match.group(4)[4:6])
    day = int(match.group(4)[6:8])
    coherent = coherent_path(range_start=year_start, range_end=year_end,
                                  year_folder=year, month=month,
                                  filename=filename, day=day)
    if path is None:
        path = match.group(0)
    return PdfFileInfo(path=path, year=year, month=month, day=day,coherent_path=coherent)

def cb_range_day5(match, path=None):
    #./1923-1963/19351010.pdf
    year_start = int(match.group(1))
    year_end = int(match.group(2))
    year = int(match.group(3)[0:4])
    month = int(match.group(3)[4:6])
    day = int(match.group(3)[6:8])
    filename = match.group(3)[0:8]
    coherent = coherent_path(range_start=year_start, range_end=year_end,
                                  year_folder=year, month=month,
                                  filename=filename, day=day)
    if path is None:
        path = match.group(0)
    return PdfFileInfo(path=path, year=year, month=month, day=day,coherent_path=coherent)

def cb_page(match, path=None):
    #./1963/08/08/PDF/19630808_0006.pdf
    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))
    page = int(match.group(5))
    filename = match.group(4)[0:8]
    coherent= coherent_path(range_start=year, range_end=year,
                              year_folder=year, month=month,
                              filename=filename, day=day) 
    if path is None:
        path = match.group(0)
    return PdfFileInfo(path=path, year=year, month=month, day=day, page=page, coherent_path=coherent)

def cb_day(match, path=None):
    #./1963/08/08/19630808.pdf
    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))
    filename = match.group(4)[0:8]
    coherent= coherent_path(range_start=year, range_end=year,
                              year_folder=year, month=month,
                              filename=filename, day=day)
    if path is None:
        path = match.group(0)
    return PdfFileInfo(path=path, year=year, month=month, day=day, coherent_path=coherent)

def cb_month_abbr_extremadura(match, path=None):
    #./1995-1999/1997/jun_1997_1 EXTREMADURA.pdf
    #year = int(match.group(4))
    #if year < 1000:
    #    year =int (match.group(2))
    year_start = int(match.group(1))
    year_end = int(match.group(2))
    year = int(match.group(3))
    month_abbr = match.group(4).lower()
    month = month_map.get(month_abbr, None)
    if month == None:
        print(f"Unknown month abbreviation: {month_abbr} in file {path}")
    filename = match.group(5)
    coherent = coherent_path(range_start=year_start, range_end=year_end,
                                  year_folder=year, month=None, day=None,
                                  filename=filename, year_2=year)
    if path is None:
        path = match.group(0)
    return PdfFileInfo(path=path, year=year, month=month, coherent_path=coherent)

def cb_hoy_day_code(match, path=None):
    #./1950/08/08/01195008085BAD.pdf
    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))
    filename = match.group(5)[0:8]
    coherent = coherent_path(range_start=year, range_end=year,
                              year_folder=year, month=month,
                              filename=filename, day=day)
    if path is None:
        path = match.group(0)
    return PdfFileInfo(path=path, year=year, month=month, day=day, coherent_path=coherent)

def cb_hoy_day_code2(match, path=None):
    #./1986/06/06/08/1519860608RBAD.pdf
    year = int(match.group(1))
    month = int(match.group(2))
    month_2 = int(match.group(3))
    day = int(match.group(4))
    filename = match.group(6)[0:8]
    coherent = coherent_path(range_start=year, range_end=year,
                              year_folder=year, month=month,
                              month_2=month_2,
                              filename=filename, day=day)
    if path is None:
        path = match.group(0)
    return PdfFileInfo(path=path, year=year, month=month, day=day, coherent_path=coherent)
def cb_hoy_day_code3(match, path=None):
    #./1968/1968/08/08/0819680808NBAD.pdf
    year = int(match.group(1))
    year_2 = int(match.group(2))
    month = int(match.group(3))
    day = int(match.group(4))
    filename = match.group(6)[0:8]
    coherent = coherent_path(range_start=year, range_end=year,
                              year_folder=year, month=month,
                              filename=filename, year_2=year_2, day=day)    
    if path is None:
        path = match.group(0)
    return PdfFileInfo(path=path, year=year, month=month, day=day, coherent_path=coherent)

def cb_month_abbr_hoy(match, path=None):
    #./1950/ene_1950.pdf
    year = int(match.group(1))
    month_abbr = match.group(2).lower()
    month = month_map.get(month_abbr, None)
    filename = match.group(3)
    coherent = coherent_path(range_start=year, range_end=year,
                              year_folder=year, month=None, day=None,
                              filename=filename)
    if month == None:
        print(f"Unknown month abbreviation: {month_abbr} in file {path}")
    if path is None:
        path = match.group(0)
    return PdfFileInfo(path=path, year=year, month=month, coherent_path=coherent)

patterns = [
    # ./[YEAR]-[YEAR]/[YEAR]/[YEAR]/[MONTH]/[DAY]/[YYYYMMDD].pdf
    {'pattern':r'^\./(\d{4})-(\d{4})/(\d{4})/(\d{4})/(\d{2})/(\d{2})/(\d{8})\.pdf','callback':cb_range_day,'count':0,'name':'range_day'},
    # ./[YEAR]-[YEAR]/[YEAR]/[MONTH]/[DAY]/[YYYYMMDD].pdf
    {'pattern':r'^\./(\d{4})-(\d{4})/(\d{4})/(\d{2})/(\d{2})/(\d{8})\.pdf','callback':cb_range_day4,'count':0,'name':'range_day4'},
    # ./[YEAR]-[YEAR]/[YEAR]/[YEAR]/[MONTH]/[DAY]/PDF/[YYYYMMDD]_[PAGE].pdf
    {'pattern':r'^\./(\d{4})-(\d{4})/(\d{4})/(\d{4})/(\d{2})/(\d{2})/PDF/(\d{8})_(\d{4})\.pdf','callback':cb_range_page,'count':0,'name':'range_page'},
    # ./[YEAR]-[YEAR]/[YEAR]/[MONTH_ABBR]_[YEAR].pdf
    {'pattern':r'^\./(\d{4})-(\d{4})/(\d{4})/([a-z]{3})_(\d{4})\.pdf','callback':cb_month_abbr,'count':0,'name':'month_abbr'},
    # ./[YEAR]-[YEAR]/[YEAR]/[YEAR]/[YYYYMMDD].pdf
    {'pattern':r'^\./(\d{4})-(\d{4})/(\d{4})/(\d{4})/(\d{8})\.pdf','callback':cb_range_day2,'count':0,'name':'cb_range_day2'},
    # ./[YEAR]-[YEAR]/[YEAR]/[YYYYMMDD].pdf
    {'pattern':r'^\./(\d{4})-(\d{4})/(\d{4})/(\d{8})\.pdf','callback':cb_range_day3,'count':0,'name':'cb_range_day3'},
    # ./[YEAR]-[YEAR]/[YEAR]/[MONTH]/[DAY]/PDF/[YYYYMMDD]_[PAGE].pdf
    {'pattern':r'^\./(\d{4})-(\d{4})/(\d{4})/(\d{2})/(\d{2})/PDF/(\d{8})_(\d{4})\.pdf','callback':cb_range_page2,'count':0,'name':'range_page2'},
    # ./[YEAR]-[YEAR]/[YYYYMMDD].pdf
    {'pattern':r'^\./(\d{4})-(\d{4})/(\d{8})\.pdf','callback':cb_range_day5,'count':0,'name':'cb_range_day5'},
     # ./[YEAR]-[YEAR]/[YEAR]/[YEAR]/[MONTH_ABBR]_[YEAR].pdf
    {'pattern':r'^\./(\d{4})-(\d{4})/(\d{4})/(\d{4})/([a-z]{3})_(\d{4})\.pdf','callback':cb_month_abbr2,'count':0,'name':'month_abbr2'},
    #  ./[YEAR]-[YEAR]/[YEAR]/[MONTH]/[MONTH_ABBR]_[YEAR].pdf
    {'pattern':r'^\./(\d{4})-(\d{4})/(\d{4})/(\d{2})/([a-z]{3})_(\d{4})\.pdf','callback':cb_month_abbr3,'count':0,'name':'month_abbr3'},
    # ./[YEAR]/[MONTH]/[DAY]/PDF/[YYYYMMDD]_[PAGE].pdf
    {'pattern':r'^\./(\d{4})/(\d{2})/(\d{2})/PDF/(\d{8})_(\d{4})\.pdf','callback':cb_page,'count':0,'name':'page'},

    # ./[YEAR]/[MONTH]/[DAY]/PDF/[YYYYMMDD]_[PAGE].pdf
    {'pattern':r'^\./(\d{4})/(\d{2})/(\d{2})/(\d{8})\.pdf','callback':cb_day,'count':0,'name':'day'},

    # Extremadura raros:
    # ./[YEAR]-[YEAR]/[YEAR]/[MONTH_ABBR]_[YEAR]_[NUMBER] EXTREMADURA.pdf
    {'pattern':r'^\./(\d{4})-(\d{4})/(\d{4})/([a-zA-Z]{3})_(\d{3,4})(_\d+)?\.pdf','callback':cb_month_abbr_extremadura,'count':0,'name':'month_abbr_extremadura'},
    
    # Hoy Con Codigo:    
    # ./[YEAR]/[MONTH]/[DAY]/[CODE].pdf
    {'pattern':r'^\./(\d{4})/(\d{2})/(\d{2})/(\d{2})(\d{8})([A-Z0-9]{4,})\.pdf','callback':cb_hoy_day_code,'count':0,'name':'hoy_day_code'},
    # ./[YEAR]/[MONTH]/[MONTH]/[DAY]/[CODE].pdf
    {'pattern':r'^\./(\d{4})/(\d{2})/(\d{2})/(\d{2})/(\d{2})(\d{8})([A-Z0-9]{4,})\.pdf','callback':cb_hoy_day_code2,'count':0,'name':'hoy_day_code2'},
    # ./1968/1968/08/08/0819680808NBAD.pdf
    #./[YEAR]/[YEAR]/[MONTH]/[DAY]/[CODE].pdf
    {'pattern':r'^\./(\d{4})/(\d{4})/(\d{2})/(\d{2})/(\d{2})(\d{8})([A-Z0-9]{4,})\.pdf','callback':cb_hoy_day_code3,'count':0,'name':'hoy_day_code_3'},


    #./[YEAR]/[MONTH_ABBR]_[YEAR]_N.pdf
    {'pattern':r'^\./(\d{4})/([a-zA-Z]{3})[_-](\d{4})(_\d){0,2}\.pdf','callback':cb_month_abbr_hoy,'count':0,'name':'month_abbr_hoy'},
    ]

bad_ends=[
    " EXTREMADURA.pdf\n",
    " EXTREMATURA.pdf\n",
    " EXTREMADURAA.pdf\n",
    " Extremadura.pdf\n",
    " EXTREMADURAAA.pdf\n",
    " EXTREMAADURA.pdf\n",
    " EXTREMDURA.pdf\n",
    

    "  HOY.pdf\n",
    " HOY.pdf\n",
    "_HOY.pdf\n",
    " HOY0.pdf\n",
    " HOY_1.pdf\n",
    " HOY_2.pdf\n",
    "_ 2HOY.pdf\n",
    " HOy.pdf\n",
    " Hoy.pdf\n",
    " hoy.pdf\n",
    "_1HOY.pdf\n",
    " H0Y.pdf\n",
]

class PdfManager:
    def __init__(self, pdf_raw_path="./data/datasets/raw"):
        self.pdf_raw_path = pdf_raw_path

    def extract_text(self):
        # Placeholder for text extraction logic
        pass

    def save_text(self, text, output_path):
        # Placeholder for saving extracted text logic
        pass

    def _validate_newspaper(self, newspaper):
        if newspaper not in ["extremadura", "hoy"]:
            raise ValueError(f"Newspaper '{newspaper}' is not supported.")
        pass


    def _match_patterns(self, line: str, debug=False) -> Optional[PdfFileInfo]:
        path = line.strip()
        if debug:
            print (f"Matching line: {line.strip()}")
        
        if line.endswith("19891 HOY.pdf\n"):
            line = line.replace("19891 HOY.pdf\n","1989.pdf\n")

        if "1er semestre/" in line:
            line = line.replace("1er semestre/","")
        if "2o semestre/" in line:
            line = line.replace("2o semestre/","")
        if "2do semestre/" in line:
            line = line.replace("2do semestre/","")

        for bad_end in bad_ends:
            if line.endswith(bad_end):
                line = line.replace(bad_end,".pdf\n")
        if "/julio_" in line:
            line = line.replace("/julio_","/jul_")
        if "/junio_" in line:
            line = line.replace("/junio_","/jun_")

        for pattern in patterns:
            if debug:
                print(f"Trying pattern: {pattern['name']}") 
            match = re.match(pattern['pattern'], line.strip())

            if match:
                try:
                    pdf = pattern['callback'](match,path=path)
                except Exception as e:
                    print(f"Error processing line: {line.strip()} with pattern: {pattern['name']}") 
                    raise e
                
                pattern['count'] += 1
                return pdf
        print(f"No pattern matched for line: {line.strip()}")
        return None

    def list_pdfs(self,newspaper="extremadura", year=None) -> List[PdfFileInfo]:
        self._validate_newspaper(newspaper)
        lines=0
        pdfs = []
        for pattern in patterns:
            pattern['count']=0 

        with open(f"{self.pdf_raw_path}/{newspaper}.txt", "r") as f:
            for line in f:
                pdf = self._match_patterns(line)
                if pdf:
                    if year is None or pdf.year == year:
                        pdfs.append(pdf)
                        lines += 1
                else:
                    print(f"Line did not match any pattern: {line.strip()}") 
                    # self._match_patterns(line, debug=True)
                    return pdfs #
                    
        print(f"Found {lines} PDFs for newspaper '{newspaper}' with year filter '{year}'")
        return pdfs
