// Modern, animated dataset creation interface
document.addEventListener('DOMContentLoaded', function() {
    // State
    let currentStep = 1;
    let datasetDescription = '';
    let columns = [];
    let rowCount = 10;
    let generatedData = null;
    let isLoading = false;
    let logs = [];

    // DOM Elements
    const app = document.getElementById('app');
    const step1 = document.getElementById('step-1');
    const step2 = document.getElementById('step-2');
    const step3 = document.getElementById('step-3');
    const step4 = document.getElementById('step-4');
    const descriptionInput = document.getElementById('dataset-description');    
    const columnsInput = document.getElementById('columns-input');
    const addColumnBtn = document.getElementById('add-column-btn');
    const columnsList = document.getElementById('columns-list');
    const rowCountInput = document.getElementById('row-count');
    const rowCountValue = document.getElementById('row-count-value');
    const nextStepBtn = document.getElementById('next-step');
    const prevStepBtn = document.getElementById('prev-step');
    const generateBtn = document.getElementById('generate-btn');
    const feedbackInput = document.getElementById('feedback-input');
    const regenerateBtn = document.getElementById('regenerate-btn');
    const finalizeBtn = document.getElementById('finalize-btn');
    const logsContainer = document.getElementById('logs');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    // Initialize
    updateStep(1);

    // Event Listeners
    nextStepBtn.addEventListener('click', nextStep);
    prevStepBtn.addEventListener('click', prevStep);
    generateBtn.addEventListener('click', generateDataset);
    regenerateBtn.addEventListener('click', generateDataset);
    finalizeBtn.addEventListener('click', finalizeDataset);
    
    // Update row count display
    rowCountInput.addEventListener('input', (e) => {
        rowCount = parseInt(e.target.value);
        rowCountValue.textContent = rowCount;
    });

    // Add column on Enter
    columnsInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addColumn();
        }
    });
    
    addColumnBtn.addEventListener('click', addColumn);

    // Functions
    function updateStep(step) {
        currentStep = step;
        
        // Hide all steps
        [step1, step2, step3, step4].forEach(step => {
            step.classList.add('hidden');
            step.classList.remove('fade-in');
        });
        
        // Show current step with animation
        const currentStepEl = document.getElementById(`step-${step}`);
        currentStepEl.classList.remove('hidden');
        setTimeout(() => currentStepEl.classList.add('fade-in'), 10);
        
        // Update navigation buttons
        prevStepBtn.style.visibility = step === 1 ? 'hidden' : 'visible';
        nextStepBtn.style.display = step < 4 ? 'block' : 'none';
        
        // Update progress bar
        const progress = ((step - 1) / 3) * 100;
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `Step ${step} of 4`;
    }
    
    function nextStep() {
        if (currentStep === 1 && !descriptionInput.value.trim()) {
            showError('Please enter a dataset description');
            return;
        }
        
        if (currentStep === 2 && columns.length === 0) {
            showError('Please add at least one column');
            return;
        }
        
        if (currentStep < 4) {
            updateStep(currentStep + 1);
        }
    }
    
    function prevStep() {
        if (currentStep > 1) {
            updateStep(currentStep - 1);
        }
    }
    
    function addColumn() {
        const columnName = columnsInput.value.trim();
        if (!columnName) return;
        
        if (!columns.includes(columnName)) {
            columns.push(columnName);
            renderColumns();
            columnsInput.value = '';
            columnsInput.focus();
        } else {
            showError('Column name already exists');
        }
    }
    
    function renderColumns() {
        columnsList.innerHTML = columns.map(column => `
            <div class="flex items-center justify-between p-2 bg-gray-50 rounded mb-2">
                <span>${column}</span>
                <button onclick="removeColumn('${column}')" class="text-red-500 hover:text-red-700">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    }
    
    function removeColumn(columnName) {
        columns = columns.filter(col => col !== columnName);
        renderColumns();
    }
    
    async function generateDataset() {
        if (isLoading) return;
        
        datasetDescription = descriptionInput.value.trim();
        const feedback = feedbackInput ? feedbackInput.value.trim() : '';
        
        if (!datasetDescription) {
            showError('Please enter a dataset description');
            return;
        }
        
        if (columns.length === 0) {
            showError('Please add at least one column');
            return;
        }
        
        isLoading = true;
        updateLoadingState(true);
        logs = [];
        updateLogs('Starting dataset generation...');
        
        try {
            const response = await fetch('/api/generate-sample', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    description: datasetDescription,
                    columns: columns,
                    row_count: rowCount,
                    feedback: feedback
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                console.log('Received sample data:', data);
                if (!data.sample_data) {
                    console.error('No sample_data in response:', data);
                    throw new Error('No sample data received from server');
                }
                
                generatedData = data.sample_data;
                console.log('Generated data structure:', {
                    type: Array.isArray(generatedData) ? 'array' : typeof generatedData,
                    length: Array.isArray(generatedData) ? generatedData.length : 'N/A',
                    firstItem: generatedData && generatedData.length > 0 ? generatedData[0] : 'empty'
                });
                
                updateLogs(`Generated ${data.sample_size} sample rows successfully!`);
                renderDataPreview();
                updateStep(4);
            } else {
                console.error('Error response from server:', data);
                throw new Error(data.error || 'Failed to generate dataset');
            }
        } catch (error) {
            console.error('Error generating dataset:', error);
            showError(error.message || 'An error occurred while generating the dataset');
        } finally {
            isLoading = false;
            updateLoadingState(false);
        }
    }
    
    function renderDataPreview() {
        const previewElement = document.getElementById('data-preview');
        
        try {
            console.log('Rendering data preview with:', generatedData);
            
            if (!generatedData || generatedData.length === 0) {
                console.warn('No data to display in preview');
                previewElement.innerHTML = '<p class="text-yellow-600 bg-yellow-50 p-4 rounded">No data to display. The dataset was generated but contains no rows.</p>';
                return;
            }
            
            // Handle case where generatedData is an array but items don't have expected structure
            if (!generatedData[0] || typeof generatedData[0] !== 'object') {
                console.error('Unexpected data format:', generatedData);
                previewElement.innerHTML = `
                    <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
                        <div class="flex">
                            <div class="flex-shrink-0">
                                <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                                </svg>
                            </div>
                            <div class="ml-3">
                                <p class="text-sm text-red-700">
                                    Error: Unexpected data format received. Please check the console for details.
                                </p>
                            </div>
                        </div>
                    </div>
                    <pre class="bg-gray-100 p-4 rounded overflow-auto text-xs">${JSON.stringify(generatedData, null, 2)}</pre>
                `;
                return;
            }
            
            const headers = Object.keys(generatedData[0]);
            const rows = generatedData.map(row => Object.values(row));
            
            previewElement.innerHTML = `
                <div class="overflow-x-auto">
                    <table class="min-w-full bg-white">
                        <thead>
                            <tr>
                                ${headers.map(header => 
                                    `<th class="px-4 py-2 border-b border-gray-200 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        ${header}
                                    </th>`
                                ).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${rows.slice(0, 10).map(row => `
                                <tr class="hover:bg-gray-50">
                                    ${row.map(cell => 
                                        `<td class="px-4 py-2 border-b border-gray-200 text-sm">
                                            ${cell !== null && cell !== undefined ? cell : 
                                                '<span class="text-gray-400 italic">null</span>'}
                                        </td>`
                                    ).join('')}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                    ${rows.length > 10 ? 
                        `<p class="mt-2 text-sm text-gray-500">Showing 10 of ${rows.length} rows</p>` : 
                        `<p class="mt-2 text-sm text-gray-500">Showing all ${rows.length} rows</p>`
                    }
                </div>
            `;
        } catch (error) {
            console.error('Error rendering data preview:', error);
            previewElement.innerHTML = `
                <div class="bg-red-50 border-l-4 border-red-400 p-4">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                            </svg>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm text-red-700">
                                Error rendering data preview: ${error.message}
                            </p>
                        </div>
                    </div>
                </div>
            `;
        }
    }
    
    async function finalizeDataset() {
        if (!generatedData) return;
        
        try {
            updateLogs('Saving dataset...');
            const response = await fetch('/api/finalize-dataset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    description: datasetDescription,
                    columns: columns,
                    data: generatedData
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                updateLogs('Dataset saved successfully!');
                showSuccess('Dataset created successfully!');
                
                // Redirect to datasets page after a short delay
                setTimeout(() => {
                    window.location.href = '/datasets';
                }, 1500);
            } else {
                throw new Error(data.error || 'Failed to save dataset');
            }
        } catch (error) {
            console.error('Error saving dataset:', error);
            showError(error.message || 'An error occurred while saving the dataset');
        }
    }
    
    function updateLoadingState(isLoading) {
        const buttons = [generateBtn, regenerateBtn, finalizeBtn, nextStepBtn];
        buttons.forEach(btn => {
            if (!btn) return;
            btn.disabled = isLoading;
            const spinner = btn.querySelector('.spinner');
            if (spinner) {
                spinner.classList.toggle('hidden', !isLoading);
            }
        });
    }
    
    function updateLogs(message) {
        logs.push(`[${new Date().toLocaleTimeString()}] ${message}`);
        if (logsContainer) {
            logsContainer.innerHTML = logs.map(log => `<div class="log-entry">${log}</div>`).join('');
            logsContainer.scrollTop = logsContainer.scrollHeight;
        }
    }
    
    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded';
        errorDiv.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-exclamation-circle mr-2"></i>
                <span>${message}</span>
                <button class="ml-4 text-red-700" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        document.body.appendChild(errorDiv);
        setTimeout(() => errorDiv.remove(), 5000);
    }
    
    function showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded';
        successDiv.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-check-circle mr-2"></i>
                <span>${message}</span>
            </div>
        `;
        document.body.appendChild(successDiv);
        setTimeout(() => successDiv.remove(), 3000);
    }
    
    function getCSRFToken() {
        return document.querySelector('input[name="csrf_token"]')?.value || '';
    }
    
    // Make removeColumn available globally for inline handlers
    window.removeColumn = removeColumn;
});

// Add some basic animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease-out forwards;
    }
    
    .log-entry {
        padding: 0.5rem 0;
        border-bottom: 1px solid #e5e7eb;
        font-family: monospace;
        font-size: 0.875rem;
    }
    
    .spinner {
        display: inline-block;
        width: 1rem;
        height: 1rem;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);
            
            const typeName = typeNames[column.type] || column.type;
            const options = [];
            if (column.nullable) options.push('Nullable');
            if (column.pattern) options.push('Custom Pattern');
            
            tr.innerHTML = `
                <td class="px-3 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">${column.name}</div>
                </td>
                <td class="px-3 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        ${typeName}
                    </span>
                </td>
                <td class="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${options.join(' • ')}
                </td>
                <td class="px-3 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button class="text-blue-600 hover:text-blue-900 mr-3">Edit</button>
                    <button class="text-red-600 hover:text-red-900" data-index="${index}">Delete</button>
                </td>
            `;
            
            // Add event listeners to the delete button
            const deleteBtn = tr.querySelector('button.text-red-600');
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (confirm('Are you sure you want to delete this column?')) {
                    columns.splice(index, 1);
                    renderColumns();
                }
            });
            
            columnsTbody.appendChild(tr);
        });
        
        // Update preview
        updatePreview();
    }

    function toggleCustomPattern() {
        const type = dataTypeSelect.value;
        if (type === 'custom') {
            customPatternGroup.classList.remove('hidden');
        } else {
            customPatternGroup.classList.add('hidden');
        }
    }

    function toggleNullPercentage() {
        if (isNullableCheckbox.checked) {
            nullPercentageGroup.classList.remove('hidden');
        } else {
            nullPercentageGroup.classList.add('hidden');
        }
    }

    function updateNullPercentage() {
        nullPercentageValue.textContent = `${nullPercentageInput.value}%`;
    }

    function updatePreview() {
        const previewHeader = document.getElementById('preview-header');
        const previewBody = document.getElementById('preview-body');
        
        // Update header
        previewHeader.innerHTML = columns.map(col => 
            `<th scope="col" class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">${col.name}</th>`
        ).join('');
        
        if (columns.length === 0) {
            previewHeader.innerHTML = '<th scope="col" class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">No columns defined</th>';
        }
        
        // Update body with sample data
        previewBody.innerHTML = '';
        
        if (columns.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td colspan="${Math.max(1, columns.length)}" class="px-3 py-2 text-sm text-gray-500 text-center">
                    Add columns to see a preview of your data
                </td>
            `;
            previewBody.appendChild(row);
            return;
        }
        
        // Generate sample data for preview
        for (let i = 0; i < 3; i++) {
            const row = document.createElement('tr');
            row.className = i % 2 === 0 ? 'bg-white' : 'bg-gray-50';
            
            const cells = columns.map(col => {
                let value = '';
                
                // Simple data generation for preview
                switch(col.type) {
                    case 'text':
                        value = 'Sample text';
                        break;
                    case 'number':
                        value = Math.floor(Math.random() * 100);
                        break;
                    case 'date':
                        value = new Date().toISOString().split('T')[0];
                        break;
                    case 'boolean':
                        value = Math.random() > 0.5 ? 'True' : 'False';
                        break;
                    case 'email':
                        value = 'user@example.com';
                        break;
                    case 'name':
                        value = 'John Doe';
                        break;
                    case 'address':
                        value = '123 Main St';
                        break;
                    case 'phone':
                        value = '(555) 123-4567';
                        break;
                    case 'url':
                        value = 'https://example.com';
                        break;
                    case 'custom':
                        value = col.pattern ? 'Custom data' : 'No pattern';
                        break;
                    default:
                        value = 'Data';
                }
                
                return `<td class="px-3 py-2 whitespace-nowrap text-sm text-gray-500">${value}</td>`;
            });
            
            row.innerHTML = cells.join('');
            previewBody.appendChild(row);
        }
    }

    async function generateDataset(type) {
        const datasetName = document.getElementById('dataset-name').value.trim();
        const datasetDescription = document.getElementById('dataset-description').value.trim();
        const rowCount = parseInt(document.getElementById('row-count').value) || 1000;
        const format = document.getElementById('data-format').value;
        const includeHeader = document.getElementById('include-header').checked;
        
        if (!datasetName) {
            alert('Please enter a dataset name');
            return;
        }
        
        if (columns.length === 0) {
            alert('Please add at least one column to your dataset');
            return;
        }
    }
    
    // Initialize the preview
    updatePreview();
});
