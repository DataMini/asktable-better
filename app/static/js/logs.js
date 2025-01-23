/**
 * 打开一个模态框用于显示实时日志
 * @param {string} taskId - 测试任务的唯一标识符
 */
function openLogWindow(taskId) {
    // 创建模态框 HTML
    const modalHtml = `
        <div class="modal fade" id="logModal" tabindex="-1" aria-labelledby="logModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-scrollable">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="logModalLabel">Logs for Task ${taskId}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <pre id="log-content" style="height: 70vh; overflow-y: scroll; background: #f8f9fa; padding: 1rem; border: 1px solid #ddd; white-space: pre-wrap;"></pre>
                    </div>
                </div>
            </div>
        </div>
    `;

    // 如果已存在旧的模态框则移除
    const existingModal = document.getElementById('logModal');
    if (existingModal) {
        existingModal.remove();
    }

    // 将模态框添加到文档中
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // 获取日志内容的容器
    const logContent = document.getElementById('log-content');
    let lastReadId = 0; // 初始化为 0，表示从最早的日志开始读取

    // 定义轮询函数
    async function fetchLogs() {
        try {
            // 发送 GET 请求获取新增日志
            const response = await axios.get(`/api/home/logs/${taskId}?last_read_id=${lastReadId}`);
            const { logs, last_read_id } = response.data;

            // 追加日志到模态框内容
            logs.forEach(log => {
                const logLine = `[${log.created_at}] [${log.level}] ${log.message}\n`;
                logContent.appendChild(document.createTextNode(logLine));
                logContent.scrollTop = logContent.scrollHeight; // 自动滚动到最新日志
            });

            // 更新 lastReadId 为最新日志的 ID
            if (logs.length > 0) {
                lastReadId = last_read_id;
            }
        } catch (error) {
            const errorLine = "\n[Error] Failed to fetch logs.\n";
            logContent.appendChild(document.createTextNode(errorLine));
        }
    }

    // 创建并显示模态框
    const logModal = new bootstrap.Modal(document.getElementById('logModal'));
    logModal.show();

    // 立即执行一次获取日志
    fetchLogs();

    // 开始轮询，每秒执行一次
    const pollingInterval = setInterval(fetchLogs, 1000);

    // 模态框关闭时清除轮询
    document.getElementById('logModal').addEventListener('hidden.bs.modal', () => {
        clearInterval(pollingInterval);
    });
}