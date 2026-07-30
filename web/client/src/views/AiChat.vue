<template>
  <div class="chat-container">
    <div class="chat-box" ref="chatBox">
      <div 
        v-for="(msg, index) in messages" 
        :key="index" 
        :class="['message', msg.role]"
      >
        {{ msg.text }}
      </div>
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

const userInput = ref('');
const messages = ref([
  { role: 'ai', text: 'AI 비서가 준비되었습니다. 무엇을 도와드릴까요?' }
]);
const chatBox = ref(null);

const sendMessage = async () => {
  if (!userInput.value.trim()) return;

  const text = userInput.value;
  messages.value.push({ role: 'user', text: text });
  userInput.value = '';

  await scrollToBottom();

  try {
    // Node.js 서버로 통신
    const res = await axios.post('http://localhost:3000/api/chat', { 
      message: text 
    });
    
    messages.value.push({ role: 'ai', text: res.data.answer });
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
</style>