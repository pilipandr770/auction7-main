// MetaMask integration for wallet connect
async function connectWallet() {
    if (window.ethereum) {
        try {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            const walletAddress = accounts[0];
            // Send address to backend
            const response = await fetch('/user/connect_wallet', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `wallet_address=${walletAddress}`
            });
            if (response.ok) {
                window.location.reload();
            } else {
                alert('Не вдалося підключити гаманець.');
            }
        } catch (err) {
            alert('Підключення MetaMask скасовано або сталася помилка.');
        }
    } else {
        alert('MetaMask не встановлено!');
    }
}

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

