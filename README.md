# 운전관계규정 간편검색 시스템 — 자동 업데이트 버전

현재 업로드된 7개 운전관련 사규의 조문을 `regulations.json`에 수록했습니다. 웹 화면은 이 JSON을 검색합니다.

## 자동 업데이트 연결
1. 이 폴더 전체를 GitHub 저장소에 업로드합니다.
2. GitHub 저장소 `Settings → Secrets and variables → Actions → Variables`에서 `SEOULMETRO_RULES_URL`을 만듭니다.
3. 값에는 **서울교통공사 홈페이지 > 공사소개 > 정관 및 사규의 실제 목록 페이지 URL**을 입력합니다.
4. Actions를 허용하면 매일 09:15(KST) `scripts/update_regulations.py`가 실행됩니다.
5. 목록 페이지에서 7개 사규의 직접 첨부 링크를 확인할 수 있을 때 파일을 내려받아 조문을 재추출하고 `regulations.json`을 갱신합니다.
6. Netlify를 GitHub 저장소와 연결하면 GitHub 커밋 후 사이트도 자동 재배포됩니다.

## 중요한 안전장치
- 대상 7개 사규만 갱신합니다.
- 새 파일의 조문 추출에 실패하면 기존 검색 데이터를 유지합니다.
- 검색 화면에는 최종 개정정보와 데이터 생성시각을 표시합니다.
- 서울교통공사 페이지가 JavaScript 전용 다운로드, 인증, POST 방식이면 `discover()` 부분을 실제 페이지 구조에 맞게 1회 조정해야 합니다.
- 현장 운전취급 판단은 검색 요약이 아니라 반드시 최신 공식 원문을 확인해야 합니다.

## 로컬 확인
브라우저의 `file://` 보안 때문에 JSON을 못 읽을 수 있습니다. 폴더에서 `python -m http.server 8000` 실행 후 `http://localhost:8000`으로 확인하세요.


## 공식 사규 페이지
- https://www.seoulmetro.co.kr/kr/board.do?menuIdx=518
- menuIdx=518
- 위 주소를 자동 확인 기본값으로 연결했습니다.
- 홈페이지 구조/보안 정책 변경 시 파서 보완이 필요할 수 있습니다.
