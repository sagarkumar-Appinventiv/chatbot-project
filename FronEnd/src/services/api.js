import axios from 'axios';

const Base_Url = "http://localhost:8000/"

const api = axios.create({
    baseURL : Base_Url,
    headers : {"Content-Type": "application/json"},
});

api.interceptors.request.use((config)=>{
    const token = localStorage.getItem("token");
    if(token){
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// export const signupAPI = (username,email, password) =>{
//     api.post("/auth/signup", {username,email, password});
// }

export const signupAPI = (username, password) =>{
    return api.post("/auth/signup", {username, password});
}

export const loginAPI = (username, password) =>{
    return api.post("/auth/login", {username, password});
}

// Chat management APIs
export const createChatAPI = (title) => {
    return api.post("/chat/new", { title });
}

export const getAllChatsAPI = () => {
    return api.get("/chat/all");
}

export const getMessagesAPI = (chatId) => {
    return api.get(`/chat/${chatId}/messages`);
}

export const sendMessageAPI = (chatId, prompt) => {
    return api.post(`/chat/${chatId}/send`, { prompt });
}

export const deleteChatAPI = (chatId) => {
    return api.delete(`/chat/${chatId}`);
}

export default api;


