<template>
    <div>
        <el-container style="height: 630px; border: 1px solid #eee;">
            <!-- 侧边栏 -->
            <el-aside v-if="showSidebar" style="display: flex; flex-direction: column; height: 100%; width: 200px; border-right: 0.2px solid #ccc;">
                <!-- 添加对话按钮区域 -->
                <div style="padding: 10px; display: flex; justify-content: center; align-items: center; border-bottom: 1px solid #ccc;">
                    <el-button @click="addConversation">创建新对话</el-button>
                </div>
                <!-- 对话列表区域 -->
                <div style="padding: 10px;flex-grow: 1; overflow-y: auto; display: flex; flex-direction: column;">
                    <el-button 
                        v-for="(item, index) in conversations"
                        :key="index" 
                        style="margin: 10px 0; width: 100%; height: 40px;"
                        @click="selectConversation(index)"
                    >
                        {{ item }}
                    </el-button>
                </div>
            </el-aside>

            <el-container>
                <el-button @click="toggleSidebar" style="display: flex; align-items: center; justify-content: center; height: 10%; width: 40px;">
                    <span v-if="showSidebar" style="display : flex ;align-items: center;">
                        <i class="el-icon-arrow-left"></i> <!-- 隐藏侧栏 -->
                    </span>
                    <span v-else style="display : flex; align-items: center;">
                        <i class="el-icon-arrow-right"></i> <!-- 显示侧栏 -->
                    </span>
                </el-button>
                
                <el-main style="display: flex; flex-direction: column; height: 90%;">
                    <div v-if="selectedConversationIndex !== null" style="flex-grow: 1; padding: 80px; overflow-y: auto;">
                        <div v-for="(message, index) in conversationContent[selectedConversationIndex]" :key="index" class="message-container">
                            <div :class="{'my-message': message.self, 'AI-message': !message.self}">
                                <img v-if="message.type === 'image'" :src="message.content" style="max-width: 100%;" />
                                <div v-else>
                                    {{ message.content }}
                                </div>
                            </div>
                        </div>
                    </div>
                </el-main>
                
                <el-footer style="display: flex; align-items: center; height: 100px;">
                    <el-input type="textarea" :rows="2" placeholder="请输入内容" v-model="textarea" @keyup.enter.native.prevent="sendQuery" style="flex-grow: 1; margin-right: 10px;">
                    </el-input>
                    <el-button round @click="sendQuery">发送</el-button>
                </el-footer>
            </el-container>
        </el-container>
    </div>
</template>

<script>
import axios from 'axios'
export default {
    data () {
        return {
            textarea: '',
            conversations: [], // 存储对话标识
            conversationContent: [], // 存储每个对话的具体内容
            selectedConversationIndex: null, // 当前选中对话的索引
            showSidebar: true  // 控制侧栏显示和隐藏
        }
    },
    methods: {
        addConversation() {
            const newIndex = this.conversations.length + 1;
            this.conversations.push(`对话 ${newIndex}`);
            this.conversationContent.push([]);
        },
        toggleSidebar() {
            this.showSidebar = !this.showSidebar;
        },
        selectConversation(index) {
            this.selectedConversationIndex = index;
        },
        sendQuery() {
            const messageContent = this.textarea.trim();
            if (messageContent) {
                const newMessage = {
                    self: true, // true 表示用户发送的消息
                    content: messageContent,
                    type: 'text'
                };
                const conversation = this.conversationContent[this.selectedConversationIndex];
                conversation.push(newMessage);

                axios.post('http://127.0.0.1:7000/query', { text: messageContent }, {
                    responseType: 'blob' // 指定响应类型为 blob
                })
                .then(response => {
                    const AIMessage = {
                        self: false, // false 表示 AI 发送的消息
                        content: URL.createObjectURL(response.data),
                        type: 'image'
                    };
                    conversation.push(AIMessage);
                    this.textarea = ''; // 清空输入框
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            } else {
                this.$message.error('请输入内容');
            }
            
        }
    }
}
</script>

<style scoped>
.message-container {
    margin-bottom: 10px;
    display: flex;              /* 使用flexbox布局 */
}

.my-message {
    display: inline-block;
    margin-left: auto;         /* 用户消息框向右扩展 */
    margin-right: 45px;        /* 设置右侧边距 */
    background-color: #dcf8c6; /* 用户消息背景色 */
    border-radius: 10px;
    padding: 10px;             /* 内边距 */
    text-align: left;
    max-width: 89%;            /* 最大宽度 */
    word-wrap: break-word;     /* 允许单词换行 */
}

.AI-message {
    display: inline-block;
    margin-right: auto;        /* AI消息框向左扩展 */
    margin-left: 45px;         /* 设置左侧边距 */
    background-color: #e6e6fa; /* AI消息背景色 */
    border-radius: 10px;
    padding: 10px;             /* 内边距 */
    text-align: left;
    max-width: 89%;            /* 最大宽度 */
    word-wrap: break-word;     /* 允许单词换行 */
}

</style>
