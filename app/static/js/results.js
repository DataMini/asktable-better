
/**
 * 渲染测试历史记录到表格
 * @param {Array} history - 测试历史记录数据
 */

function renderTestHistory(history) {
    const tableBody = document.getElementById('test-history-body');
    tableBody.innerHTML = ''; // 清空之前的内容

    history.forEach(test => {
        const row = `
            <tr>
                <td>${test.task_id ? `<button class="btn btn-link" onclick="openLogWindow('${test.task_id}')">${test.id}</button>` : test.id}</td>
                <td>${test.story_name}</td>
                <td>${test.model_group_name || '-'}</td>
                <td>${test.total_cases}</td>
                <td>${test.time_taken || '-'}</td>
                <td>${test.created_at}</td>
                <td>${test.at_cloud_url ? `<a href="${test.at_cloud_url}" target="_blank">AskTable</a>` : '-'}</td>
                <td>${test.feishu_doc_url ? `<a href="${test.feishu_doc_url}" target="_blank">Feishu Doc</a>` : '-'}</td>
            </tr>
        `;
        tableBody.insertAdjacentHTML('beforeend', row);
    });
}

async function loadTestHistory() {
    try {
        const response = await axios.get('/api/home/test-history');
        const history = response.data.history || [];
        renderTestHistory(history);
    } catch (error) {
        console.error('Failed to load test history:', error);
        alert('Error loading test history.');
    }
}

// 页面初始化时加载测试历史记录
loadTestHistory();