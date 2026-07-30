import { createRouter, createWebHistory } from 'vue-router'
// 방금 만든 페이지들을 불러옴
import Home from '../views/Home.vue'
import AiChat from '../views/AiChat.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/ai-chat',
    name: 'AiChat',
    component: AiChat
  }
]

const router = createRouter({
  // 브라우저의 뒤로가기/앞으로가기가 자연스럽게 동작하도록 HTML5 History 모드 사용
  history: createWebHistory(),
  routes
})

export default router