document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.querySelector('input[placeholder="Type your message..."]');
    const sendButton = document.getElementById('submitButton');
    const chatContainer = document.querySelector('.layout-content-container');
    const uploadButton = document.getElementById('uploadButton');
    const fileInput = document.getElementById('documentUpload');
    let originalButtonHTML = uploadButton.innerHTML;

    if (!sendButton) console.error('Submit button not found!');
    if (!chatInput) console.error('Chat input not found!');
    if (!chatContainer) console.error('Chat container not found!');
    if (!uploadButton) console.error('Upload button not found!');
    if (!fileInput) console.error('File input not found!');

    sendButton.addEventListener('click', handleSendMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    uploadButton.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', async function(e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            console.log('File selected:', file.name);
            try {
                uploadButton.innerHTML = `
                    <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>`;
                uploadButton.disabled = true;

                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch('/load_faiss', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();

                if (response.ok) {
                    addMessageToChat('bot', `Document "${file.name}" loaded successfully!`);
                } else {
                    throw new Error(result.message || 'Failed to load document');
                }
            } catch (error) {
                console.error('Error uploading file:', error);
                addMessageToChat('bot', `Error: ${error.message}`);
            } finally {
                fileInput.value = '';
                uploadButton.innerHTML = originalButtonHTML;
                uploadButton.disabled = false;
            }
        }
    });

    async function handleSendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        addMessageToChat('user', message);
        chatInput.value = '';

        try {
            const typingIndicator = addTypingIndicator();
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            chatContainer.removeChild(typingIndicator);

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            addMessageToChat('bot', data.response || 'Sorry, I encountered an error processing your request.');
        } catch (error) {
            console.error('Error:', error);
            const typingIndicator = document.querySelector('.typing-indicator');
            if (typingIndicator) chatContainer.removeChild(typingIndicator);
            addMessageToChat('bot', 'Sorry, I encountered an error. Please try again.');
        }
    }

    function addMessageToChat(sender, message) {
        const messageContainer = document.createElement('div');
        messageContainer.className = `flex items-end gap-3 p-4 ${sender === 'user' ? 'justify-end' : ''}`;

        if (sender === 'bot') {
            let faqList = null;
            if (typeof message === 'string') {
                try {
                    const parsed = JSON.parse(message);
                    if (Array.isArray(parsed) && parsed[0]?.question && parsed[0]?.answer) {
                        faqList = parsed;
                    }
                } catch {}
            } else if (Array.isArray(message) && message[0]?.question && message[0]?.answer) {
                faqList = message;
            }

            if (faqList) {
                const leftCol = document.createElement('div');
                leftCol.className = "bg-center bg-no-repeat aspect-square bg-cover rounded-full w-10 h-10 flex-shrink-0";
                leftCol.style.backgroundImage = "url('https://lh3.googleusercontent.com/aida-public/AB6AXuB6fqyw15tcMHhUy2uW9F4SBl4yvd65dTaJovlV0Hxp7UpczLZnmJMoAMnF_PVWzcfyTZO3sOiqJqKtOO87Sw1uDnVaLF3na-2F1ZIhvkiHjw2pTKaigvu3Ahwmhh_adSScQ3DW1hIOxGSZDmfkSiZJYLWcOImsnI6JWWmaBgn22ZFIMfLHVR326XS1GOADCEk4XyqcgO7CFBH_UGsyjhByJMufIx9UBLqqsbABpmdIXqp5oysB05kA-2OnDv_qrqvt_k_bccmEMjIW')";
                
                const faqContainer = document.createElement('div');
                faqContainer.className = "flex-1 min-w-0";

                const label = document.createElement('p');
                label.className = "text-[#adadad] text-[13px] font-normal mb-1";
                label.textContent = "Support";

                const faqItemsContainer = document.createElement('div');
                faqItemsContainer.className = "flex flex-col gap-2";

                faqList.forEach(faq => {
                    const faqItem = document.createElement('div');
                    faqItem.className = 'faq-item text-white bg-[#363636] p-3 rounded-xl';

                    const formattedAnswer = faq.answer
                        .replace(/\n\s*\n/g, '<br><br>')
                        .replace(/\n/g, ' ');

                    faqItem.innerHTML = `
                        <div class="faq-question flex justify-between items-center cursor-pointer">
                            <span class="truncate">${faq.question}</span>
                            <svg class="faq-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="6 9 12 15 18 9"></polyline>
                            </svg>
                        </div>
                        <div class="faq-answer text-white" style="display: none;">
                            <span>${formattedAnswer}</span>
                        </div>
                    `;

                    const questionEl = faqItem.querySelector('.faq-question');
                    const answerEl   = faqItem.querySelector('.faq-answer');
                    const chevronEl  = faqItem.querySelector('.faq-chevron');

                    questionEl.addEventListener('click', () => {
                        const isOpen = faqItem.classList.toggle('active');
                        answerEl.style.display = isOpen ? 'block' : 'none';
                        chevronEl.classList.toggle('rotated', isOpen);
                    });

                    faqItemsContainer.appendChild(faqItem);
                });
                // Removed auto-expand logic; all answers are hidden by default.

                faqContainer.appendChild(label);
                faqContainer.appendChild(faqItemsContainer);
                messageContainer.appendChild(leftCol);
                messageContainer.appendChild(faqContainer);
            } else {
                // regular bot text
                messageContainer.innerHTML = `
                    <div class="bg-center bg-no-repeat aspect-square bg-cover rounded-full w-10 shrink-0" 
                         style='background-image: url("https://lh3.googleusercontent.com/aida-public/AB6AXuB6fqyw15tcMHhUy2uW9F4SBl4yvd65dTaJovlV0Hxp7UpczLZnmJMoAMnF_PVWzcfyTZO3sOiqJqKtOO87Sw1uDnVaLF3na-2F1ZIhvkiHjw2pTKaigvu3Ahwmhh_adSScQ3DW1hIOxGSZDmfkSiZJYLWcOImsnI6JWWmaBgn22ZFIMfLHVR326XS1GOADCEk4XyqcgO7CFBH_UGsyjhByJMufIx9UBLqqsbABpmdIXqp5oysB05kA-2OnDv_qrqvt_k_bccmEMjIW");'>
                    </div>
                    <div class="flex flex-1 flex-col gap-1 items-start">
                        <p class="text-[#adadad] text-[13px] font-normal leading-normal max-w-[360px]">Support</p>
                        <p class="text-base font-normal leading-normal flex max-w-[360px] rounded-xl px-4 py-3 bg-[#363636] text-white">
                            ${message}
                        </p>
                    </div>`;
            }
        } else {
            // user text
            messageContainer.innerHTML = `
                <div class="flex flex-1 flex-col gap-1 items-end">
                    <p class="text-[#adadad] text-[13px] font-normal leading-normal max-w-[360px] text-right">User</p>
                    <p class="text-base font-normal leading-normal flex max-w-[360px] rounded-xl px-4 py-3 bg-black text-white">
                        ${message}
                    </p>
                </div>
                <div class="bg-center bg-no-repeat aspect-square bg-cover rounded-full w-10 shrink-0" 
                     style='background-image: url("https://lh3.googleusercontent.com/aida-public/AB6AXuCeMmg03CXEvJe7wbCxwvAQpGY6xoCZtEOIuszYHnbaHGGrXABvheMe_tVkaHeTpDM40jHPiEsjjzYywJFlrezb9btziL5Cn7tAJbag7S-E3FHuOrQuclfOrDxmWynYoAMBESMfE24UjkVrpiNQdkmcTnLy2qV7h2XytuXacHncQKKpKol1H15KNBa50l2khyM4KZOpceD_dceRdJJysCrjrNuPOD_0m49yTg7LBuUOhw6OQ1eA9ourPF19FKLdZvpesrsKMoswbdYt");'>
                </div>`;
        }

        chatContainer.insertBefore(messageContainer, document.querySelector('.flex.items-center.px-4.py-3'));
        messageContainer.scrollIntoView({ behavior: 'smooth' });
    }

    function addTypingIndicator() {
        const typingContainer = document.createElement('div');
        typingContainer.className = 'flex items-end gap-3 p-4 typing-indicator';
        typingContainer.innerHTML = `
            <div class="bg-center bg-no-repeat aspect-square bg-cover rounded-full w-10 shrink-0" 
                 style='background-image: url("https://lh3.googleusercontent.com/aida-public/AB6AXuB6fqyw15tcMHhUy2uW9F4SBl4yvd65dTaJovlV0Hxp7UpczLZnmJMoAMnF_PVWzcfyTZO3sOiqJqKtOO87Sw1uDnVaLF3na-2F1ZIhvkiHjw2pTKaigvu3Ahwmhh_adSScQ3DW1hIOxGSZDmfkSiZJYLWcOImsnI6JWWmaBgn22ZFIMfLHVR326XS1GOADCEk4XyqcgO7CFBH_UGsyjhByJMufIx9UBLqqsbABpmdIXqp5oysB05kA-2OnDv_qrqvt_k_bccmEMjIW");'>
            </div>
            <div class="flex flex-1 flex-col gap-1 items-start">
                <p class="text-[#adadad] text-[13px] font-normal leading-normal max-w-[360px]">Support</p>
                <div class="flex space-x-2">
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                </div>
            </div>`;
        
        chatContainer.insertBefore(typingContainer, document.querySelector('.flex.items-center.px-4.py-3'));
        typingContainer.scrollIntoView({ behavior: 'smooth' });
        return typingContainer;
    }
});
