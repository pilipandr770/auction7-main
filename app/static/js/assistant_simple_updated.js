class SimpleAssistant {    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
        this.recordingTimeout = null;
        this.audioChunks = [];
        this.isExpanded = false;
        this.isEnabled = true;
        this.audioResponses = true; // Enable audio responses by default
        
        // Діагностична інформація
        console.log('Simple Assistant initialized');
        console.log('Location protocol:', location.protocol);
        console.log('User agent:', navigator.userAgent);
        console.log('MediaDevices support:', !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia));
        console.log('Legacy getUserMedia support:', !!(navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia));
        console.log('MediaRecorder support:', typeof MediaRecorder !== 'undefined');
        
        this.createWidget();
        this.bindEvents();
        this.checkMicrophonePermission();
    }
    
    createWidget() {
        // Create main widget container
        this.widget = document.createElement('div');
        this.widget.id = 'simple-assistant-widget';
        this.widget.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
        `;
        
        // Create toggle button
        this.toggleBtn = document.createElement('button');
        this.toggleBtn.innerHTML = '🤖';
        this.toggleBtn.style.cssText = `
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #ff6b35, #f7931e);
            border: none;
            font-size: 28px;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(255, 107, 53, 0.4);
            transition: all 0.3s ease;
            position: relative;
            z-index: 1001;
        `;
        
        // Create chat container
        this.chatContainer = document.createElement('div');
        this.chatContainer.style.cssText = `
            position: absolute;
            bottom: 70px;
            right: 0;
            width: 350px;
            max-width: calc(100vw - 40px);
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            display: none;
            flex-direction: column;
            max-height: 500px;
            overflow: hidden;
            border: 1px solid #e0e0e0;
        `;
        
        // Create header
        this.createHeader();
        
        // Create messages area
        this.messagesArea = document.createElement('div');
        this.messagesArea.style.cssText = `
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            max-height: 300px;
            border-bottom: 1px solid #f0f0f0;
        `;        // Add welcome message
        this.addMessage('Привіт! Я AI-асистент. Можу допомогти вам з будь-якими питаннями про аукціон.', 'assistant');
        
        // Add microphone test button in messages
        setTimeout(() => {
            this.addMicrophoneTestMessage();
        }, 1000);
        
        // Create input area
        this.createInputArea();
        
        // Assemble widget
        this.chatContainer.appendChild(this.header);
        this.chatContainer.appendChild(this.messagesArea);
        this.chatContainer.appendChild(this.inputArea);
        
        this.widget.appendChild(this.toggleBtn);
        this.widget.appendChild(this.chatContainer);
        
        document.body.appendChild(this.widget);
    }
    
    createHeader() {
        this.header = document.createElement('div');
        this.header.style.cssText = `
            background: linear-gradient(135deg, #ff6b35, #f7931e);
            color: white;
            padding: 15px;
            border-radius: 15px 15px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
        `;
        
        const title = document.createElement('span');
        title.textContent = 'AI Асистент';
        
        const controls = document.createElement('div');
        controls.style.cssText = 'display: flex; gap: 10px; align-items: center;';
          // Audio toggle button
        this.audioToggle = document.createElement('button');
        this.audioToggle.innerHTML = '🔊';
        this.audioToggle.style.cssText = `
            background: rgba(255,255,255,0.2);
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            cursor: pointer;
            font-size: 14px;
        `;
        this.audioToggle.title = 'Вимкнути/увімкнути звук';
        
        // Microphone permission button
        this.micPermissionBtn = document.createElement('button');
        this.micPermissionBtn.innerHTML = '🎤';
        this.micPermissionBtn.style.cssText = `
            background: rgba(255,255,255,0.2);
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            cursor: pointer;
            font-size: 14px;
        `;
        this.micPermissionBtn.title = 'Дозволити доступ до мікрофона';
        
        // Resize button
        this.resizeBtn = document.createElement('button');
        this.resizeBtn.innerHTML = '↕️';
        this.resizeBtn.style.cssText = `
            background: rgba(255,255,255,0.2);
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            cursor: pointer;
            font-size: 14px;
        `;
        this.resizeBtn.title = 'Змінити розмір';
        
        // Close button
        this.closeBtn = document.createElement('button');
        this.closeBtn.innerHTML = '×';
        this.closeBtn.style.cssText = `
            background: rgba(255,255,255,0.2);
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            cursor: pointer;
            font-size: 18px;
            font-weight: bold;
        `;
        
        controls.appendChild(this.audioToggle);
        controls.appendChild(this.micPermissionBtn);
        controls.appendChild(this.resizeBtn);
        controls.appendChild(this.closeBtn);
        
        this.header.appendChild(title);
        this.header.appendChild(controls);
    }
    
    createInputArea() {
        this.inputArea = document.createElement('div');
        this.inputArea.style.cssText = `
            padding: 15px;
            background: #f8f9fa;
            border-radius: 0 0 15px 15px;
        `;
        
        // Recording status
        this.recordingStatus = document.createElement('div');
        this.recordingStatus.style.cssText = `
            text-align: center;
            color: #dc3545;
            font-weight: bold;
            margin-bottom: 10px;
            display: none;
            font-size: 14px;
        `;
        this.recordingStatus.innerHTML = '🎙️ Запис... Говоріть зараз';
        
        // Input container
        const inputContainer = document.createElement('div');
        inputContainer.style.cssText = `
            display: flex;
            gap: 10px;
            align-items: center;
        `;
        
        // Text input
        this.textInput = document.createElement('input');
        this.textInput.type = 'text';
        this.textInput.placeholder = 'Введіть запитання...';
        this.textInput.style.cssText = `
            flex: 1;
            border: 1px solid #ddd;
            border-radius: 25px;
            padding: 10px 15px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s ease;
        `;
        
        // Voice button
        this.voiceBtn = document.createElement('button');
        this.voiceBtn.innerHTML = '🎤';
        this.voiceBtn.style.cssText = `
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #ff6b35, #f7931e);
            border: none;
            color: white;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        // Send button
        this.sendBtn = document.createElement('button');
        this.sendBtn.innerHTML = '➤';
        this.sendBtn.style.cssText = `
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #ff6b35, #f7931e);
            border: none;
            color: white;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        inputContainer.appendChild(this.textInput);
        inputContainer.appendChild(this.voiceBtn);
        inputContainer.appendChild(this.sendBtn);
        
        this.inputArea.appendChild(this.recordingStatus);
        this.inputArea.appendChild(inputContainer);
    }
    
    bindEvents() {
        // Toggle chat
        this.toggleBtn.addEventListener('click', () => this.toggleChat());
        this.closeBtn.addEventListener('click', () => this.toggleChat());
          // Audio toggle
        this.audioToggle.addEventListener('click', () => {
            this.audioResponses = !this.audioResponses;
            this.audioToggle.innerHTML = this.audioResponses ? '🔊' : '🔇';
            this.audioToggle.style.opacity = this.audioResponses ? '1' : '0.6';
        });
        
        // Microphone permission request
        this.micPermissionBtn.addEventListener('click', async () => {
            await this.requestMicrophonePermission();
        });
        
        // Resize
        this.resizeBtn.addEventListener('click', () => this.toggleSize());
        
        // Send message
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Voice recording
        this.voiceBtn.addEventListener('mousedown', () => this.startRecording());
        this.voiceBtn.addEventListener('mouseup', () => this.stopRecording());
        this.voiceBtn.addEventListener('mouseleave', () => this.stopRecording());
        
        // Touch events for mobile
        this.voiceBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });
        this.voiceBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopRecording();
        });
        
        // Hover effects
        this.toggleBtn.addEventListener('mouseenter', () => {
            this.toggleBtn.style.transform = 'scale(1.1)';
        });
        this.toggleBtn.addEventListener('mouseleave', () => {
            this.toggleBtn.style.transform = 'scale(1)';
        });
    }
    
    toggleChat() {
        this.isExpanded = !this.isExpanded;
        this.chatContainer.style.display = this.isExpanded ? 'flex' : 'none';
        
        if (this.isExpanded) {
            this.toggleBtn.style.transform = 'rotate(180deg)';
            this.textInput.focus();
        } else {
            this.toggleBtn.style.transform = 'rotate(0deg)';
        }
    }
    
    toggleSize() {
        const currentWidth = parseInt(this.chatContainer.style.width);
        const newWidth = currentWidth === 350 ? 450 : 350;
        const newHeight = currentWidth === 350 ? 600 : 500;
        
        this.chatContainer.style.width = newWidth + 'px';
        this.chatContainer.style.maxHeight = newHeight + 'px';
        this.messagesArea.style.maxHeight = (newHeight - 200) + 'px';
    }
      addMicrophoneTestMessage() {
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            margin-bottom: 15px;
            display: flex;
            justify-content: flex-start;
        `;
        
        const messageBubble = document.createElement('div');
        messageBubble.style.cssText = `
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.4;
            word-wrap: break-word;
            background: #f1f3f5;
            color: #333;
            border-bottom-left-radius: 4px;
            border: 1px solid #e9ecef;
        `;
        
        // Додаємо інформацію про протокол
        const protocolWarning = location.protocol === 'http:' ? 
            '<br><small style="color: #856404;">⚠️ Увага: сайт відкритий по HTTP. Для кращої роботи мікрофона використовуйте HTTPS.</small>' : '';
        
        messageBubble.innerHTML = `
            🎤 Для голосових повідомлень натисніть і тримайте кнопку мікрофона знизу.${protocolWarning}<br>
            <button id="test-mic-btn" style="
                background: linear-gradient(135deg, #ff6b35, #f7931e);
                color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 16px;
                margin-top: 8px;
                cursor: pointer;
                font-size: 12px;
            ">🎤 Тест мікрофона</button>
        `;
        
        messageDiv.appendChild(messageBubble);
        this.messagesArea.appendChild(messageDiv);
        
        // Add test button functionality
        const testBtn = document.getElementById('test-mic-btn');
        if (testBtn) {
            testBtn.addEventListener('click', () => {
                this.testMicrophone();
            });
        }
        
        // Auto scroll to bottom
        this.messagesArea.scrollTop = this.messagesArea.scrollHeight;
    }
      async testMicrophone() {
        console.log('Testing microphone access...');
        console.log('navigator:', typeof navigator);
        console.log('navigator.mediaDevices:', navigator.mediaDevices);
        console.log('navigator.getUserMedia:', navigator.getUserMedia);
        console.log('location.protocol:', location.protocol);
        
        // Перевіряємо всі можливі варіанти доступу до мікрофона
        const getUserMedia = this.getGetUserMedia();
        
        if (!getUserMedia) {
            this.addMessage('❌ Ваш браузер не підтримує доступ до мікрофона. Спробуйте:\n• Оновити браузер до останньої версії\n• Використати Chrome, Firefox або Edge\n• Відкрити сайт по HTTPS', 'assistant');
            return;
        }
        
        try {
            console.log('Requesting microphone access with getUserMedia...');
            
            const stream = await new Promise((resolve, reject) => {
                getUserMedia.call(navigator, 
                    { audio: true },
                    resolve,
                    reject
                );
            });
            
            console.log('Microphone access granted!');
            stream.getTracks().forEach(track => track.stop());
            
            this.addMessage('✅ Мікрофон працює! Тепер ви можете використовувати голосові повідомлення.', 'assistant');
            this.voiceBtn.style.opacity = '1';
            this.voiceBtn.title = 'Натисніть і тримайте для запису';
            
        } catch (error) {
            console.error('Microphone test failed:', error);
            
            let errorMessage = '❌ Тест мікрофона не пройшов. ';
            
            if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
                errorMessage += 'Доступ заборонено. Натисніть на іконку 🔒 в адресному рядку та дозвольте мікрофон.';
            } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
                errorMessage += 'Мікрофон не знайдено. Перевірте підключення мікрофона.';
            } else if (error.name === 'NotSupportedError') {
                errorMessage += 'Браузер не підтримує доступ до мікрофона. Використайте HTTPS або новіший браузер.';
            } else {
                errorMessage += `Помилка: ${error.message || error}`;
            }
            
            // Додаткові поради
            if (location.protocol === 'http:') {
                errorMessage += '\n\n💡 Спробуйте відкрити сайт по HTTPS для кращої підтримки мікрофона.';
            }
            
            this.addMessage(errorMessage, 'assistant');
        }
    }
    
    // Функція для отримання getUserMedia в різних браузерах
    getGetUserMedia() {
        console.log('Checking getUserMedia support...');
        
        // Сучасний спосіб
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            console.log('Using modern navigator.mediaDevices.getUserMedia');
            return function(constraints, success, error) {
                navigator.mediaDevices.getUserMedia(constraints)
                    .then(success)
                    .catch(error);
            };
        }
        
        // Старі браузери
        const getUserMedia = navigator.getUserMedia || 
                           navigator.webkitGetUserMedia || 
                           navigator.mozGetUserMedia || 
                           navigator.msGetUserMedia;
        
        if (getUserMedia) {
            console.log('Using legacy getUserMedia');
            return getUserMedia;
        }
        
        console.log('No getUserMedia support found');
        return null;
    }
    
    addMessage(content, sender = 'user') {
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            margin-bottom: 15px;
            display: flex;
            ${sender === 'user' ? 'justify-content: flex-end;' : 'justify-content: flex-start;'}
        `;
        
        const messageBubble = document.createElement('div');
        messageBubble.style.cssText = `
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.4;
            word-wrap: break-word;
            ${sender === 'user' 
                ? 'background: linear-gradient(135deg, #ff6b35, #f7931e); color: white; border-bottom-right-radius: 4px;'
                : 'background: #f1f3f5; color: #333; border-bottom-left-radius: 4px; border: 1px solid #e9ecef;'
            }
        `;
        
        messageBubble.textContent = content;
        messageDiv.appendChild(messageBubble);
        this.messagesArea.appendChild(messageDiv);
        
        // Auto scroll to bottom
        this.messagesArea.scrollTop = this.messagesArea.scrollHeight;
    }
    
    async sendMessage() {
        const message = this.textInput.value.trim();
        if (!message) return;
        
        this.textInput.value = '';
        this.addMessage(message, 'user');
        this.showTyping();
        
        try {
            const response = await fetch('/assistant/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    page: window.location.pathname,
                    lang: document.documentElement.lang || 'uk'
                })
            });
            
            const data = await response.json();
            this.hideTyping();
            
            if (data.response) {
                this.addMessage(data.response, 'assistant');
                
                // Play audio response if enabled
                if (this.audioResponses && data.audio_url) {
                    this.playAudioResponse(data.audio_url);
                }
            } else {
                this.addMessage('Вибачте, сталася помилка. Спробуйте ще раз.', 'assistant');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTyping();
            this.addMessage('Помилка з\'єднання. Перевірте інтернет-з\'єднання.', 'assistant');
        }
    }
    
    showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.style.cssText = `
            margin-bottom: 15px;
            display: flex;
            justify-content: flex-start;
        `;
        
        const typingBubble = document.createElement('div');
        typingBubble.style.cssText = `
            background: #f1f3f5;
            color: #666;
            padding: 12px 16px;
            border-radius: 18px;
            border-bottom-left-radius: 4px;
            font-size: 14px;
            border: 1px solid #e9ecef;
        `;
        
        typingBubble.innerHTML = '⭯ Друкую...';
        typingDiv.appendChild(typingBubble);
        this.messagesArea.appendChild(typingDiv);
        this.messagesArea.scrollTop = this.messagesArea.scrollHeight;
    }
    
    hideTyping() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }    async requestMicrophonePermission() {
        try {
            console.log('Manually requesting microphone permission...');
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(track => track.stop());
            
            this.voiceBtn.style.opacity = '1';
            this.voiceBtn.title = 'Натисніть і тримайте для запису';
            this.micPermissionBtn.style.display = 'none';
            
            this.addMessage('✅ Доступ до мікрофона дозволено! Тепер ви можете використовувати голосові повідомлення.', 'assistant');
        } catch (error) {
            console.error('Permission request failed:', error);
            
            let errorMessage = 'Не вдалося отримати доступ до мікрофона. ';
            
            if (error.name === 'NotAllowedError') {
                errorMessage += 'Натисніть на іконку 🔒 біля адресного рядка та дозвольте доступ до мікрофона для цього сайту.';
            } else {
                errorMessage += 'Перевірте, чи підключений мікрофон та чи не використовується іншими програмами.';
            }
            
            this.addMessage(errorMessage, 'assistant');
        }
    }    async checkMicrophonePermission() {
        const getUserMedia = this.getGetUserMedia();
        
        if (!getUserMedia) {
            console.warn('No getUserMedia support found');
            this.voiceBtn.style.opacity = '0.5';
            this.voiceBtn.title = 'Мікрофон не підтримується браузером';
            this.micPermissionBtn.style.display = 'none';
            return;
        }

        // Для всіх інших випадків показуємо кнопку як доступну
        this.voiceBtn.style.opacity = '1';
        this.voiceBtn.title = 'Натисніть і тримайте для запису';
        this.micPermissionBtn.style.display = 'none';
        
        console.log('Microphone appears to be supported');
    }async startRecording() {
        if (this.isRecording) return;
        
        console.log('Attempting to start recording...');
        
        const getUserMedia = this.getGetUserMedia();
        
        if (!getUserMedia) {
            console.error('getUserMedia not supported');
            this.addMessage('Ваш браузер не підтримує запис аудіо. Спробуйте:\n• Оновити браузер\n• Використати Chrome, Firefox або Edge\n• Відкрити сайт по HTTPS', 'assistant');
            return;
        }
        
        // Перевіряємо MediaRecorder окремо
        if (typeof MediaRecorder === 'undefined') {
            console.error('MediaRecorder not supported');
            this.addMessage('Запис аудіо не підтримується вашим браузером. Оновіть браузер до останньої версії.', 'assistant');
            return;
        }
        
        try {
            console.log('Requesting microphone access...');
            
            // Отримуємо доступ до мікрофона
            const stream = await new Promise((resolve, reject) => {
                getUserMedia.call(navigator, 
                    { audio: true },
                    resolve,
                    reject
                );
            });
            
            console.log('Microphone access granted, starting recording...');
            
            // Створюємо MediaRecorder з найпростішими налаштуваннями
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                    console.log('Audio chunk received:', event.data.size, 'bytes');
                }
            };
            
            this.mediaRecorder.onstop = () => {
                console.log('Recording stopped, processing audio...');
                const audioBlob = new Blob(this.audioChunks, { 
                    type: 'audio/wav'
                });
                console.log('Audio blob created:', audioBlob.size, 'bytes');
                this.sendVoiceMessage(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };
            
            this.mediaRecorder.onerror = (event) => {
                console.error('MediaRecorder error:', event.error);
                this.addMessage('Помилка запису аудіо. Спробуйте ще раз.', 'assistant');
                this.resetRecordingState();
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            
            console.log('Recording started successfully');
            
            // Visual feedback
            this.voiceBtn.style.background = '#dc3545';
            this.voiceBtn.innerHTML = '⏹️';
            this.voiceBtn.title = 'Відпустіть щоб зупинити запис';
            this.recordingStatus.style.display = 'block';
            
            // Auto-stop after 30 seconds
            this.recordingTimeout = setTimeout(() => {
                console.log('Auto-stopping recording after 30 seconds');
                this.stopRecording();
            }, 30000);
            
        } catch (error) {
            console.error('Error starting recording:', error);
            
            // Детальні повідомлення про помилки
            let errorMessage = 'Помилка доступу до мікрофона. ';
            
            if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
                errorMessage += 'Натисніть на іконку 🔒 в адресному рядку браузера та дозвольте доступ до мікрофона для цього сайту.';
            } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
                errorMessage += 'Мікрофон не знайдено. Перевірте, чи підключений мікрофон до комп\'ютера.';
            } else if (error.name === 'NotReadableError') {
                errorMessage += 'Мікрофон зайнятий іншим додатком. Закрийте інші програми що використовують мікрофон.';
            } else if (error.name === 'OverconstrainedError') {
                errorMessage += 'Налаштування мікрофона не підходять. Спробуйте ще раз.';
            } else if (error.name === 'NotSupportedError') {
                errorMessage += 'Браузер не підтримує доступ до мікрофона. Використайте HTTPS або новіший браузер.';
            } else {
                errorMessage += `Невідома помилка: ${error.message || error}. Спробуйте перезавантажити сторінку.`;
            }
            
            // Додаткові поради для HTTP
            if (location.protocol === 'http:') {
                errorMessage += '\n\n💡 Спробуйте відкрити сайт по HTTPS для кращої підтримки мікрофона.';
            }
            
            this.addMessage(errorMessage, 'assistant');
            this.resetRecordingState();
        }
    }
    
    resetRecordingState() {
        this.isRecording = false;
        this.voiceBtn.style.background = 'linear-gradient(135deg, #ff6b35, #f7931e)';
        this.voiceBtn.innerHTML = '🎤';
        this.voiceBtn.title = 'Натисніть і тримайте для запису';
        this.recordingStatus.style.display = 'none';
        
        if (this.recordingTimeout) {
            clearTimeout(this.recordingTimeout);
            this.recordingTimeout = null;
        }
    }
      stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) return;
        
        console.log('Stopping recording...');
        
        try {
            if (this.mediaRecorder.state === 'recording') {
                this.mediaRecorder.stop();
            }
        } catch (error) {
            console.error('Error stopping recording:', error);
        }
        
        this.resetRecordingState();
    }
      async sendVoiceMessage(audioBlob) {
        this.addMessage('🎙️ Голосове повідомлення', 'user');
        this.showTyping();
        
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'voice_message.wav');
            formData.append('page', window.location.pathname);
            formData.append('lang', document.documentElement.lang || 'uk');
            
            console.log('Sending voice message to server...');
            
            const response = await fetch('/assistant/voice', {
                method: 'POST',
                body: formData
            });
            
            console.log('Server response status:', response.status);
            
            const data = await response.json();
            console.log('Server response data:', data);
            
            this.hideTyping();
            
            if (data.transcribed_text || data.transcription) {
                // Show what was transcribed
                const transcription = data.transcribed_text || data.transcription;
                this.addMessage(`📝 "${transcription}"`, 'user');
            }
            
            if (data.response) {
                this.addMessage(data.response, 'assistant');
                
                // Play audio response if enabled
                if (this.audioResponses && (data.audio_url || data.audio)) {
                    const audioUrl = data.audio_url || data.audio;
                    this.playAudioResponse(audioUrl);
                }
            } else if (data.error) {
                this.addMessage(`❌ ${data.error}`, 'assistant');
            } else {
                this.addMessage('Вибачте, не вдалося обробити голосове повідомлення.', 'assistant');
            }
        } catch (error) {
            console.error('Error sending voice message:', error);
            this.hideTyping();
            this.addMessage('Помилка відправки голосового повідомлення. Перевірте інтернет-з\'єднання.', 'assistant');
        }
    }
    
    playAudioResponse(audioUrl) {
        if (!this.audioResponses) return;
        
        const audio = new Audio(audioUrl);
        audio.play().catch(error => {
            console.warn('Could not play audio response:', error);
        });
    }
}

// Initialize assistant when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new SimpleAssistant();
});
