<template>
  <div class="ai-workspace">
    <!-- 좌측 인트로 브랜드 패널 -->
    <section class="intro-panel">
      <div class="brand-badge">
        <span class="status-dot"></span>
        <span class="brand-tag">JARYONG AI LABS</span>
      </div>

      <div class="hero-graphic">
        <div class="glowing-core">
          <div class="core-spark">✦</div>
        </div>
        <div class="orbit-ring ring-1"></div>
        <div class="orbit-ring ring-2"></div>
      </div>

      <div class="intro-content">
        <p class="kicker">INTELLIGENT WORKSPACE</p>
        <h1>모빌리티 전장 업무의<br /><span class="gradient-text">다음 단계를 시작해보세요.</span></h1>
        <p class="desc">자룡모빌리티의 사내 데이터베이스와 표준 문서를 실시간 분석하는 차세대 AI Copilot입니다.</p>
      </div>

      <div class="capability-grid">
        <div class="cap-card">
          <div class="cap-icon blue">⌁</div>
          <div class="cap-info">
            <strong>사내 데이터</strong>
            <small>사원 · ECU · BMS 로그</small>
          </div>
        </div>
        <div class="cap-card purple">
          <div class="cap-icon violet">⌕</div>
          <div class="cap-info">
            <strong>문서 RAG</strong>
            <small>채용공고 · 사내 규정 PDF</small>
          </div>
        </div>
        <div class="cap-card green">
          <div class="cap-icon green">↗</div>
          <div class="cap-info">
            <strong>자동화 실행</strong>
            <small>등록 · 수정 · 삭제 CRUD</small>
          </div>
        </div>
      </div>

      <div class="security-footer">
        <span class="check-icon">✓</span>
        <span>보안 세션 적용됨 (사내 데이터 세션 보호)</span>
      </div>
    </section>

    <!-- 우측 대화형 메인 인터페이스 -->
    <section class="chat-panel">
      <header class="chat-header">
        <div class="agent-profile">
          <div class="avatar-box">✦</div>
          <div class="agent-meta">
            <h2>Jaryong Copilot <span class="version-tag">v3.5</span></h2>
            <span class="status-text"><i class="online-indicator"></i> Active & Ready</span>
          </div>
        </div>
        <button class="btn-clear" type="button" :disabled="isLoading" @click="clearConversation">
          <span class="icon">↺</span> 새 세션
        </button>
      </header>

      <!-- 메시지 대화 창 -->
      <div ref="chatBox" class="chat-viewport" aria-live="polite">
        <div class="timeline-divider"><span>Today</span></div>

        <div 
          v-for="(msg, index) in messages" 
          :key="`${msg.role}-${index}`" 
          :class="['chat-row', msg.role]"
        >
          <div v-if="msg.role === 'ai'" class="avatar ai-avatar">✦</div>
          <div class="bubble-group">
            <span v-if="msg.role === 'ai'" class="sender-name">Jaryong AI</span>
            <div class="bubble-body" v-html="renderMarkdown(msg.text)"></div>
            <time v-if="msg.time" class="timestamp">{{ msg.time }}</time>
          </div>
          <div v-if="msg.role === 'user'" class="avatar user-avatar">ME</div>
        </div>

        <!-- 로딩 애니메이션 -->
        <div v-if="isLoading" class="chat-row ai">
          <div class="avatar ai-avatar">✦</div>
          <div class="bubble-group">
            <span class="sender-name">Jaryong AI</span>
            <div class="bubble-body loading-state">
              <div class="typing-dots">
                <span></span><span></span><span></span>
              </div>
              <span class="loading-text">데이터 분석 및 응답 생성 중...</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 빠른 질문 추천 -->
      <div v-if="messages.length === 1 && !isLoading" class="quick-prompts">
        <span class="prompt-label">추천 쿼리</span>
        <div class="prompt-tags">
          <button 
            v-for="question in suggestedQuestions" 
            :key="question" 
            type="button" 
            @click="useSuggestion(question)"
          >
            {{ question }} <span class="arrow">→</span>
          </button>
        </div>
      </div>

      <!-- 프롬프트 입력 창 -->
      <form class="composer-container" @submit.prevent="sendMessage">
        <textarea
          v-model="userInput"
          rows="1"
          :disabled="isLoading"
          placeholder="무엇이든 물어보세요... (예: '김철수 사원 자격증 업데이트해줘')"
          @keydown.enter.exact.prevent="sendMessage"
        ></textarea>
        
        <div class="composer-bar">
          <span class="key-hint"><strong>Enter</strong> 전송 · <strong>Shift+Enter</strong> 줄바꿈</span>
          <button 
            class="btn-send" 
            type="submit" 
            :disabled="isLoading || !userInput.trim()" 
            aria-label="전송"
          >
            <span v-if="isLoading" class="spinner"></span>
            <span v-else class="send-icon">↑</span>
          </button>
        </div>
      </form>
    </section>
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue';
import axios from 'axios';
import { marked } from 'marked';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const initialMessage = '안녕하세요, master! 자룡모빌리티의 **AI Copilot**입니다.\n사원 관리, ECU 노드 분석, BMS 셀 로그 검토 및 채용 PDF 검색을 지원합니다.';
const suggestedQuestions = ['현재 ECU 상태 요약해줘', 'CRITICAL BMS 로그 찾아줘', '채용공고 복리후생 알려줘'];
const userInput = ref('');
const isLoading = ref(false);
const messages = ref([{ role: 'ai', text: initialMessage, time: '방금 전' }]);
const chatBox = ref(null);

const renderMarkdown = (text) => {
  if (!text) return '';
  try {
    return marked.parse(text);
  } catch (e) {
    return text;
  }
};

const useSuggestion = (question) => {
  userInput.value = question;
  sendMessage();
};

const clearConversation = () => {
  messages.value = [{ role: 'ai', text: initialMessage, time: '방금 전' }];
};

const sendMessage = async () => {
  const text = userInput.value.trim();
  if (!text || isLoading.value) return;

  messages.value.push({ role: 'user', text, time: '방금 전' });
  userInput.value = '';
  isLoading.value = true;
  await scrollToBottom();

  try {
    const { data } = await axios.post(`${API_BASE_URL}/api/chat`, { message: text });
    messages.value.push({
      role: 'ai',
      text: data.reply || data.answer || '응답을 생성하지 못했습니다.',
      time: '방금 전'
    });
  } catch (error) {
    messages.value.push({
      role: 'ai',
      text: '⚠️ 백엔드 서버 연결에 실패했습니다. (8000번 포트를 확인해주세요)',
      time: '방금 전'
    });
  } finally {
    isLoading.value = false;
    await scrollToBottom();
  }
};

const scrollToBottom = async () => {
  await nextTick();
  if (chatBox.value) {
    chatBox.value.scrollTop = chatBox.value.scrollHeight;
  }
};
</script>

<style scoped>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

/* ==========================================
   글로벌 컨테이너 & 변수 정의
   ========================================== */
.ai-workspace {
  --bg-primary: #0b101d;
  --panel-bg: #131b2e;
  --accent-blue: #4f75ff;
  --accent-purple: #8b5cf6;
  --accent-green: #10b981;
  --text-main: #f1f5f9;
  --text-muted: #94a3b8;
  --border-color: rgba(255, 255, 255, 0.08);

  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 20px;
  width: min(100%, 1240px);
  height: calc(100vh - 40px);
  margin: 0 auto;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  color: var(--text-main);
}

/* ==========================================
   좌측 브랜드 패널 (Intro Panel)
   ========================================== */
.intro-panel {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 32px 26px;
  border-radius: 24px;
  background: radial-gradient(circle at 10% 10%, rgba(79, 117, 255, 0.15), transparent 40%),
              linear-gradient(165deg, #0f172a 0%, #1e1b4b 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
  overflow: hidden;
}

.brand-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  width: fit-content;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 10px #10b981;
}

.brand-tag {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #a5b4fc;
}

.hero-graphic {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 40px auto 20px;
}

.glowing-core {
  position: absolute;
  inset: 25px;
  display: grid;
  place-items: center;
  border-radius: 24px;
  background: linear-gradient(135deg, #4f75ff, #8b5cf6);
  box-shadow: 0 0 40px rgba(139, 92, 246, 0.6);
}

.core-spark {
  font-size: 32px;
  color: #fff;
}

.orbit-ring {
  position: absolute;
  inset: 0;
  border: 1px solid rgba(165, 180, 252, 0.25);
  border-radius: 50%;
}

.ring-1 { transform: rotate(-30deg) scaleY(0.45); }
.ring-2 { transform: rotate(45deg) scaleY(0.65); border-color: rgba(16, 185, 129, 0.3); }

.intro-content .kicker {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.15em;
  color: #818cf8;
  margin-bottom: 8px;
}

.intro-content h1 {
  font-size: 24px;
  font-weight: 800;
  line-height: 1.3;
  margin: 0 0 12px;
}

.gradient-text {
  background: linear-gradient(135deg, #a5b4fc, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.intro-content .desc {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 24px;
}

.capability-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: auto;
}

.cap-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(10px);
}

.cap-icon {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  font-size: 16px;
}

.cap-icon.blue { background: rgba(79, 117, 255, 0.15); color: #818cf8; }
.cap-icon.violet { background: rgba(139, 92, 246, 0.15); color: #c084fc; }
.cap-icon.green { background: rgba(16, 185, 129, 0.15); color: #34d399; }

.cap-info strong { display: block; font-size: 13px; color: #f8fafc; }
.cap-info small { font-size: 11px; color: #64748b; }

.security-footer {
  margin-top: 20px;
  font-size: 11px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 6px;
}
.check-icon { color: #10b981; }

/* ==========================================
   우측 메인 대화 패널 (Chat Panel)
   ========================================== */
.chat-panel {
  display: flex;
  flex-direction: column;
  border-radius: 24px;
  background: var(--panel-bg);
  border: 1px solid var(--border-color);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 28px;
  background: rgba(15, 23, 42, 0.6);
  border-bottom: 1px solid var(--border-color);
}

.agent-profile {
  display: flex;
  align-items: center;
  gap: 14px;
}

.avatar-box {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: linear-gradient(135deg, #4f75ff, #8b5cf6);
  display: grid;
  place-items: center;
  font-size: 20px;
  color: #fff;
  box-shadow: 0 0 20px rgba(79, 117, 255, 0.4);
}

.agent-meta h2 {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 2px;
}

.version-tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 6px;
  background: rgba(129, 140, 248, 0.2);
  color: #a5b4fc;
}

.status-text {
  font-size: 12px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
}

.online-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
}

.btn-clear {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-clear:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

/* 메시지 뷰포트 영역 */
.chat-viewport {
  flex: 1;
  padding: 28px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.timeline-divider {
  display: flex;
  align-items: center;
  gap: 16px;
  color: #475569;
  font-size: 11px;
  font-weight: 600;
}
.timeline-divider::before, .timeline-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.06);
}

.chat-row {
  display: flex;
  gap: 12px;
  max-width: 85%;
}

.chat-row.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.ai-avatar {
  background: linear-gradient(135deg, #4f75ff, #8b5cf6);
  color: #fff;
}

.user-avatar {
  background: #334155;
  color: #cbd5e1;
}

.bubble-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sender-name {
  font-size: 11px;
  color: #64748b;
  font-weight: 600;
}

.bubble-body {
  padding: 14px 18px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.65;
  word-break: break-word;
}

.ai .bubble-body {
  background: rgba(30, 41, 59, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #f1f5f9;
  border-top-left-radius: 4px;
}

.user .bubble-body {
  background: linear-gradient(135deg, #4f75ff, #6366f1);
  color: #fff;
  border-top-right-radius: 4px;
  box-shadow: 0 4px 15px rgba(79, 117, 255, 0.3);
}

.timestamp {
  font-size: 10px;
  color: #475569;
  align-self: flex-end;
  margin-top: 2px;
}

/* 로딩 애니메이션 디자인 */
.loading-state {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #94a3b8;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #818cf8;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 빠른 질문 추천 버튼 */
.quick-prompts {
  padding: 0 28px 16px;
}

.prompt-label {
  display: block;
  font-size: 11px;
  color: #64748b;
  margin-bottom: 8px;
  font-weight: 600;
}

.prompt-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.prompt-tags button {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #cbd5e1;
  padding: 8px 14px;
  border-radius: 12px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.prompt-tags button:hover {
  background: rgba(79, 117, 255, 0.15);
  border-color: #818cf8;
  color: #fff;
}

/* 프롬프트 입력 창 */
.composer-container {
  margin: 0 28px 28px;
  padding: 14px 18px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 18px;
  transition: all 0.2s;
}

.composer-container:focus-within {
  border-color: #818cf8;
  box-shadow: 0 0 25px rgba(99, 102, 241, 0.25);
}

.composer-container textarea {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  color: #f8fafc;
  font-family: inherit;
  font-size: 14px;
  resize: none;
  max-height: 100px;
}

.composer-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.key-hint {
  font-size: 11px;
  color: #475569;
}

.key-hint strong { color: #64748b; }

.btn-send {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #4f75ff;
  border: none;
  color: #fff;
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: all 0.2s;
}

.btn-send:disabled {
  background: #1e293b;
  color: #475569;
  cursor: not-allowed;
}

.btn-send:hover:not(:disabled) {
  background: #6366f1;
  box-shadow: 0 0 15px rgba(79, 117, 255, 0.5);
}

/* Markdown 렌더링 스타일 보정 */
.bubble-body :deep(p) { margin: 0 0 8px; }
.bubble-body :deep(p:last-child) { margin-bottom: 0; }
.bubble-body :deep(pre) {
  background: #0f172a;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.bubble-body :deep(code) {
  font-family: monospace;
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 5px;
  border-radius: 4px;
}
.bubble-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
  font-size: 12px;
}
.bubble-body :deep(th), .bubble-body :deep(td) {
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 6px 10px;
}

/* 스크롤바 모던 커스텀 */
.chat-viewport::-webkit-scrollbar { width: 6px; }
.chat-viewport::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

/* 반응형 모바일 레이아웃 */
@media (max-width: 900px) {
  .ai-workspace {
    grid-template-columns: 1fr;
    height: auto;
  }
  .intro-panel { display: none; }
  .chat-panel { height: calc(100vh - 20px); }
}
</style>