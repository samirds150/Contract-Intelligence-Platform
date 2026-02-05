// DOM Elements
const questionInput = document.getElementById('question-input');
const submitBtn = document.getElementById('submit-btn');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('error-message');
const errorText = document.getElementById('error-text');
const answerSection = document.getElementById('answer-section');
const emptyState = document.getElementById('empty-state');

// Event Listeners
submitBtn.addEventListener('click', handleSubmit);
questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
        handleSubmit();
    }
});

/**
 * Handle question submission
 */
async function handleSubmit() {
    const question = questionInput.value.trim();
    
    if (!question) {
        showError('Please enter a question');
        return;
    }
    
    await askQuestion(question);
}

/**
 * Ask a question to the RAG system
 */
async function askQuestion(question) {
    // Update input if called from suggestion button
    if (questionInput.value !== question) {
        questionInput.value = question;
    }
    
    // Clear previous state
    clearError();
    answerSection.style.display = 'none';
    emptyState.style.display = 'none';
    loading.style.display = 'flex';
    
    // Disable submit button
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question })
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || `HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            displayAnswer(question, data);
        } else {
            showError(data.error || 'Failed to get answer');
        }
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred. Please try again.');
    } finally {
        // Re-enable submit button
        submitBtn.disabled = false;
        loading.style.display = 'none';
    }
}

/**
 * Display the answer
 */
function displayAnswer(question, data) {
    // Display question
    document.getElementById('display-question').textContent = question;
    
    // Display answer
    document.getElementById('answer-text').textContent = data.answer;
    
    // Display confidence
    const confidencePercentage = (data.confidence * 100).toFixed(0);
    const confidenceBadge = document.getElementById('confidence-badge');
    confidenceBadge.textContent = `Confidence: ${confidencePercentage}%`;
    
    // Set confidence color
    if (data.confidence >= 0.8) {
        confidenceBadge.style.background = '#4caf50';
    } else if (data.confidence >= 0.5) {
        confidenceBadge.style.background = '#ff9800';
    } else {
        confidenceBadge.style.background = '#f44336';
    }
    
    // Display context
    if (data.context && data.context.length > 0) {
        const contextSection = document.getElementById('context-section');
        const contextItems = document.getElementById('context-items');
        contextItems.innerHTML = '';
        
        data.context.forEach((ctx, index) => {
            const contextItem = document.createElement('div');
            contextItem.className = 'context-item';
            contextItem.innerHTML = `
                <div class="context-item-header">
                    <span class="context-item-source">📌 ${ctx.source}</span>
                    <span class="context-item-similarity">${(ctx.similarity * 100).toFixed(0)}% match</span>
                </div>
                <p class="context-item-text">${escapeHtml(ctx.text)}</p>
            `;
            contextItems.appendChild(contextItem);
        });
        
        contextSection.style.display = 'block';
    } else {
        document.getElementById('context-section').style.display = 'none';
    }
    
    // Display sources
    if (data.sources && data.sources.length > 0) {
        const sourcesSection = document.getElementById('sources-section');
        const sourcesList = document.getElementById('sources-list');
        sourcesList.innerHTML = '';
        
        data.sources.forEach(source => {
            const badge = document.createElement('span');
            badge.className = 'source-badge';
            badge.textContent = `📄 ${source}`;
            sourcesList.appendChild(badge);
        });
        
        sourcesSection.style.display = 'block';
    } else {
        document.getElementById('sources-section').style.display = 'none';
    }
    
    // Show answer section
    answerSection.style.display = 'block';
}

/**
 * Show error message
 */
function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
}

/**
 * Clear error message
 */
function clearError() {
    errorMessage.style.display = 'none';
    errorText.textContent = '';
}

/**
 * Reset form for new question
 */
function resetForm() {
    questionInput.value = '';
    answerSection.style.display = 'none';
    emptyState.style.display = 'flex';
    questionInput.focus();
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, (m) => map[m]);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Focus on input
    questionInput.focus();
    
    // Show empty state
    emptyState.style.display = 'flex';
});
