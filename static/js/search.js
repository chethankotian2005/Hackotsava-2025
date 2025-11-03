/**
 * Search page functionality - Drag & Drop, Preview, Form handling
 */

document.addEventListener('DOMContentLoaded', function() {
    initSelfieUpload();
    initToleranceSlider();
    initSearchForm();
    initDownloadAll();
});

/**
 * Initialize selfie upload with drag & drop
 */
function initSelfieUpload() {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('selfie-upload');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeBtn = document.getElementById('remove-preview');
    
    if (!uploadZone || !fileInput) return;
    
    // Click to upload
    uploadZone.addEventListener('click', function(e) {
        if (e.target !== removeBtn && !e.target.closest('.btn-remove-preview')) {
            fileInput.click();
        }
    });
    
    // File input change
    fileInput.addEventListener('change', function(e) {
        handleFiles(e.target.files);
    });
    
    // Drag & Drop functionality
    uploadZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.classList.add('drag-over');
    });
    
    uploadZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.classList.remove('drag-over');
    });
    
    uploadZone.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFiles(files);
        }
    });
    
    // Remove preview
    if (removeBtn) {
        removeBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            clearPreview();
        });
    }
    
    /**
     * Handle uploaded files
     */
    function handleFiles(files) {
        if (files.length === 0) return;
        
        const file = files[0];
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
            showNotification('Please upload an image file', 'error');
            return;
        }
        
        // Validate file size (20MB)
        const maxSize = 20 * 1024 * 1024; // 20MB in bytes
        if (file.size > maxSize) {
            showNotification('File size exceeds 20MB limit', 'error');
            return;
        }
        
        // Show preview
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            previewContainer.style.display = 'block';
            uploadZone.querySelector('.upload-label').style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
    
    /**
     * Clear preview
     */
    function clearPreview() {
        fileInput.value = '';
        imagePreview.src = '';
        previewContainer.style.display = 'none';
        uploadZone.querySelector('.upload-label').style.display = 'flex';
    }
}

/**
 * Initialize tolerance slider
 */
function initToleranceSlider() {
    const slider = document.getElementById('tolerance-slider');
    const valueDisplay = document.getElementById('tolerance-value');
    
    if (slider && valueDisplay) {
        slider.addEventListener('input', function() {
            valueDisplay.textContent = this.value;
        });
    }
}

/**
 * Initialize search form
 */
function initSearchForm() {
    const form = document.getElementById('search-form');
    const searchBtn = document.getElementById('search-btn');
    
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        const fileInput = document.getElementById('selfie-upload');
        
        if (!fileInput.files || fileInput.files.length === 0) {
            e.preventDefault();
            showNotification('Please upload a selfie first', 'warning');
            return;
        }
        
        // Show loading state
        if (searchBtn) {
            const btnText = searchBtn.querySelector('.btn-text');
            const btnLoader = searchBtn.querySelector('.btn-loader');
            
            if (btnText && btnLoader) {
                btnText.style.display = 'none';
                btnLoader.style.display = 'inline-flex';
                searchBtn.disabled = true;
            }
        }
        
        // Form will submit normally
        // Loading state will be removed on page reload
    });
}

/**
 * Initialize download all button
 */
function initDownloadAll() {
    const downloadAllBtn = document.getElementById('download-all');
    
    if (!downloadAllBtn) return;
    
    downloadAllBtn.addEventListener('click', async function() {
        const resultCards = document.querySelectorAll('.result-card');
        
        if (resultCards.length === 0) {
            showNotification('No photos to download', 'warning');
            return;
        }
        
        showNotification('Downloading photos... This may take a moment', 'info');
        
        // Download each image
        for (let i = 0; i < resultCards.length; i++) {
            const card = resultCards[i];
            const img = card.querySelector('.result-image img');
            
            if (img && img.src) {
                try {
                    await downloadImage(img.src, `photo-${i + 1}.jpg`);
                    
                    // Small delay between downloads to avoid overwhelming the browser
                    if (i < resultCards.length - 1) {
                        await sleep(300);
                    }
                } catch (error) {
                    console.error('Error downloading image:', error);
                }
            }
        }
        
        showNotification(`Downloaded ${resultCards.length} photos successfully!`, 'success');
    });
}

/**
 * Download single image
 */
async function downloadImage(url, filename) {
    try {
        const response = await fetch(url);
        const blob = await response.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Clean up
        window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
        console.error('Download failed:', error);
        throw error;
    }
}

/**
 * Sleep utility
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Filter results by confidence
 */
function filterByConfidence(minConfidence) {
    const resultCards = document.querySelectorAll('.result-card');
    
    resultCards.forEach(card => {
        const confidence = parseFloat(card.dataset.confidence);
        
        if (confidence >= minConfidence) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

/**
 * Add confidence filter if needed
 */
function initConfidenceFilter() {
    const resultsSection = document.querySelector('.results-section');
    
    if (!resultsSection) return;
    
    const filterHtml = `
        <div class="confidence-filter" style="margin-bottom: 2rem; text-align: center;">
            <label for="confidence-filter">Minimum Confidence: <span id="confidence-filter-value">0</span>%</label>
            <input type="range" id="confidence-filter" min="0" max="100" value="0" class="slider" style="width: 300px; max-width: 100%;">
        </div>
    `;
    
    resultsSection.querySelector('.results-header').insertAdjacentHTML('afterend', filterHtml);
    
    const filterSlider = document.getElementById('confidence-filter');
    const filterValue = document.getElementById('confidence-filter-value');
    
    filterSlider.addEventListener('input', function() {
        filterValue.textContent = this.value;
        filterByConfidence(parseFloat(this.value));
    });
}

// Initialize confidence filter if results exist
if (document.querySelector('.results-section')) {
    initConfidenceFilter();
}
