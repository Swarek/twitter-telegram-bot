// Initialize Lucide icons if available
if (typeof lucide !== 'undefined') {
    lucide.createIcons();
}

// API base URL
const API_URL = 'http://localhost:5000/api';

// Helper function to update numbers with animation
function updateNumber(elementId, value) {
    const element = document.getElementById(elementId);
    if (element && element.textContent !== value.toString()) {
        element.classList.add('updating');
        element.textContent = value;
        setTimeout(() => {
            element.classList.remove('updating');
        }, 300);
    }
}

// Animation helper for number changes
function animateNumber(element, newValue) {
    const currentValue = element.textContent;
    if (currentValue !== newValue.toString()) {
        element.style.animation = 'none';
        setTimeout(() => {
            element.textContent = newValue;
            element.style.animation = 'ticker 0.5s ease-out';
        }, 10);
    }
}

// Load data on page load
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadAccounts();
    checkBotStatus();
    
    // Refresh every 30 seconds
    setInterval(() => {
        loadStats();
        checkBotStatus();
    }, 30000);
    
    // Reinitialize Lucide icons after dynamic content loads if available
    if (typeof lucide !== 'undefined') {
        const observer = new MutationObserver(() => {
            lucide.createIcons();
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
});

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        const data = await response.json();
        
        if (data.success) {
            const stats = data.stats;
            
            // Update stats cards with animation
            animateNumber(document.getElementById('total-tweets'), stats.total_tweets);
            animateNumber(document.getElementById('active-accounts'), `${stats.active_accounts}/${stats.total_accounts}`);
            animateNumber(document.getElementById('api-usage'), `${stats.api_usage.estimated_usage}/100`);
            
            // Update poll interval with animation
            const hours = Math.round(stats.poll_interval / 3600);
            animateNumber(document.getElementById('poll-interval'), `${hours}h`);
            
            // Update API usage color
            const apiUsageEl = document.getElementById('api-usage');
            if (stats.api_usage.percentage > 90) {
                apiUsageEl.className = 'text-3xl font-bold text-red-600 number-ticker';
            } else if (stats.api_usage.percentage > 70) {
                apiUsageEl.className = 'text-3xl font-bold text-orange-600 number-ticker';
            } else {
                apiUsageEl.className = 'text-3xl font-bold text-green-600 number-ticker';
            }
            
            // Load recent tweets
            loadRecentTweets(stats.recent_tweets);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load accounts
async function loadAccounts() {
    try {
        const response = await fetch(`${API_URL}/accounts`);
        const data = await response.json();
        
        if (data.success) {
            const accountsList = document.getElementById('accounts-list');
            accountsList.innerHTML = '';
            
            data.accounts.forEach(account => {
                const accountEl = createAccountElement(account);
                accountsList.appendChild(accountEl);
            });
            
            if (data.accounts.length === 0) {
                accountsList.innerHTML = '<p class="text-gray-500 text-center py-8">Aucun compte configuré</p>';
            }
        }
    } catch (error) {
        console.error('Error loading accounts:', error);
    }
}

// Create account element with enhanced styling
function createAccountElement(account) {
    const div = document.createElement('div');
    div.className = 'flex items-center justify-between p-4 border border-gray-200/50 dark:border-gray-700/50 rounded-lg hover:shadow-md transition-all duration-300 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm';
    
    const statusClass = account.is_active ? 'bg-green-500' : 'bg-gray-400';
    const statusText = account.is_active ? 'Actif' : 'Inactif';
    
    div.innerHTML = `
        <div class="flex items-center space-x-4">
            <div class="flex-shrink-0">
                <span class="w-3 h-3 ${statusClass} rounded-full inline-block pulse-indicator"></span>
            </div>
            <div>
                <p class="text-sm font-medium text-gray-900 dark:text-white">@${account.username}</p>
                <p class="text-sm text-gray-500 dark:text-gray-400">→ ${account.telegram_channel_id}</p>
            </div>
        </div>
        <div class="flex items-center space-x-2">
            <button onclick="toggleAccount('${account.username}', ${!account.is_active})" 
                    class="px-4 py-2 text-sm rounded-lg transition-all ${account.is_active ? 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/50' : 'bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-400 dark:hover:bg-green-900/50'}">
                ${account.is_active ? 'Désactiver' : 'Activer'}
            </button>
        </div>
    `;
    
    // Add fade-in animation
    div.style.opacity = '0';
    div.style.transform = 'translateY(10px)';
    setTimeout(() => {
        div.style.transition = 'all 0.3s ease-out';
        div.style.opacity = '1';
        div.style.transform = 'translateY(0)';
    }, 50);
    
    return div;
}

// Load recent tweets
function loadRecentTweets(tweets) {
    const tweetsContainer = document.getElementById('recent-tweets');
    tweetsContainer.innerHTML = '';
    
    if (tweets.length === 0) {
        tweetsContainer.innerHTML = '<p class="text-gray-500 text-center py-8">Aucun tweet récent</p>';
        return;
    }
    
    tweets.forEach((tweet, index) => {
        const tweetEl = document.createElement('div');
        tweetEl.className = 'border-l-4 border-blue-500 pl-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800/50 rounded-r-lg transition-all duration-300';
        
        const date = new Date(tweet.published_at).toLocaleString('fr-FR');
        const text = tweet.text ? tweet.text.substring(0, 100) + '...' : '';
        
        tweetEl.innerHTML = `
            <p class="text-sm text-gray-600 dark:text-gray-400">@${tweet.username} • ${date}</p>
            <p class="text-gray-900 dark:text-white mt-1">${text}</p>
        `;
        
        // Add staggered fade-in animation
        tweetEl.style.opacity = '0';
        tweetEl.style.transform = 'translateX(-20px)';
        setTimeout(() => {
            tweetEl.style.transition = 'all 0.3s ease-out';
            tweetEl.style.opacity = '1';
            tweetEl.style.transform = 'translateX(0)';
        }, index * 100);
        
        tweetsContainer.appendChild(tweetEl);
    });
}

// Check bot status
async function checkBotStatus() {
    try {
        const response = await fetch(`${API_URL}/bot/status`);
        const data = await response.json();
        
        const statusIndicator = document.getElementById('status-indicator');
        
        if (data.success && data.running) {
            statusIndicator.innerHTML = `
                <span class="w-2 h-2 bg-green-500 rounded-full pulse-indicator"></span>
                <span class="text-sm font-medium text-green-600">En cours</span>
            `;
        } else {
            statusIndicator.innerHTML = `
                <span class="w-2 h-2 bg-red-500 rounded-full"></span>
                <span class="text-sm font-medium text-red-600">Arrêté</span>
            `;
        }
    } catch (error) {
        console.error('Error checking bot status:', error);
    }
}

// Toggle account
async function toggleAccount(username, active) {
    try {
        const response = await fetch(`${API_URL}/accounts/${username}/toggle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ active })
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadAccounts();
            loadStats();
        } else {
            alert('Erreur: ' + data.error);
        }
    } catch (error) {
        console.error('Error toggling account:', error);
        alert('Erreur lors de la modification du compte');
    }
}

// Show add account modal with animation
function showAddAccountModal() {
    const modal = document.getElementById('add-account-modal');
    modal.classList.remove('hidden');
    
    // Trigger reflow to ensure animation plays
    modal.offsetHeight;
    
    // Reinitialize Lucide icons in modal
    setTimeout(() => {
        lucide.createIcons();
    }, 100);
}

// Hide add account modal
function hideAddAccountModal() {
    document.getElementById('add-account-modal').classList.add('hidden');
    document.getElementById('new-username').value = '';
    document.getElementById('new-channel').value = '';
}

// Add account
async function addAccount() {
    const username = document.getElementById('new-username').value.trim();
    const channel = document.getElementById('new-channel').value.trim();
    
    if (!username || !channel) {
        alert('Veuillez remplir tous les champs');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/accounts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                channel_id: channel.startsWith('@') ? channel : '@' + channel
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            hideAddAccountModal();
            loadAccounts();
            loadStats();
        } else {
            alert('Erreur: ' + data.error);
        }
    } catch (error) {
        console.error('Error adding account:', error);
        alert('Erreur lors de l\'ajout du compte');
    }
}