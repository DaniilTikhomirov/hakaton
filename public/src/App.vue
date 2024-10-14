<script setup>
import {ref, computed} from 'vue'
import axios from "axios";


const currentScreen = ref('login')
const selectedStand = ref(null)
const telegramUsername = ref('')
const hasCompletedBotInteraction = ref(false)
const queueHuman = ref(0)
const queueTime = ref(0)

const stands = ref([
  {id: 'A', name: 'Стенд A', queue: 'x', color: 'bg-yellow-400'},
  {id: 'B', name: 'Стенд B', queue: 'y', color: 'bg-yellow-400'},
  {id: 'C', name: 'Стенд C', queue: 'z', color: 'bg-yellow-400'},
])



const botLink = computed(() => {
  return `https://t.me/test_shop_525252bot?start=${encodeURIComponent(telegramUsername.value)}`
})


const registerInQueue = async () => {
  try {
    const response = await axios.post("http://127.0.0.1:8000/queue/add", {
      title: selectedStand.value.name,
      username: telegramUsername.value,
    });
    console.log('Регистрация успешна:', response.data);
    // Обновляем информацию об очереди, если необходимо
    const res = await axios.post('http://127.0.0.1:8000/queue/users/count?title=' + String(selectedStand.value.name));
    const res2 = await axios.post('http://127.0.0.1:8000/queue/users/time?title=' + String(selectedStand.value.name));
    queueHuman.value = res.data;
    queueTime.value = res2.data;
  } catch (error) {
    console.error('Ошибка при регистрации в очередь:', error);
  }
}
  


const selectStand = async (stand) => {
  selectedStand.value = stand
  currentScreen.value = 'confirmation'
  const res = await axios.post('http://127.0.0.1:8000/queue/users/count?title=' + String(selectedStand.value.name))
  const res2 = await axios.post('http://127.0.0.1:8000/queue/users/time?title=' + String(selectedStand.value.name))
  queueHuman.value = res.data
  queueTime.value = res2.data
}

const leaveQueue = async () => {
  await axios.delete('http://127.0.0.1:8000/queue/del')
  selectedStand.value = null

}

const goBack = () => {
  if (currentScreen.value === 'confirmation') {
    currentScreen.value = 'choose-stand'
  } else if (currentScreen.value === 'choose-stand') {
    currentScreen.value = 'login'
    hasCompletedBotInteraction.value = false
  }
}

const login = async () => {
  if (telegramUsername.value.trim()) {
    try {
      const response = await axios.post('http://127.0.0.1:8000/registration?username=' + String(telegramUsername.value));
      console.log('Успешный ответ:', response);
      window.location.href = botLink.value;
    } catch (error) {
      console.error('Ошибка при запросе:', error);
    }
  }
}


const completeBotInteraction = () => {
  hasCompletedBotInteraction.value = true
  currentScreen.value = 'choose-stand'
}
</script>

<template>
  <div class="container mx-auto px-4 py-8 max-w-md">
    <header class="flex justify-between items-center mb-8">
      <br>
      <div class="flex items-center">
        <span class="text-3xl font-bold text-yellow-400">Т-БАНК</span>
      </div>
      <br>
      <button v-if="currentScreen !== 'login'" class="text-gray-600 hover:text-gray-800" @click="goBack">
        {{ currentScreen === 'choose-stand' ? 'Выйти' : 'Назад' }}
      </button>
    </header>

    <main>
      <div v-if="currentScreen === 'login'" class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-2xl font-bold mb-6 text-center">Войти через Telegram</h2>
        <form @submit.prevent="login" class="space-y-4">
          <div>
            <label for="telegramUsername" class="block text-sm font-medium text-gray-700 mb-1">
              Имя пользователя Telegram
            </label>
            <input
                id="telegramUsername"
                v-model="telegramUsername"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400"
                placeholder="Введите ваше имя пользователя"
            />
          </div>
          <a
              :href="botLink"
              class="block w-full bg-yellow-400 hover:bg-yellow-500 text-black font-bold py-2 px-4 rounded transition-colors text-center"
              @click.prevent="login"
          >
            Войти
          </a>
        </form>
        <div v-if="!hasCompletedBotInteraction" class="mt-4">
          <p class="text-sm text-gray-600 text-center">После взаимодействия с ботом, нажмите кнопку ниже:</p>
          <button
              @click="completeBotInteraction"
              class="mt-2 w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded transition-colors"
          >
            Я выполнил действия в боте
          </button>
        </div>
      </div>

      <div v-else-if="currentScreen === 'choose-stand'">
        <h1 class="text-2xl font-bold text-center mb-4">Запишись, чтобы не ждать <br>в очереди</h1>
        <div v-if="hasCompletedBotInteraction" class="space-y-4">
          <div
              v-for="stand in stands"
              :key="stand.id"
              class="bg-white rounded-lg shadow-md p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
              @click="selectStand(stand)"
          >
            <div class="flex items-center">
              <div
                  :class="['w-10 h-10 rounded-full flex items-center justify-center text-black font-bold mr-4', stand.color]">
                <span>{{ stand.id }}</span>
              </div>
              <div>
                <h2 class="text-lg font-semibold">{{ stand.name }}</h2>
                <p class="text-sm text-gray-600">Очередь: {{ stand.queue }} человек</p>
              </div>
            </div>
            <ChevronLeft class="transform rotate-180 text-gray-400"/>
          </div>
        </div>
        <div v-else class="text-center">
          <p class="text-lg text-gray-800 mb-4">Пожалуйста, завершите взаимодействие с ботом, чтобы выбрать стенд.</p>
          <button
              @click="currentScreen = 'login'"
              class="bg-yellow-400 hover:bg-yellow-500 text-black font-bold py-2 px-4 rounded transition-colors"
          >
            Вернуться к входу
          </button>
        </div>
      </div>

      <div v-else-if="currentScreen === 'confirmation'" class="bg-white rounded-lg shadow-md p-6">
        <button @click="goBack" class="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded transition-colors">
          <ChevronLeft class="mr-1 flex items-center"/>
          Выйти
        </button>
        <h2 class="text-2xl font-bold mb-6">Вы записаны на {{ selectedStand?.name }}</h2>
        <div class="flex justify-between mb-6">
          <div class="text-center">
            <p class="text-3xl font-bold text-yellow-400">{{ queueHuman }}</p>
            <p class="text-sm text-gray-600">человек перед вами</p>
          </div>
          <div class="text-center">
            <p class="text-3xl font-bold text-yellow-400">{{ queueTime }}</p>
            <p class="text-sm text-gray-600">минут ожидания</p>
          </div>
        </div>
        <div class="space-y-2">
          <button
              class="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded transition-colors">
            Пропустить человека вперед
          </button>
          <button
              class="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded transition-colors" @click="leaveQueue">
            Отменить запись
          </button>
          <button
              class="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded transition-colors"
              @click="registerInQueue">
            Зарегистрироваться в очередь   
          </button>
        </div>
      </div>
    </main>
  </div>
</template>