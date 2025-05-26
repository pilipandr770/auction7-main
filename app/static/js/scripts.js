// Universal Web3 Wallet Integration
async function connectWallet() {
    // Detect available wallet providers
    let provider = null;
    let walletType = '';
    
    // Check for MetaMask
    if (window.ethereum && window.ethereum.isMetaMask) {
        provider = window.ethereum;
        walletType = 'MetaMask';
    }
    // Check for Coinbase Wallet
    else if (window.ethereum && window.ethereum.isCoinbaseWallet) {
        provider = window.ethereum;
        walletType = 'Coinbase Wallet';
    }
    // Check for Trust Wallet
    else if (window.ethereum && window.ethereum.isTrust) {
        provider = window.ethereum;
        walletType = 'Trust Wallet';
    }
    // Check for generic Web3 provider
    else if (window.ethereum) {
        provider = window.ethereum;
        walletType = 'Web3 Wallet';
    }
    // Check for legacy web3
    else if (window.web3) {
        provider = window.web3.currentProvider;
        walletType = 'Legacy Web3';
    }
    
    if (provider) {
        try {
            // Request account access
            let accounts;
            if (provider.request) {
                accounts = await provider.request({ method: 'eth_requestAccounts' });
            } else if (provider.enable) {
                accounts = await provider.enable();
            } else {
                throw new Error('Непідтримуваний провайдер гаманця');
            }
            
            const walletAddress = accounts[0];
            
            // Verify we're on the correct network (Polygon Mainnet)
            try {
                const chainId = await provider.request({ method: 'eth_chainId' });
                if (chainId !== '0x89') { // Polygon Mainnet chain ID
                    const shouldSwitch = confirm('Ви не підключені до мережі Polygon. Переключитись автоматично?');
                    if (shouldSwitch) {
                        await switchToPolygon(provider);
                    }
                }
            } catch (networkError) {
                console.warn('Не вдалося перевірити мережу:', networkError);
            }
            
            // Send address to backend
            const response = await fetch('/user/connect_wallet', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `wallet_address=${walletAddress}&wallet_type=${walletType}`
            });
            
            if (response.ok) {
                alert(`Гаманець ${walletType} успішно підключено!`);
                window.location.reload();
            } else {
                alert('Не вдалося підключити гаманець.');
            }
        } catch (err) {
            console.error('Помилка підключення гаманця:', err);
            if (err.code === 4001) {
                alert('Підключення гаманця скасовано користувачем.');
            } else {
                alert(`Помилка підключення ${walletType}: ${err.message}`);
            }
        }
    } else {
        // No Web3 provider detected - show manual input option
        showManualWalletInput();
    }
}

// Switch to Polygon network
async function switchToPolygon(provider) {
    try {
        await provider.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: '0x89' }], // Polygon Mainnet
        });
    } catch (switchError) {
        // Network not added to wallet, try to add it
        if (switchError.code === 4902) {
            try {
                await provider.request({
                    method: 'wallet_addEthereumChain',
                    params: [{
                        chainId: '0x89',
                        chainName: 'Polygon Mainnet',
                        nativeCurrency: {
                            name: 'MATIC',
                            symbol: 'MATIC',
                            decimals: 18,
                        },
                        rpcUrls: ['https://polygon-rpc.com/'],
                        blockExplorerUrls: ['https://polygonscan.com/'],
                    }],
                });
            } catch (addError) {
                console.error('Не вдалося додати мережу Polygon:', addError);
                alert('Будь ласка, додайте мережу Polygon вручну в налаштуваннях гаманця.');
            }
        } else {
            console.error('Не вдалося переключитись на Polygon:', switchError);
        }
    }
}

// Manual wallet input for users without Web3 browser extension
function showManualWalletInput() {
    const walletAddress = prompt(
        'Web3 гаманець не знайдено.\n\n' +
        'Ви можете ввести адресу вашого гаманця вручну:\n' +
        '(Підтримуються: MetaMask, Trust Wallet, Coinbase Wallet, Rainbow, та інші Ethereum-сумісні гаманці)'
    );
    
    if (walletAddress) {
        // Basic validation for Ethereum address format
        if (/^0x[a-fA-F0-9]{40}$/.test(walletAddress)) {
            submitWalletAddress(walletAddress, 'Manual Input');
        } else {
            alert('Неправильний формат адреси. Адреса повинна починатися з 0x та містити 40 символів.');
            showManualWalletInput(); // Try again
        }
    }
}

// Submit wallet address to backend
async function submitWalletAddress(address, walletType) {
    try {
        const response = await fetch('/user/connect_wallet', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `wallet_address=${address}&wallet_type=${walletType}`
        });
        
        if (response.ok) {
            alert(`Гаманець успішно підключено!\nТип: ${walletType}\nАдреса: ${address.substring(0,6)}...${address.substring(38)}`);
            window.location.reload();
        } else {
            alert('Не вдалося зберегти адресу гаманця.');
        }
    } catch (error) {
        console.error('Помилка збереження адреси:', error);
        alert('Сталася помилка при збереженні адреси гаманця.');
    }
}

// Detect wallet changes
function setupWalletEventListeners() {
    if (window.ethereum) {
        // Account changed
        window.ethereum.on('accountsChanged', function (accounts) {
            if (accounts.length === 0) {
                console.log('Гаманець відключено');
                alert('Гаманець відключено. Перезавантажте сторінку для повторного підключення.');
            } else {
                console.log('Акаунт змінено на:', accounts[0]);
                // Optionally auto-update the connected wallet
                if (confirm('Виявлено зміну акаунта в гаманці. Оновити підключення?')) {
                    window.location.reload();
                }
            }
        });
        
        // Network changed
        window.ethereum.on('chainChanged', function (chainId) {
            console.log('Мережа змінена на:', chainId);
            if (chainId !== '0x89') {
                alert('Увага: Ви переключилися з мережі Polygon. Деякі функції можуть не працювати правильно.');
            }
        });
    }
}

// Initialize wallet event listeners when page loads
document.addEventListener('DOMContentLoaded', function() {
    setupWalletEventListeners();
});

document.addEventListener('DOMContentLoaded', function () {
    const walletShort = document.getElementById('wallet-address-short');
    const walletCopyStatus = document.getElementById('wallet-copy-status');
    // Multilingual copy message from data attribute or fallback    
    let copiedMsg = walletCopyStatus ? walletCopyStatus.textContent : 'Copied!';
    if (walletShort) {
        walletShort.addEventListener('click', function () {
            const fullAddress = walletShort.getAttribute('data-full-address');
            navigator.clipboard.writeText(fullAddress).then(() => {
                if (walletCopyStatus) {
                    walletCopyStatus.style.display = 'inline';
                    walletCopyStatus.textContent = copiedMsg;
                    setTimeout(() => {
                        walletCopyStatus.style.display = 'none';
                    }, 1500);
                }
            });
        });
    }
    
    // Логіка для відео-фону    const videoBackground = document.getElementById('ocean-background');
    if (videoBackground) {
        videoBackground.addEventListener('error', function() {
            console.error('Помилка завантаження відео');
            document.body.classList.add('video-fallback');
            document.querySelector('.video-overlay').style.backgroundImage = 'linear-gradient(rgba(255, 255, 255, 0.9), rgba(245, 245, 245, 0.8))';
        });
        
        // Перевірка на мобільних пристроях
        if (window.matchMedia("(max-width: 767px)").matches) {
            // На малих екранах зменшуємо якість відео для кращої продуктивності
            videoBackground.pause();
            document.querySelector('.video-overlay').style.background = 'linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.7))';
            setTimeout(() => videoBackground.play(), 100);
        }
        
        // Динамічне накладання при прокрутці
        window.addEventListener('scroll', function() {
            const scrollPosition = window.scrollY;
            const maxScroll = document.body.scrollHeight - window.innerHeight;
            const scrollPercentage = scrollPosition / maxScroll;
            
            // Збільшуємо прозорість накладання при прокрутці
            const overlay = document.querySelector('.video-overlay');
            const baseOpacity = 0.5;
            const maxAdditionalOpacity = 0.3;
            const newOpacity = baseOpacity + (scrollPercentage * maxAdditionalOpacity);
            
            overlay.style.background = `linear-gradient(rgba(255, 255, 255, ${newOpacity}), rgba(255, 255, 255, ${Math.max(0.4, newOpacity - 0.1)}))`;
        });
        
        // Оптимізація для слабких пристроїв
        let frameCount = 0;
        let lastTime = performance.now();
        let lowPerformance = false;
        
        function checkPerformance() {
            frameCount++;
            const now = performance.now();
            if (now - lastTime >= 1000) {
                const fps = frameCount;
                frameCount = 0;
                lastTime = now;
                
                if (fps < 15 && !lowPerformance) {
                    lowPerformance = true;
                    videoBackground.pause();
                    document.querySelector('.video-overlay').style.background = 'linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.8))';
                }
            }
            
            if (!lowPerformance) {
                requestAnimationFrame(checkPerformance);
            }
        }
        
        requestAnimationFrame(checkPerformance);
    }    document.querySelectorAll('.auction-toggle-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var auctionId = btn.getAttribute('data-auction-id');
            var modal = document.getElementById('auctionModal-' + auctionId);
            if (modal) {
                try {
                    var bsModal = new bootstrap.Modal(modal);
                    bsModal.show();
                } catch (error) {
                    console.error("Error showing modal:", error);
                    // Fallback to direct navigation if modal fails
                    window.location.href = "/auction/" + auctionId;
                }
            } else {
                console.error("Modal element not found for auction ID:", auctionId);
                // Fallback to direct navigation if modal element is missing
                window.location.href = "/auction/" + auctionId;
            }
        });
    });

    function handleAuctionAction(btnClass, resultTextCb) {
        document.querySelectorAll(btnClass).forEach(function (btn) {
            btn.addEventListener('click', async function () {
                const auctionId = btn.getAttribute('data-auction-id');
                const url = btn.getAttribute('data-url');
                const resultDiv = document.getElementById('auction-action-result-' + auctionId);
                if (!url || !resultDiv) return;
                // Disable all action buttons for this auction
                const modal = btn.closest('.modal');
                modal.querySelectorAll('.participate-btn, .view-price-btn, .close-auction-btn').forEach(b => b.disabled = true);
                resultDiv.style.display = 'none';
                try {
                    const response = await fetch(url, { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' } });
                    const data = await response.json();
                    let html = '';
                    if (data.error) {
                        html = `<div class='alert alert-danger mb-0'>${data.error}</div>`;
                    } else {
                        html = resultTextCb(data);
                    }
                    resultDiv.innerHTML = html;
                    resultDiv.style.display = 'block';
                } catch (e) {
                    resultDiv.innerHTML = `<div class='alert alert-danger mb-0'>Сталася помилка. Спробуйте ще раз.</div>`;
                    resultDiv.style.display = 'block';
                }
                setTimeout(() => {
                    resultDiv.style.display = 'none';
                    modal.querySelectorAll('.participate-btn, .view-price-btn, .close-auction-btn').forEach(b => b.disabled = false);
                }, 5000);
            });
        });
    }
    handleAuctionAction('.participate-btn', data => `<div class='alert alert-success mb-0'>Успішно! Учасників: <b>${data.participants ?? '?'}</b>, поточна ціна: <b>${data.final_price ?? '?'}</b> грн</div>`);
    handleAuctionAction('.view-price-btn', data => `<div class='alert alert-info mb-0'>Перегляд ціни. Учасників: <b>${data.participants ?? '?'}</b>, поточна ціна: <b>${data.final_price ?? '?'}</b> грн</div>`);
    handleAuctionAction('.close-auction-btn', data => `<div class='alert alert-warning mb-0'>Аукціон закрито. Учасників: <b>${data.participants ?? '?'}</b>, ціна: <b>${data.final_price ?? '?'}</b> грн</div>`);
});

