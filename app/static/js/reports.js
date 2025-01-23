async function loadTestReport() {
    const response = await axios.get('/api/home/test-report');
    const report = response.data.report || {};
    const headerRow = document.getElementById('test-report-header');
    const body = document.getElementById('test-report-body');

    headerRow.innerHTML = '';
    body.innerHTML = '';

    const allModels = new Set();
    for (const [story, models] of Object.entries(report)) {
        for (const model of Object.keys(models)) {
            allModels.add(model);
        }
    }
    const sortedModels = Array.from(allModels).sort();
    headerRow.innerHTML = `<th>Story</th>` + sortedModels.map(m => `<th>${m}</th>`).join('');

    for (const [story, models] of Object.entries(report)) {
        const row = [`<td>${story}</td>`];
        sortedModels.forEach(model => {
            if (models[model]) {
                const { score, timestamp } = models[model];
                const percentage = parseFloat(score.replace('%', '')); // Convert score to a number
                row.push(`
                    <td>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar" role="progressbar" style="width: ${percentage}%" aria-valuenow="${percentage}" aria-valuemin="0" aria-valuemax="100">
                                ${score}
                            </div>
                        </div>
                        <div class="mt-1 text-muted" style="font-size: 0.85rem;">${timestamp}</div>
                    </td>
                `);
            } else {
                row.push('<td>-</td>');
            }
        });
        body.insertAdjacentHTML('beforeend', `<tr>${row.join('')}</tr>`);
    }
}