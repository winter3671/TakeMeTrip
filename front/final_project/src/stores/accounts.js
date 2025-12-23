import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAccountStore = defineStore('account', () => {
    const router = useRouter()
    const token = ref(null)
    const user = ref(null)

    const API_URL = 'http://127.0.0.1:8000'

    const signUp = async function(payload) {
        const username = payload.username
        const email = payload.email
        const password1 = payload.password1
        const password2 = payload.password2

        const requestData = {
            username,
            password1,
            password2
        }

        if (email && email.trim() !== '') {
            requestData.email = email
        }

        try {
            const res = await axios({
                method: 'post',
                url: `${API_URL}/api/auth/registration/`,
                data: requestData
            })
            const password = password1
            await logIn({ username, password }) 

        } catch (err) {
            console.log(err)
            throw err 
        }
    }

    const logIn = function (payload) {
        const username = payload.username
        const password = payload.password

        axios({
            method: 'post',
            url: `${API_URL}/api/auth/login`,
            data: {
                username, password
            }
        }).then(res => {
            token.value = res.data.access
            user.value = {
                username: username
            }
            getUserInfo()

            router.push({ name : 'home'})
        }).catch(err => console.log(err))
    }

    const getUserInfo = function () {
        if (!token.value) return

        axios({
            method: 'get',
            url: `${API_URL}/api/auth/user/`,
            headers: {
                Authorization: `Bearer ${token.value}`
            }
        }).then(res => {
            user.value = {
                username: res.data.username
            }
        }).catch(err => {
            console.log('사용자 정보 로드 실패:', err)
            if (err.response?.status === 401) {
                logOut()
            }
        })
    }

    const isLogin = computed(() => {
        return token.value ? true : false
    })

     const logOut = function () {
        token.value = null
        router.push({ name : 'login'})
    }


    return {
        signUp,
        logIn,
        getUserInfo,
        isLogin,
        logOut,
        token,
        user
    }
}, { persist: true })