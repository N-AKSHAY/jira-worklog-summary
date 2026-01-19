class WorklogForm {
    constructor(formId, dateRangeId, startDateId, endDateId) {
        this.form = document.getElementById(formId);
        this.dateRangeInput = document.getElementById(dateRangeId);
        this.startDateInput = document.getElementById(startDateId);
        this.endDateInput = document.getElementById(endDateId);
        
        if (!this.form || !this.dateRangeInput || !this.startDateInput || !this.endDateInput) {
            console.error('WorklogForm: Required elements not found');
            return;
        }
        
        this.flatpickr = null;
        this.currentView = this.getStoredView() || 'card';
        this.currentData = null;
        this.init();
    }
    
    init() {
        this.setDefaultDates();
        this.initializeDateRangePicker();
        this.attachEventListeners();
        this.initializeViewToggle();
        this.loadInitialData();
    }
    
    getStoredView() {
        try {
            return localStorage.getItem('worklogView') || 'card';
        } catch (e) {
            return 'card';
        }
    }
    
    setStoredView(view) {
        try {
            localStorage.setItem('worklogView', view);
        } catch (e) {
            console.warn('Failed to store view preference');
        }
    }
    
    initializeViewToggle() {
        const toggleButton = document.getElementById('viewToggle');
        if (toggleButton) {
            this.updateToggleButton();
            toggleButton.addEventListener('click', () => this.toggleView());
        }
    }
    
    toggleView() {
        this.currentView = this.currentView === 'card' ? 'table' : 'card';
        this.setStoredView(this.currentView);
        this.updateToggleButton();
        if (this.currentData) {
            this.renderResults(this.currentData);
        }
    }
    
    updateToggleButton() {
        const toggleButton = document.getElementById('viewToggle');
        const toggleText = toggleButton?.querySelector('.view-toggle-text');
        const svg = toggleButton?.querySelector('svg');
        if (toggleButton && toggleText && svg) {
            if (this.currentView === 'table') {
                toggleText.textContent = 'Card';
                svg.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path>';
            } else {
                toggleText.textContent = 'Table';
                svg.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>';
            }
        }
    }
    
    loadInitialData() {
        const serverDataScript = document.getElementById('serverData');
        const resultsContainer = document.getElementById('resultsContainer');
        
        if (serverDataScript) {
            try {
                const data = JSON.parse(serverDataScript.textContent);
                this.currentData = data;
                
                if (this.currentView === 'table') {
                    resultsContainer.innerHTML = '';
                    this.renderResults(data);
                }
            } catch (e) {
                console.warn('Failed to parse server data', e);
            }
        } else {
            const hasExistingData = resultsContainer && resultsContainer.querySelector('[data-day-card]');
            
            if (!hasExistingData) {
                const startDate = this.startDateInput.value;
                const endDate = this.endDateInput.value;
                
                if (startDate && endDate) {
                    this.submitFormAsync();
                }
            }
        }
    }
    
    initializeDateRangePicker() {
        const existingStart = this.startDateInput.value;
        const existingEnd = this.endDateInput.value;
        const today = this.getTodayDate();
        
        let initialDates = [];
        if (existingStart && existingEnd) {
            initialDates = [existingStart, existingEnd];
        } else if (existingStart) {
            initialDates = [existingStart, existingStart];
        } else {
            initialDates = [today, today];
        }
        
        this.flatpickr = flatpickr(this.dateRangeInput, {
            mode: 'range',
            dateFormat: 'Y-m-d',
            defaultDate: initialDates,
            minDate: null,
            maxDate: today,
            allowInput: false,
            clickOpens: true,
            onChange: (selectedDates, dateStr, instance) => {
                this.handleDateRangeChange(selectedDates);
            },
            onReady: (selectedDates, dateStr, instance) => {
                this.updateHiddenInputs(selectedDates.length > 0 ? selectedDates : initialDates);
            }
        });
    }
    
    setDefaultDates() {
        if (!this.startDateInput.value || !this.endDateInput.value) {
            const { startDate, endDate } = this.calculateDateRange('thisWeek');
            this.startDateInput.value = startDate;
            this.endDateInput.value = endDate;
        }
    }
    
    getTodayDate() {
        return new Date().toISOString().split('T')[0];
    }
    
    handleDateRangeChange(selectedDates) {
        if (selectedDates.length === 2) {
            const [startDate, endDate] = selectedDates;
            this.startDateInput.value = this.formatDate(startDate);
            this.endDateInput.value = this.formatDate(endDate);
        } else if (selectedDates.length === 1) {
            this.startDateInput.value = this.formatDate(selectedDates[0]);
            this.endDateInput.value = this.formatDate(selectedDates[0]);
        }
    }
    
    updateHiddenInputs(selectedDates) {
        if (selectedDates.length >= 1) {
            this.startDateInput.value = this.formatDate(selectedDates[0]);
            if (selectedDates.length === 2) {
                this.endDateInput.value = this.formatDate(selectedDates[1]);
            } else {
                this.endDateInput.value = this.formatDate(selectedDates[0]);
            }
        }
    }
    
    formatDate(date) {
        if (!date) return '';
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    attachEventListeners() {
        this.form.addEventListener('submit', (event) => this.handleFormSubmit(event));
        this.attachQuickRangeButtons();
    }
    
    attachQuickRangeButtons() {
        const quickButtons = document.querySelectorAll('.quick-range-btn');
        quickButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const range = button.getAttribute('data-range');
                this.setQuickRange(range);
            });
        });
    }
    
    setQuickRange(range) {
        const { startDate, endDate } = this.calculateDateRange(range);
        this.setDateRange(startDate, endDate);
        this.submitFormAsync();
    }
    
    calculateDateRange(range) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        let startDate, endDate;
        
        switch (range) {
            case 'today':
                startDate = new Date(today);
                endDate = new Date(today);
                break;
                
            case 'yesterday':
                startDate = new Date(today);
                startDate.setDate(startDate.getDate() - 1);
                endDate = new Date(startDate);
                break;
                
            case 'thisWeek':
                startDate = new Date(today);
                const dayOfWeek = startDate.getDay();
                const diff = startDate.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1);
                startDate.setDate(diff);
                endDate = new Date(today);
                break;
                
            case 'thisMonth':
                startDate = new Date(today.getFullYear(), today.getMonth(), 1);
                endDate = new Date(today);
                break;
                
            case 'lastMonth':
                startDate = new Date(today.getFullYear(), today.getMonth() - 1, 1);
                endDate = new Date(today.getFullYear(), today.getMonth(), 0);
                break;
                
            case 'thisYear':
                startDate = new Date(today.getFullYear(), 0, 1);
                endDate = new Date(today);
                break;
                
            case 'lastYear':
                startDate = new Date(today.getFullYear() - 1, 0, 1);
                endDate = new Date(today.getFullYear() - 1, 11, 31);
                break;
                
            default:
                startDate = new Date(today);
                endDate = new Date(today);
        }
        
        return {
            startDate: this.formatDate(startDate),
            endDate: this.formatDate(endDate)
        };
    }
    
    setDateRange(startDate, endDate) {
        this.startDateInput.value = startDate;
        this.endDateInput.value = endDate;
        
        if (this.flatpickr) {
            const start = new Date(startDate);
            const end = new Date(endDate);
            this.flatpickr.setDate([start, end], false);
        }
    }
    
    handleFormSubmit(event) {
        event.preventDefault();
        
        if (this.isDateRangeInvalid()) {
            this.showValidationError();
            if (this.flatpickr) {
                this.flatpickr.open();
            }
            return;
        }
        
        this.submitFormAsync();
    }
    
    async submitFormAsync() {
        const submitButton = this.form.querySelector('button[type="submit"]');
        const loadingIndicator = document.getElementById('loadingIndicator');
        const resultsContainer = document.getElementById('resultsContainer');
        const errorContainer = document.getElementById('errorContainer');
        const generateText = submitButton.querySelector('.generate-text');
        const spinner = submitButton.querySelector('svg');
        
        const startDate = this.startDateInput.value;
        const endDate = this.endDateInput.value;
        
        if (!startDate || !endDate) {
            this.showError('Please select a date range');
            return;
        }
        
        submitButton.disabled = true;
        if (generateText) generateText.textContent = 'Generating...';
        if (spinner) spinner.classList.remove('hidden');
        if (loadingIndicator) loadingIndicator.classList.remove('hidden');
        if (loadingIndicator) loadingIndicator.classList.add('flex');
        if (errorContainer) errorContainer.style.display = 'none';
        if (resultsContainer) resultsContainer.innerHTML = '';
        
        try {
            const response = await fetch('/api/v1/jira-worklogs/summary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    startDate: startDate,
                    endDate: endDate
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: 'An error occurred' }));
                throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.currentData = data;
            this.renderResults(data);
        } catch (error) {
            console.error('Error fetching worklogs:', error);
            this.showError(error.message || 'Failed to fetch worklogs. Please try again.');
        } finally {
            submitButton.disabled = false;
            const generateText = submitButton.querySelector('.generate-text');
            const spinner = submitButton.querySelector('svg');
            if (generateText) generateText.textContent = 'Generate';
            if (spinner) spinner.classList.add('hidden');
            if (loadingIndicator) {
                loadingIndicator.classList.add('hidden');
                loadingIndicator.classList.remove('flex');
            }
        }
    }
    
    renderResults(data) {
        const resultsContainer = document.getElementById('resultsContainer');
        if (!resultsContainer) return;
        
        if (!data || data.length === 0) {
            resultsContainer.innerHTML = `
                <div class="rounded-lg border border-yellow-200 bg-yellow-50 p-6 text-yellow-800">
                    <h3 class="text-lg font-semibold mb-2">No worklogs found</h3>
                    <p class="text-sm">
                        There are no worklogs available for the selected date range.<br>
                        Please try a different date range.
                    </p>
                </div>
            `;
            return;
        }
        
        if (this.currentView === 'table') {
            this.renderTableView(data, resultsContainer);
            return;
        }
        
        const html = data.map((day, dayIndex) => {
            const totalHours = day.daySummary.totalTimeSpentSeconds / 3600;
            const isCritical = totalHours < 4;
            const isWarning = totalHours < 8 && totalHours >= 4;
            
            const criticalClass = isCritical ? 'worklog-day-critical' : '';
            const warningClass = isWarning ? 'worklog-day-warning' : '';
            const badgeClass = isCritical ? 'worklog-badge-critical' : 
                              isWarning ? 'worklog-badge-warning' : 
                              'bg-primary/10 text-primary';
            const indicatorColor = isCritical ? 'bg-red-500' : isWarning ? 'bg-yellow-500' : 'bg-primary';
            
            const summaryIssues = day.issues.slice(0, 3);
            const summaryHtml = summaryIssues.map(issue => `
                <div class="flex items-start gap-3 p-3 rounded-lg bg-muted/50 hover:bg-muted/70 transition-colors">
                    <div class="flex-shrink-0 mt-0.5">
                        <div class="w-2 h-2 rounded-full bg-primary"></div>
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="flex items-start justify-between gap-2">
                            <h3 class="font-medium text-sm leading-tight text-foreground truncate">
                                <span class="font-semibold text-primary">${this.escapeHtml(issue.issueKey)}</span>
                                <span class="text-muted-foreground"> — ${this.escapeHtml(issue.issueSummary)}</span>
                            </h3>
                            <span class="flex-shrink-0 text-xs font-medium text-primary">${issue.worklogSummary.totalTimeSpentFormatted}</span>
                        </div>
                        <p class="text-xs text-muted-foreground mt-1">${issue.worklogs.length} worklog${issue.worklogs.length !== 1 ? 's' : ''}</p>
                    </div>
                </div>
            `).join('');
            
            const moreIssuesCount = day.issues.length > 3 ? day.issues.length - 3 : 0;
            const moreIssuesHtml = moreIssuesCount > 0 ? `
                <div class="text-center py-2">
                    <span class="text-xs text-muted-foreground">+${moreIssuesCount} more issue${moreIssuesCount !== 1 ? 's' : ''}</span>
                </div>
            ` : '';
            
            const detailsIssuesHtml = day.issues.map(issue => {
                const worklogsHtml = issue.worklogs.map(wl => `
                    <div class="flex items-start gap-3 py-1.5">
                        <div class="flex-shrink-0 mt-1">
                            <svg class="w-4 h-4 text-primary/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <div class="flex-1">
                            <div class="flex items-center gap-2 mb-1">
                                <span class="font-semibold text-sm text-primary">${wl.timeSpentFormatted}</span>
                            </div>
                            ${wl.comment ? `<p class="text-sm text-foreground/80 leading-relaxed">${this.escapeHtml(wl.comment)}</p>` : '<p class="text-xs text-muted-foreground italic">No comment</p>'}
                        </div>
                    </div>
                `).join('');
                
                return `
                    <div class="rounded-lg border-l-4 border-primary bg-muted/30 p-4 hover:bg-muted/50 transition-colors">
                        <div class="flex items-start justify-between mb-3">
                            <div class="flex-1">
                                <h3 class="font-semibold text-base leading-tight text-foreground mb-1">
                                    <span class="text-primary">${this.escapeHtml(issue.issueKey)}</span> — ${this.escapeHtml(issue.issueSummary)}
                                </h3>
                                <div class="flex items-center gap-3 text-xs text-muted-foreground">
                                    <span class="flex items-center gap-1">
                                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                                        </svg>
                                        ${this.escapeHtml(issue.reportedBy.displayName)}
                                    </span>
                                    <span>•</span>
                                    <span class="font-medium text-primary">${issue.worklogSummary.totalTimeSpentFormatted}</span>
                                </div>
                            </div>
                        </div>
                        <div class="space-y-2.5 pl-4 border-l-2 border-primary/30">
                            ${worklogsHtml}
                        </div>
                    </div>
                `;
            }).join('');
            
            return `
                <div class="group rounded-xl border bg-card text-card-foreground shadow-sm hover:shadow-md transition-all duration-200 ${criticalClass} ${warningClass}" data-day-card>
                    <div class="p-5">
                        <div class="flex items-center justify-between mb-4">
                            <div class="flex items-center gap-3">
                                <div class="flex-shrink-0 w-1 h-12 rounded-full ${indicatorColor}"></div>
                                <div>
                                    <h2 class="text-lg font-semibold tracking-tight text-foreground">${this.escapeHtml(day.workDateFormatted)}</h2>
                                    <p class="text-xs text-muted-foreground mt-0.5">${day.issues.length} issue${day.issues.length !== 1 ? 's' : ''}</p>
                                </div>
                            </div>
                            <div class="flex items-center gap-3">
                                <div class="inline-flex items-center rounded-lg px-3 py-1.5 text-sm font-semibold ${badgeClass}">
                                    ${day.daySummary.totalTimeSpentFormatted}
                                </div>
                                <button type="button" 
                                        class="day-details-toggle inline-flex items-center justify-center rounded-md border border-input bg-background px-3 py-1.5 text-xs font-medium text-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
                                        data-day-index="${dayIndex}">
                                    <span class="toggle-text">View Details</span>
                                    <svg class="toggle-icon ml-1.5 h-3.5 w-3.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                                    </svg>
                                </button>
                            </div>
                        </div>
                        <div class="day-summary space-y-3">
                            ${summaryHtml}
                            ${moreIssuesHtml}
                        </div>
                        <div class="day-details hidden mt-4 pt-4 border-t">
                            <div class="space-y-4">
                                ${detailsIssuesHtml}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        resultsContainer.innerHTML = `<div class="space-y-4">${html}</div>`;
        this.attachDetailsToggleListeners();
    }
    
    renderTableView(data, resultsContainer) {
        const rows = [];
        
        data.forEach(day => {
            day.issues.forEach(issue => {
                issue.worklogs.forEach(worklog => {
                    rows.push({
                        date: day.workDateFormatted,
                        issueKey: issue.issueKey,
                        issueSummary: issue.issueSummary,
                        timeSpent: worklog.timeSpentFormatted,
                        comment: worklog.comment || '',
                        reportedBy: issue.reportedBy.displayName
                    });
                });
            });
        });
        
        if (rows.length === 0) {
            resultsContainer.innerHTML = `
                <div class="rounded-lg border border-yellow-200 bg-yellow-50 p-6 text-yellow-800">
                    <h3 class="text-lg font-semibold mb-2">No worklogs found</h3>
                    <p class="text-sm">
                        There are no worklogs available for the selected date range.<br>
                        Please try a different date range.
                    </p>
                </div>
            `;
            return;
        }
        
        const tableHtml = `
            <div class="overflow-x-auto rounded-lg border border-border">
                <table class="w-full border-collapse">
                    <thead>
                        <tr class="bg-muted/50 border-b border-border">
                            <th class="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Date</th>
                            <th class="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Issue</th>
                            <th class="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Summary</th>
                            <th class="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Time</th>
                            <th class="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Comment</th>
                            <th class="px-4 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">Reported By</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows.map((row, index) => `
                            <tr class="border-b border-border hover:bg-muted/30 transition-colors ${index % 2 === 0 ? 'bg-card' : 'bg-muted/10'}">
                                <td class="px-4 py-3 text-sm text-foreground whitespace-nowrap">${this.escapeHtml(row.date)}</td>
                                <td class="px-4 py-3 text-sm font-semibold text-primary whitespace-nowrap">${this.escapeHtml(row.issueKey)}</td>
                                <td class="px-4 py-3 text-sm text-foreground">${this.escapeHtml(row.issueSummary)}</td>
                                <td class="px-4 py-3 text-sm font-medium text-primary whitespace-nowrap">${this.escapeHtml(row.timeSpent)}</td>
                                <td class="px-4 py-3 text-sm text-foreground/80 max-w-md">${row.comment ? this.escapeHtml(row.comment) : '<span class="text-muted-foreground italic">No comment</span>'}</td>
                                <td class="px-4 py-3 text-sm text-muted-foreground whitespace-nowrap">${this.escapeHtml(row.reportedBy)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        resultsContainer.innerHTML = tableHtml;
    }
    
    attachDetailsToggleListeners() {
        const toggleButtons = document.querySelectorAll('.day-details-toggle');
        toggleButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const dayIndex = button.getAttribute('data-day-index');
                const dayCard = button.closest('[data-day-card]');
                if (!dayCard) return;
                
                const detailsSection = dayCard.querySelector('.day-details');
                const summarySection = dayCard.querySelector('.day-summary');
                const toggleText = button.querySelector('.toggle-text');
                const toggleIcon = button.querySelector('.toggle-icon');
                
                if (detailsSection && summarySection) {
                    const isHidden = detailsSection.classList.contains('hidden');
                    
                    if (isHidden) {
                        detailsSection.classList.remove('hidden');
                        summarySection.classList.add('hidden');
                        if (toggleText) toggleText.textContent = 'Hide Details';
                        if (toggleIcon) toggleIcon.style.transform = 'rotate(180deg)';
                    } else {
                        detailsSection.classList.add('hidden');
                        summarySection.classList.remove('hidden');
                        if (toggleText) toggleText.textContent = 'View Details';
                        if (toggleIcon) toggleIcon.style.transform = 'rotate(0deg)';
                    }
                }
            });
        });
    }
    
    showError(message) {
        const errorContainer = document.getElementById('errorContainer');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
                    <h3 class="text-sm font-semibold mb-1">Error</h3>
                    <p class="text-sm">${this.escapeHtml(message)}</p>
                </div>
            `;
            errorContainer.style.display = 'block';
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    isDateRangeInvalid() {
        return (
            this.startDateInput.value &&
            this.endDateInput.value &&
            this.endDateInput.value < this.startDateInput.value
        );
    }
    
    showValidationError() {
        alert('End Date must be greater than or equal to Start Date.');
    }
    
    destroy() {
        if (this.flatpickr) {
            this.flatpickr.destroy();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new WorklogForm('worklogForm', 'dateRange', 'startDate', 'endDate');
});
