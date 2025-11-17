"""
generate_mock_logs.py

AI 학습송 서비스(멜로디 학습) 운영자 관점 대시보드를 위한
가짜 사용자 행동 로그 데이터를 생성하는 스크립트.

생성되는 파일:
- songs.csv           : 학습 노래 메타 정보 (곡 단위)
- listening_logs.csv  : 노래 재생 로그 (사용자 행동)
- quiz_results.csv    : 퀴즈 전/후 점수 로그 (학습 효과)
"""

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import os


# --- CSV 저장 폴더 지정 ---
OUTPUT_DIR = "dashboard_logs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# 0. 랜덤 시드 고정 (재현 가능하게)
# -----------------------------
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# -----------------------------
# 1. 기본 설정값
# -----------------------------
N_USERS = 50              # 가상 사용자 수
MIN_SONGS_PER_USER = 3    # 사용자당 최소 곡 수
MAX_SONGS_PER_USER = 8    # 사용자당 최대 곡 수

MIN_LISTENS_PER_SONG = 5   # 곡당 최소 재생 수
MAX_LISTENS_PER_SONG = 30  # 곡당 최대 재생 수

QUIZ_PROB = 0.5           # 곡이 퀴즈 데이터(전/후 점수)를 가질 확률

BASE_DATE = datetime(2025, 11, 15)  # 데이터 기준일 (적당히 수정 가능)
MAX_DAYS_HISTORY = 30               # 과거 30일 이내로 생성/재생 로그를 만듦


# -----------------------------
# 2. 도메인 값 정의
# -----------------------------
SUBJECTS = ["간호학", "생리학", "수학", "통계학", "역사", "영어", "기타"]
TOPICS_BY_SUBJECT = {
    "간호학": ["RAAS 시스템", "강심제 작용기전", "혈압조절 약물", "폐렴 간호", "심부전 병태생리"],
    "생리학": ["혈압 조절", "레닌-안지오텐신-알도스테론", "전해질 균형", "심장 전도계"],
    "수학": ["미분 공식", "적분 공식", "확률 분포", "선형대수 기초"],
    "통계학": ["정규분포", "가설검정", "신뢰구간", "회귀분석 개요"],
    "역사": ["조선시대 왕 연표", "임진왜란 핵심 연도", "근대 개항 사건"],
    "영어": ["의학 영단어", "병동 회화 표현", "기본 문법 패턴"],
    "기타": ["자격증 암기", "용어 정리", "약어 리스트"],
}

INPUT_TYPES = ["text", "image", "pdf", "mixed"]
SUNO_STYLES = ["ballad", "pop", "lofi", "hiphop", "edm"]
LANGUAGES = ["ko", "en", "ko-mixed"]
MAJORS = ["간호학과", "소프트웨어학과", "경영학과", "의예과", "고등학생", "기타"]

QUIZ_TYPES = ["객관식", "OX", "단답형", "서술형"]
DEVICE_TYPES = ["mobile", "desktop"]


# -----------------------------
# 3. 유틸 함수
# -----------------------------
def random_datetime_within(days_back: int) -> datetime:
    """최근 days_back일 이내의 임의 시각 반환."""
    delta_days = random.randint(0, days_back)
    delta_seconds = random.randint(0, 24 * 60 * 60 - 1)
    return BASE_DATE - timedelta(days=delta_days, seconds=delta_seconds)


def ensure_after(start_dt: datetime, max_days_after: int = 7) -> datetime:
    """start_dt 이후 ~ max_days_after일 이내의 임의 시각."""
    delta_days = random.randint(0, max_days_after)
    delta_seconds = random.randint(0, 24 * 60 * 60 - 1)
    return start_dt + timedelta(days=delta_days, seconds=delta_seconds)


# -----------------------------
# 4. 사용자 테이블 생성 (선택)
# -----------------------------
def generate_users(n_users: int) -> pd.DataFrame:
    users = []
    for i in range(1, n_users + 1):
        user_id = f"user_{i:03d}"
        major = random.choice(MAJORS)
        joined_at = random_datetime_within(MAX_DAYS_HISTORY + 10)  # 가입일은 조금 더 과거까지
        users.append(
            {
                "user_id": user_id,
                "major": major,
                "joined_at": joined_at,
            }
        )
    return pd.DataFrame(users)


# -----------------------------
# 5. 곡 정보(songs) 생성
# -----------------------------
def generate_songs(users_df: pd.DataFrame) -> pd.DataFrame:
    songs = []
    song_counter = 1

    for _, row in users_df.iterrows():
        user_id = row["user_id"]
        n_songs = random.randint(MIN_SONGS_PER_USER, MAX_SONGS_PER_USER)

        for _ in range(n_songs):
            subject = random.choice(SUBJECTS)
            topic = random.choice(TOPICS_BY_SUBJECT[subject])

            input_type = random.choice(INPUT_TYPES)

            # 입력 타입에 따라 이미지 개수/다이어그램/수식 유무를 대략적으로 설정
            if input_type == "text":
                num_images = 0
                has_formula = int(subject in ["수학", "통계학"] and random.random() < 0.3)
                has_diagram = int(random.random() < 0.2)
            elif input_type == "image":
                num_images = random.randint(1, 3)
                has_formula = int(subject in ["수학", "생리학", "간호학"] and random.random() < 0.6)
                has_diagram = int(random.random() < 0.6)
            elif input_type == "pdf":
                num_images = random.randint(0, 5)
                has_formula = int(subject in ["수학", "통계학", "생리학"] and random.random() < 0.5)
                has_diagram = int(random.random() < 0.5)
            else:  # mixed
                num_images = random.randint(1, 5)
                has_formula = int(subject in ["수학", "통계학", "생리학", "간호학"] and random.random() < 0.7)
                has_diagram = int(random.random() < 0.7)

            suno_style = random.choice(SUNO_STYLES)
            language = random.choice(LANGUAGES)
            created_at = random_datetime_within(MAX_DAYS_HISTORY)

            difficulty = random.choice(["low", "medium", "high"])

            songs.append(
                {
                    "song_id": f"song_{song_counter:04d}",
                    "user_id": user_id,
                    "subject": subject,
                    "topic": topic,
                    "input_type": input_type,
                    "num_images": num_images,
                    "has_formula": has_formula,
                    "has_diagram": has_diagram,
                    "suno_style": suno_style,
                    "language": language,
                    "difficulty": difficulty,
                    "created_at": created_at,
                }
            )
            song_counter += 1

    songs_df = pd.DataFrame(songs)
    return songs_df


# -----------------------------
# 6. 재생 로그(listening_logs) 생성
# -----------------------------
def generate_listening_logs(songs_df: pd.DataFrame) -> pd.DataFrame:
    logs = []
    log_counter = 1

    for _, song in songs_df.iterrows():
        song_id = song["song_id"]
        user_id = song["user_id"]  # 기본적으로 곡 만든 사용자는 최소 1번은 들었다고 가정
        created_at = song["created_at"]

        n_listens = random.randint(MIN_LISTENS_PER_SONG, MAX_LISTENS_PER_SONG)

        for _ in range(n_listens):
            # 곡 만든 유저 또는 다른 유저도 섞어서 재생했다고 가정
            if random.random() < 0.7:
                listen_user = user_id
            else:
                # 랜덤 다른 유저
                listen_user = f"user_{random.randint(1, N_USERS):03d}"

            played_at = ensure_after(created_at, max_days_after=MAX_DAYS_HISTORY)
            listen_duration = random.randint(10, 240)  # 10초 ~ 4분
            is_completed = int(random.random() < 0.6)  # 60% 정도는 완청
            device = random.choice(DEVICE_TYPES)

            logs.append(
                {
                    "log_id": f"log_{log_counter:06d}",
                    "user_id": listen_user,
                    "song_id": song_id,
                    "played_at": played_at,
                    "listen_duration_sec": listen_duration,
                    "is_completed": is_completed,
                    "device": device,
                }
            )
            log_counter += 1

    logs_df = pd.DataFrame(logs)
    return logs_df


# -----------------------------
# 7. 퀴즈 결과(quiz_results) 생성
# -----------------------------
def generate_quiz_results(songs_df: pd.DataFrame) -> pd.DataFrame:
    results = []
    result_counter = 1

    for _, song in songs_df.iterrows():
        # 어떤 곡은 퀴즈 데이터가 없을 수도 있음
        if random.random() > QUIZ_PROB:
            continue

        song_id = song["song_id"]
        user_id = song["user_id"]
        created_at = song["created_at"]

        # 이 곡에 대해 1~3번 정도 퀴즈를 풀었다고 가정
        n_quiz = random.randint(1, 3)

        for _ in range(n_quiz):
            quiz_type = random.choice(QUIZ_TYPES)
            max_score = random.choice([5, 10, 20])

            # before/after 점수는 어느 정도 상식적인 분포로
            before_score = np.clip(np.random.normal(loc=max_score * 0.4, scale=max_score * 0.2), 0, max_score)
            after_score = before_score + np.random.normal(loc=max_score * 0.2, scale=max_score * 0.15)
            after_score = float(np.clip(after_score, 0, max_score))

            test_at = ensure_after(created_at, max_days_after=MAX_DAYS_HISTORY)
            retention_days = (test_at.date() - created_at.date()).days

            results.append(
                {
                    "result_id": f"qr_{result_counter:06d}",
                    "user_id": user_id,
                    "song_id": song_id,
                    "quiz_type": quiz_type,
                    "max_score": max_score,
                    "before_score": round(float(before_score), 1),
                    "after_score": round(after_score, 1),
                    "test_at": test_at,
                    "retention_days": retention_days,
                }
            )
            result_counter += 1

    results_df = pd.DataFrame(results)
    return results_df


# -----------------------------
# 8. 메인 실행부
# -----------------------------
def main():
    print("가짜 로그 데이터 생성 시작...")

    # 1) 사용자 생성 (선택적이지만 있으면 분석에 좋음)
    users_df = generate_users(N_USERS)
    print(f"- users 생성: {len(users_df)}명")

    # 2) 곡 메타데이터 생성
    songs_df = generate_songs(users_df)
    print(f"- songs 생성: {len(songs_df)}곡")

    # 3) 재생 로그 생성
    listening_logs_df = generate_listening_logs(songs_df)
    print(f"- listening_logs 생성: {len(listening_logs_df)}행")

    # 4) 퀴즈 결과 생성
    quiz_results_df = generate_quiz_results(songs_df)
    print(f"- quiz_results 생성: {len(quiz_results_df)}행")

    # 5) CSV 저장
    # 날짜/시간 컬럼은 문자열로 변환해 저장하면 Tableau/Power BI에서 편리하게 사용 가능
    for df, name in [
        (users_df, "users"),
        (songs_df, "songs"),
        (listening_logs_df, "listening_logs"),
        (quiz_results_df, "quiz_results"),
    ]:
        # datetime 컬럼을 문자열로 변환
        for col in df.columns:
            if np.issubdtype(df[col].dtype, np.datetime64):
                df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

        filepath = os.path.join(OUTPUT_DIR, f"{name}.csv")
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        print(f"  -> {filepath} 저장 완료")

    print("✅ 모든 CSV 생성 완료!")


if __name__ == "__main__":
    main()
