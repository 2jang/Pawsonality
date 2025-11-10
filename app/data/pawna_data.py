"""
Pawna 데이터 로더
CSV 파일에서 Pawna 질문 및 유형 정보를 로드합니다.
"""
import csv
from typing import List, Dict, Optional
from pathlib import Path


class PawnaDataLoader:
    """Pawna 데이터를 로드하고 관리하는 클래스"""
    
    def __init__(self):
        self.data_dir = Path("data/raw")
        self.pawna_types: Dict[str, Dict] = {}
        self.questions: List[Dict] = []
        self._load_data()
    
    def _load_data(self):
        """CSV 파일에서 데이터 로드"""
        # Pawna 유형 정보 로드
        pawna_csv = self.data_dir / "pawna_types.csv"
        if pawna_csv.exists():
            with open(pawna_csv, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.pawna_types[row['Pawna']] = row
            print(f"✅ {len(self.pawna_types)}개의 Pawna 유형 로드 완료")
        else:
            print(f"⚠️  {pawna_csv} 파일을 찾을 수 없습니다.")
        
        # 질문 데이터는 하드코딩
        self._load_questions()
    
    def _load_questions(self):
        """Pawna 질문 생성 (12개)"""
        self.questions = [
            {"id": 1, "title": "산책 나가자고 하면?", "type": "EI",
             "option_a": "즉시 뛰어나간다", "option_b": "잠시 생각한 후 나간다"},
            {"id": 2, "title": "낯선 사람을 만나면?", "type": "EI",
             "option_a": "적극적으로 다가간다", "option_b": "조심스럽게 관찰한다"},
            {"id": 3, "title": "새로운 장난감을 주면?", "type": "EI",
             "option_a": "즉시 가지고 논다", "option_b": "먼저 냄새를 맡아본다"},
            {"id": 4, "title": "공원에서 노는 스타일은?", "type": "SN",
             "option_a": "여기저기 탐험한다", "option_b": "주인 근처에 있다"},
            {"id": 5, "title": "새로운 환경에 가면?", "type": "SN",
             "option_a": "호기심 있게 탐색한다", "option_b": "익숙해질 때까지 기다린다"},
            {"id": 6, "title": "놀이 방식은?", "type": "SN",
             "option_a": "매번 새로운 방식", "option_b": "좋아하는 방식 반복"},
            {"id": 7, "title": "훈련할 때?", "type": "TF",
             "option_a": "간식에 집중한다", "option_b": "칭찬에 집중한다"},
            {"id": 8, "title": "주인이 슬플 때?", "type": "TF",
             "option_a": "장난감을 가져온다", "option_b": "조용히 옆에 있다"},
            {"id": 9, "title": "문제 상황에?", "type": "TF",
             "option_a": "해결책을 찾는다", "option_b": "주인의 반응을 본다"},
            {"id": 10, "title": "일상 패턴은?", "type": "JP",
             "option_a": "매번 다르다", "option_b": "규칙적이다"},
            {"id": 11, "title": "새로운 명령을 배울 때?", "type": "JP",
             "option_a": "즉흥적으로 시도", "option_b": "단계별로 학습"},
            {"id": 12, "title": "놀이 시간은?", "type": "JP",
             "option_a": "언제든지 놀고 싶어한다", "option_b": "정해진 시간을 좋아한다"},
        ]
    
    def get_questions(self) -> List[Dict]:
        """모든 질문 반환"""
        return self.questions
    
    def get_pawna_type(self, pawna_code: str) -> Optional[Dict]:
        """Pawna 코드로 유형 정보 조회"""
        return self.pawna_types.get(pawna_code)
    
    def calculate_pawna(self, answers: List[Dict]) -> str:
        """답변으로부터 Pawna 코드 계산"""
        # EI, SN, TF, JP 각 차원별 점수 계산
        scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
        
        for answer in answers:
            question = self.questions[answer["question_id"] - 1]
            dimension = question["type"]
            
            if answer["selected"] == "A":
                # A는 첫 번째 글자 (E, S, T, J)
                scores[dimension[0]] += 1
            else:
                # B는 두 번째 글자 (I, N, F, P)
                scores[dimension[1]] += 1
        
        # 각 차원에서 더 높은 점수를 선택
        pawna = ""
        pawna += "W" if scores["E"] > scores["I"] else "D"  # W=외향, D=내향
        pawna += "T" if scores["S"] > scores["N"] else "I"  # T=현실, I=직관
        pawna += "I" if scores["T"] > scores["F"] else "L"  # I=이성, L=감성
        pawna += "L" if scores["J"] > scores["P"] else "P"  # L=계획, P=즉흥
        
        return pawna


# 전역 데이터 로더 인스턴스
_data_loader: Optional[PawnaDataLoader] = None


def get_data_loader() -> PawnaDataLoader:
    """데이터 로더 싱글톤 인스턴스 반환"""
    global _data_loader
    if _data_loader is None:
        _data_loader = PawnaDataLoader()
    return _data_loader

