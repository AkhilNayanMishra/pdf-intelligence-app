document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analysis-form');
    const resultsContainer = document.getElementById('results-container');
    const loadingSpinner = document.getElementById('loading-spinner');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Show loading spinner and clear previous results
        loadingSpinner.style.display = 'block';
        resultsContainer.innerHTML = '';

        const formData = new FormData(form);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'An unknown error occurred.');
            }

            const results = await response.json();
            displayResults(results);

        } catch (error) {
            resultsContainer.innerHTML = `<div class="error"><strong>Error:</strong> ${error.message}</div>`;
        } finally {
            // Hide loading spinner
            loadingSpinner.style.display = 'none';
        }
    });

    function displayResults(data) {
        if (!data || !data.metadata) {
            resultsContainer.innerHTML = '<div class="error">No valid results returned from the server.</div>';
            return;
        }

        let html = '<h2>Analysis Results</h2>';

        // Display Metadata
        html += '<div class="result-section"><h3>Metadata</h3>';
        html += `<p><strong>Persona:</strong> ${data.metadata.persona}</p>`;
        html += `<p><strong>Job-to-be-Done:</strong> ${data.metadata.job_to_be_done}</p>`;
        html += `<p><strong>Documents:</strong> ${data.metadata.input_documents.join(', ')}</p></div>`;

        // Display Extracted Sections
        html += '<div class="result-section"><h3>Extracted Sections (Top 5)</h3>';
        if (data.extracted_section && data.extracted_section.length > 0) {
            html += '<ul>';
            data.extracted_section.forEach(section => {
                html += `<li><strong>Rank ${section.importance_rank}:</strong> ${section.section_title} <em>(from ${section.document}, Page ${section.page_number})</em></li>`;
            });
            html += '</ul>';
        } else {
            html += '<p>No relevant sections were extracted.</p>';
        }
        html += '</div>';

        // Display Sub-section Analysis
        html += '<div class="result-section"><h3>Sub-section Analysis (Refined Text)</h3>';
        if (data['sub-section_analysis'] && data['sub-section_analysis'].length > 0) {
             data['sub-section_analysis'].forEach(sub => {
                html += `<div class="sub-section">
                            <h4>From: ${sub.document} (Page ${sub.page_number})</h4>
                            <p>${sub.refined_text}</p>
                         </div>`;
            });
        } else {
            html += '<p>No sub-section analysis was performed.</p>';
        }
        html += '</div>';

        resultsContainer.innerHTML = html;
    }
});
