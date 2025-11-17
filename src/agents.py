# src/agents.py
SYSTEM_CORE = (
    "너는 학습자를 위한 기억 보조 작곡가다. "
    "입력된 학습 텍스트를 쉽고 경쾌하게 외울 수 있도록 리듬, 멜로디, 반복 구조를 설계해라. "
    "한국어로 답하고, 간결하지만 구체적으로 안내해."
)

def build_mnemonic_plan(client, study_text, final_lyrics: str = None, model="gpt-4o-mini"):
    """
    Create a structured plan describing how to sing the study text so that the
    learner can memorise it easily.
    
    Args:
        client: OpenAI 클라이언트
        study_text: 학습 텍스트
        final_lyrics: 이미 생성된 최종 가사 (있으면 포함)
        model: 사용할 모델
    """
    if final_lyrics:
        # 가사가 이미 생성된 경우, 그 가사를 포함하여 멜로디 가이드 생성
        prompt = f"""
다음 학습용 텍스트와 생성된 노래 가사를 바탕으로 멜로디 가이드를 만들어라.

[학습 텍스트]
{study_text}

[생성된 최종 가사]
{final_lyrics}

[출력 포맷]
1) 요약 포인트 3~5개 (암기할 핵심 단위)
2) 추천 리듬/템포/박자 (예: 4/4, 90BPM, 스윙 등)
3) 음 높이 가이드 (계이름 또는 숫자음으로 한 줄, 필요한 경우 두 줄)
4) 반복 구조와 하이라이트 (후렴, 콜앤리스폰스 등)
5) 최종 가창 가이드 가사 (위에 제공된 생성된 최종 가사를 그대로 전체 표시)
6) 보너스 암기 팁 한 줄

조건:
- 5번 항목에는 위에 제공된 "생성된 최종 가사"를 그대로 전체 표시해야 합니다.
- 가사를 수정하거나 요약하지 말고 전체를 그대로 표시하세요.
- 음 높이는 초보자가 따라 부르기 쉽게 단계적으로 움직이도록 제안.
- 다른 설명은 하지 말고 위 포맷만 채워서 출력.
""".strip()
    else:
        # 가사가 없는 경우 기존 방식
        prompt = f"""
다음 학습용 텍스트를 빠르게 외울 수 있도록 멜로디 가이드를 만들어라.

[학습 텍스트]
{study_text}

[출력 포맷]
1) 요약 포인트 3~5개 (암기할 핵심 단위)
2) 추천 리듬/템포/박자 (예: 4/4, 90BPM, 스윙 등)
3) 음 높이 가이드 (계이름 또는 숫자음으로 한 줄, 필요한 경우 두 줄)
4) 반복 구조와 하이라이트 (후렴, 콜앤리스폰스 등)
5) 최종 가창 가이드 가사 (학습 텍스트를 적절히 변형하되 의미 유지, 4~8줄)
6) 보너스 암기 팁 한 줄

조건:
- 학습 텍스트의 핵심 용어는 가창 가이드에 반드시 포함.
- 음 높이는 초보자가 따라 부르기 쉽게 단계적으로 움직이도록 제안.
- 다른 설명은 하지 말고 위 포맷만 채워서 출력.
""".strip()

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_CORE},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
    )
    return resp.choices[0].message.content.strip()