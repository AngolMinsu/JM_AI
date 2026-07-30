<template>
  <div class="chat-container">
    <div class="chat-box" ref="chatBox">
      <!-- marked 함수를 활용한 마크다운 렌더링 -->
      <div 
        v-for="(msg, index) in messages" 
        :key="index" 
        :class="['message', msg.role]"
        v-html="renderMarkdown(msg.text)"
      ></div>
    </div>
    
    <div class="input-area">
      <input 
        v-model="userInput" 
        @keyup.enter="sendMessage" 
        placeholder="명령을 입력하세요..." 
      />
      <button @click="sendMessage">전송</button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';
import axios from 'axios';
import { marked } from 'marked';

// .env 환경 변수에서 Base URL 가져오기 (기본값 설정 포함)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const userInput = ref('');
const messages = ref([
  { role: 'ai', text: 'AI 비서가 준비되었습니다. 무엇을 도와드릴까요?' }
]);
const chatBox = ref(null);

// 마크다운 변환 함수
const renderMarkdown = (text) => {
  if (!text) return '';
  return marked.parse(text);
};

const sendMessage = async () => {
  if (!userInput.value.trim()) return;

  const text = userInput.value;
  messages.value.push({ role: 'user', text: text });
  userInput.value = '';

  await scrollToBottom();

  try {
    // 환경 변수 주소 사용
    const res = await axios.post(`${API_BASE_URL}/api/chat`, { 
      message: text 
    });
    
    messages.value.push({ role: 'ai', text: res.data.reply });
  } catch (error) {
    messages.value.push({ role: 'ai', text: '응답을 받아오지 못했습니다.' });
  }

  await scrollToBottom();
};

const scrollToBottom = async () => {
  await nextTick();
  if (chatBox.value) {
    chatBox.value.scrollTop = chatBox.value.scrollHeight;
  }
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 600px;
  width: 100%;
  max-width: 600px;
  border: 1px solid #ccc;
  border-radius: 8px;
  margin: 0 auto;
}
.chat-box {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f9f9f9;
}
.message {
  margin-bottom: 15px;
  padding: 10px 15px;
  border-radius: 8px;
  max-width: 80%;
  line-height: 1.4;
  word-break: break-word;
}
.message.user {
  background-color: #2563eb;
  color: white;
  margin-left: auto;
}
.message.ai {
  background-color: #e5e7eb;
  color: #111;
  margin-right: auto;
}
.input-area {
  display: flex;
  padding: 10px;
  border-top: 1px solid #ccc;
  background: white;
}
.input-area input {
  flex: 1;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.input-area button {
  margin-left: 10px;
  padding: 0 20px;
  background-color: #2563eb;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* 마크다운 스타일링 (v-html 내부) */
.message :deep(p) {
  margin: 0 0 8px 0;
}
.message :deep(p:last-child) {
  margin-bottom: 0;
}

.message :deep(ul), .message :deep(ol) {
  margin: 4px 0 8px 0;
  padding-left: 20px;
}

.message :deep(code) {
  background-color: rgba(0, 0, 0, 0.08);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9em;
}

.message :deep(pre) {
  background-color: #1e293b;
  color: #f8fafc;
  padding: 10px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 8px 0;
}

.message :deep(pre code) {
  background-color: transparent;
  padding: 0;
  color: inherit;
}

.message :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
  font-size: 13px;
}

.message :deep(th), .message :deep(td) {
  border: 1px solid #cbd5e1;
  padding: 6px 8px;
  text-align: left;
}

.message :deep(th) {
  background-color: #d1d5db;
}
</style>