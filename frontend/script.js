document.addEventListener("DOMContentLoaded", () => {
    // --- CONFIGURATION ---
    // IMPORTANT: Replace with your actual Adobe Client ID
    const ADOBE_CLIENT_ID = "48ceebcbf9394c4d9cdc82a7ba469b23";

    // --- DYNAMIC FILE LOADING ---
    const urlParams = new URLSearchParams(window.location.search);
    const analysisFile = urlParams.get('analysis_file');

    if (!analysisFile) {
        document.body.innerHTML = `
            <div style="font-family: sans-serif; padding: 40px;">
                <h1>Welcome to the Intelligent Document Viewer</h1>
                <p>To view an analysis, please specify the file in the URL.</p>
                <p><strong>Example:</strong> <a href="?analysis_file=meal_plan_analysis.json">?analysis_file=meal_plan_analysis.json</a></p>
            </div>
        `;
        return;
    }

    console.log("Viewer script started. Waiting for Adobe SDK...");

    const adobeApiReady = new Promise((resolve) => {
        if (window.AdobeDC) {
            console.log("Adobe SDK already loaded.");
            resolve();
        } else {
            document.addEventListener("adobe_dc_view_sdk.ready", () => {
                console.log("Adobe SDK ready event fired.");
                resolve();
            });
        }
    });

    let adobeDCView;

    async function fetchAnalysisData(jsonFile) {
        try {
            const response = await fetch(`/output/${jsonFile}`);
            if (!response.ok) throw new Error(`File not found in /output/ folder: ${jsonFile}`);
            return await response.json();
        } catch (error) {
            console.error("Failed to fetch analysis data:", error);
            document.getElementById("smart-toc").innerHTML = `<div class="loader" style="color: red;">Error: ${error.message}</div>`;
            return null;
        }
    }

    function initializeViewer() {
        try {
            adobeDCView = new AdobeDC.View({
                clientId: ADOBE_CLIENT_ID,
                divId: "adobe-dc-view",
            });
            console.log("AdobeDC.View initialized successfully.");
        } catch (e) {
            console.error("Error initializing AdobeDC.View. Check your Client ID.", e);
            alert("Error initializing PDF viewer. Please check your Adobe Client ID in script.js.");
        }
    }

    async function loadPdf(pdfFile) {
        if (!adobeDCView) return null;
        console.log(`Attempting to load PDF: /input/${pdfFile}`);
        return adobeDCView.previewFile({
            content: { location: { url: `/input/${pdfFile}` } },
            metaData: { fileName: pdfFile },
        }, {
            embedMode: "SIZED_CONTAINER",
            showPrintPDF: true,
            showDownloadPDF: true,
        });
    }

    function populateSidebar(data) {
        const toc = document.getElementById("smart-toc");
        const personaInfo = document.getElementById("persona-info");
        const jobInfo = document.getElementById("job-info");

        if (!data?.metadata || !Array.isArray(data?.extracted_sections)) {
            toc.innerHTML = `<div class="loader">Invalid data format in JSON file.</div>`;
            return;
        }

        personaInfo.textContent = `Persona: ${data.metadata.persona}`;
        jobInfo.textContent = `Job: ${data.metadata.job_to_be_done}`;
        toc.innerHTML = ""; // Clear loader

        data.extracted_sections.forEach(item => {
            const tocItem = document.createElement("div");
            tocItem.className = "toc-item";
            tocItem.innerHTML = `
                <div class="toc-item-title">${item.section_title}</div>
                <div class="toc-item-meta">Source: ${item.document} (Page ${item.page_number})</div>
            `;

            tocItem.addEventListener("click", async () => {
                document.querySelectorAll('.toc-item.active').forEach(el => el.classList.remove('active'));
                tocItem.classList.add('active');
                
                console.log(`Loading ${item.document} and navigating to page ${item.page_number}`);
                
                const previewFilePromise = await loadPdf(item.document);
                previewFilePromise.then(adobeViewer => {
                    adobeViewer.getAPIs().then(apis => {
                        apis.gotoLocation(item.page_number);
                    });
                });
            });
            toc.appendChild(tocItem);
        });
    }

    async function main() {
        console.log("Main function started.");
        console.log("Fetching analysis data for:", analysisFile);
        const analysisData = await fetchAnalysisData(analysisFile);
        if (!analysisData) {
            console.error("Stopping main function because analysis data is null.");
            return;
        }
        console.log("Analysis data fetched successfully.");

        const extractedSections = analysisData.extracted_sections;
        if (!Array.isArray(extractedSections) || extractedSections.length === 0) {
            console.error("No extracted_sections found in analysis data or it is empty.");
            document.getElementById("smart-toc").innerHTML = `<div class="loader">No relevant sections found in analysis.</div>`;
            return;
        }
        const initialPdf = extractedSections[0].document;
        if (!initialPdf) {
            console.error("No document field found in first extracted section.");
            document.getElementById("smart-toc").innerHTML = `<div class="loader">No PDF file found for initial section.</div>`;
            return;
        }
        console.log("Initial PDF to load:", initialPdf);

        console.log("Waiting for Adobe DC View SDK to be ready...");
        await adobeApiReady;
        
        initializeViewer();
        if (!adobeDCView) return;

        console.log("Loading initial PDF...");
        await loadPdf(initialPdf);
        console.log("Initial PDF loaded.");

        populateSidebar(analysisData);
        console.log("Sidebar populated.");
    }

    main();
});
