const statusEl = document.getElementById("status");
const backendUrlEl = document.getElementById("backend-url");
const backendBase = window.BACKEND_BASE || "http://localhost:8000";

backendUrlEl.textContent = backendBase;

const generateBtn = document.getElementById("generate-btn");
const fileInput = document.getElementById("file-input");
const fileListEl = document.getElementById("file-list");
const textInput = document.getElementById("text-input");
const charCountEl = document.getElementById("char-count");
const waitCheckbox = document.getElementById("wait-audio");
const studyTextEl = document.getElementById("study-text");
const planTextEl = document.getElementById("plan-text");
const audioContainer = document.getElementById("audio-output");

// 선택된 파일들 관리
let selectedFiles = [];

function setStatus(message) {
  statusEl.textContent = message;
}

function setPre(el, value) {
  el.textContent = value?.trim() || "-";
}

function clearAudio() {
  audioContainer.innerHTML = "";
  audioContainer.append("없음");
}

function downloadAudio(url, filename) {
  // 오디오 다운로드 함수
  fetch(url)
    .then(response => response.blob())
    .then(blob => {
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = filename || "learning-song.mp3";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);
    })
    .catch(error => {
      console.error("다운로드 실패:", error);
      alert("오디오 다운로드에 실패했습니다.");
    });
}

function renderAudio(urls) {
  audioContainer.innerHTML = "";
  if (!urls || urls.length === 0) {
    audioContainer.append("없음");
    return;
  }
  urls.forEach((url, index) => {
    const audioWrapper = document.createElement("div");
    audioWrapper.style.marginBottom = "16px";
    
    const audio = document.createElement("audio");
    audio.controls = true;
    audio.src = url;
    audio.style.width = "100%";
    audio.style.marginBottom = "8px";
    
    const downloadBtn = document.createElement("button");
    downloadBtn.textContent = "다운로드";
    downloadBtn.style.cssText = `
      background: #10b981;
      color: white;
      border: none;
      border-radius: 6px;
      padding: 6px 12px;
      font-size: 0.9rem;
      cursor: pointer;
      margin-top: 4px;
    `;
    downloadBtn.onmouseover = () => {
      downloadBtn.style.background = "#059669";
    };
    downloadBtn.onmouseout = () => {
      downloadBtn.style.background = "#10b981";
    };
    
    const filename = `learning-song-${index + 1}.mp3`;
    downloadBtn.onclick = () => downloadAudio(url, filename);
    
    audioWrapper.appendChild(audio);
    audioWrapper.appendChild(downloadBtn);
    audioContainer.appendChild(audioWrapper);
  });
}

// 파일 목록 업데이트
function updateFileList() {
  fileListEl.innerHTML = "";
  if (selectedFiles.length === 0) {
    return;
  }
  
  selectedFiles.forEach((file, index) => {
    const item = document.createElement("div");
    item.className = "file-item";
    
    const fileName = document.createElement("span");
    fileName.className = "file-name";
    fileName.textContent = file.name;
    
    const fileType = document.createElement("span");
    fileType.className = "file-type";
    fileType.textContent = file.type === "application/pdf" ? "PDF" : "이미지";
    
    const removeBtn = document.createElement("button");
    removeBtn.textContent = "삭제";
    removeBtn.onclick = () => {
      selectedFiles.splice(index, 1);
      updateFileList();
      updateFileInput();
    };
    
    item.appendChild(fileName);
    item.appendChild(fileType);
    item.appendChild(removeBtn);
    fileListEl.appendChild(item);
  });
}

// 파일 입력 업데이트 (DataTransfer 사용)
function updateFileInput() {
  const dt = new DataTransfer();
  selectedFiles.forEach(file => dt.items.add(file));
  fileInput.files = dt.files;
}

// 파일 선택 이벤트
fileInput.addEventListener("change", (e) => {
  const files = Array.from(e.target.files);
  const images = files.filter(f => f.type.startsWith("image/"));
  const pdfs = files.filter(f => f.type === "application/pdf");
  
  // 이미지 개수 확인 (최대 5장)
  const currentImages = selectedFiles.filter(f => f.type.startsWith("image/"));
  if (currentImages.length + images.length > 5) {
    alert("이미지는 최대 5장까지 업로드할 수 있습니다.");
    return;
  }
  
  // PDF 개수 확인 (최대 1개)
  const currentPdfs = selectedFiles.filter(f => f.type === "application/pdf");
  if (currentPdfs.length + pdfs.length > 1) {
    alert("PDF는 최대 1개까지 업로드할 수 있습니다.");
    return;
  }
  
  // 새 파일 추가
  selectedFiles.push(...files);
  updateFileList();
  updateFileInput();
});

// 글자수 카운터 업데이트
function updateCharCount() {
  const length = textInput.value.length;
  const maxLength = 300;
  charCountEl.textContent = `${length} / ${maxLength}`;
  
  // 색상 변경
  charCountEl.classList.remove("warning", "error");
  if (length > maxLength * 0.9) {
    charCountEl.classList.add("error");
  } else if (length > maxLength * 0.7) {
    charCountEl.classList.add("warning");
  }
}

// 텍스트 입력란 글자수 카운터 이벤트
textInput.addEventListener("input", updateCharCount);
textInput.addEventListener("paste", () => {
  setTimeout(updateCharCount, 0);
});

function disableControls() {
  generateBtn.disabled = true;
  fileInput.disabled = true;
  textInput.disabled = true;
}

function enableControls() {
  generateBtn.disabled = false;
  fileInput.disabled = false;
  textInput.disabled = false;
}

function fileToDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("파일을 읽을 수 없습니다."));
    reader.readAsDataURL(file);
  });
}

async function postJSON(path, payload) {
  const resp = await fetch(`${backendBase}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`${path} 요청 실패 (${resp.status}): ${text}`);
  }

  return resp.json();
}

async function postFormData(path, formData) {
  const resp = await fetch(`${backendBase}${path}`, {
    method: "POST",
    body: formData,
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`${path} 요청 실패 (${resp.status}): ${text}`);
  }

  return resp.json();
}

async function handleGenerate() {
  try {
    disableControls();
    
    // 텍스트 입력 또는 파일 업로드 확인
    const inputText = textInput.value.trim();
    const hasFiles = selectedFiles.length > 0;
    
    if (!inputText && !hasFiles) {
      throw new Error("텍스트를 입력하거나 파일을 업로드해주세요.");
    }
    
    if (inputText.length > 300) {
      throw new Error("텍스트는 300자를 초과할 수 없습니다.");
    }

    clearAudio();
    setPre(studyTextEl, "-");
    setPre(planTextEl, "-");

    let studyText = "";
    
    // 텍스트 입력이 있으면 우선 사용
    if (inputText) {
      studyText = inputText;
      setStatus("입력된 텍스트 사용 중...");
      setPre(studyTextEl, studyText);
    } else if (hasFiles) {
      // 파일이 있으면 다중 파일 처리
      setStatus("파일 분석 중...");
      
      const formData = new FormData();
      selectedFiles.forEach((file, index) => {
        formData.append("files", file);
      });
      
      const extractResp = await postFormData("/extract-from-files", formData);
      studyText = extractResp.study_text?.trim();
      
      if (!studyText) {
        throw new Error("파일에서 내용을 추출하지 못했습니다.");
      }
      
      setPre(studyTextEl, studyText);
    }

    if (!studyText) {
      throw new Error("처리할 텍스트가 없습니다.");
    }

    setStatus("가사 및 멜로디 가이드 생성 중...");
    const planResp = await postJSON("/mnemonic-plan", { study_text: studyText });
    const mnemonicPlan = planResp.mnemonic_plan || "";
    setPre(planTextEl, mnemonicPlan);

    setStatus("Suno 노래 생성 중...");
    const songResp = await postJSON("/generate-song", {
      study_text: studyText,
      mnemonic_plan: mnemonicPlan,
      wait_for_audio: Boolean(waitCheckbox.checked),
    });
    renderAudio(songResp.audio_urls || []);

    if (songResp.audio_urls && songResp.audio_urls.length > 0) {
      setStatus("완료! 곡을 재생해보세요.");
    } else {
      setStatus("생성 완료. 오디오 URL을 응답에서 찾지 못했습니다.");
    }
  } catch (error) {
    console.error(error);
    setStatus(`에러: ${error.message || error}`);
  } finally {
    enableControls();
  }
}

generateBtn.addEventListener("click", handleGenerate);
