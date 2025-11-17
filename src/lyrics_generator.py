"""
노래 가사 생성 모듈
학습 텍스트로부터 노래 가사를 먼저 생성합니다.
"""
from openai import OpenAI


def generate_lyrics(study_text: str, api_key: str, model: str = "gpt-4o-mini") -> str:
    """
    학습 텍스트로부터 노래 가사를 생성합니다.
    
    Args:
        study_text: 학습 텍스트
        api_key: OpenAI API 키
        model: 사용할 모델
        
    Returns:
        생성된 가사
    """
    client = OpenAI(api_key=api_key)
    
    prompt = f"""다음 학습용 텍스트를 노래 가사로 변환해주세요.

[학습 텍스트]
{study_text}

[요구사항]
- 학습 내용의 핵심을 모두 포함해야 합니다
- 노래로 부르기 쉬운 자연스러운 문장으로 작성해주세요
- 4~12줄 정도의 적절한 길이로 작성해주세요
- 반복되는 후렴구를 포함하면 더 좋습니다
- 학습자가 외우기 쉽도록 리듬감 있는 표현을 사용해주세요
- 한국어로 작성해주세요

[생성된 가사]"""

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "너는 학습용 노래 가사를 만드는 전문 작사가입니다. 학습 내용을 노래로 부르기 쉬운 형태로 변환해줍니다."
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1000,
    )
    
    lyrics = resp.choices[0].message.content.strip()
    
    # 불필요한 설명 제거 (가사만 추출)
    lines = lyrics.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        # 설명성 문구 제거
        if line and not line.startswith('[') and not line.startswith('(') and '가사' not in line:
            cleaned_lines.append(line)
    
    if cleaned_lines:
        return '\n'.join(cleaned_lines)
    
    return lyrics

