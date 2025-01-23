/**
 * 打开一个新窗口用于显示实时日志
 * @param {string} taskId - 测试任务的唯一标识符
 */
function openLogWindow(taskId) {
    // 创建一个新的日志窗口
    const logWindow = window.open('', '_blank', 'width=800,height=600');
    if (!logWindow) {
        alert('Failed to open log window. Please allow popups for this website.');
        return;
    }

    // 设置窗口标题和内容
    logWindow.document.title = `Logs for Task ${taskId}`;
    logWindow.document.body.innerHTML = `
        <h3>Logs for Task ${taskId}</h3>
        <pre id="log-content" style="height: 90%; overflow-y: scroll; background: #f8f9fa; padding: 1rem; border: 1px solid #ddd;"></pre>
    `;

    // 获取日志内容的容器
    const logContent = logWindow.document.getElementById('log-content');
    let lastReadId = 0; // 初始化为 0，表示从最早的日志开始读取

    // 定义轮询函数
    async function fetchLogs() {
        try {
            // 发送 GET 请求获取新增日志
            const response = await axios.get(`/api/home/logs/${taskId}?last_read_id=${lastReadId}`);
            const { logs, last_read_id } = response.data;

            // 追加日志到窗口内容
            logs.forEach(log => {
                logContent.innerText += `[${log.created_at}] [${log.level}] ${log.message}\n`;
                logContent.scrollTop = logContent.scrollHeight; // 自动滚动到最新日志
            });

            // 更新 lastReadId 为最新日志的 ID
            if (logs.length > 0) {
                lastReadId = last_read_id;
            }
        } catch (error) {
            logContent.innerText += "\n[Error] Failed to fetch logs.\n";
        }
    }

    // 立即执行一次获取日志
    fetchLogs();

    // 开始轮询，每秒执行一次
    const pollingInterval = setInterval(fetchLogs, 1000);

    // 窗口关闭时清除轮询
    logWindow.onbeforeunload = () => {
        clearInterval(pollingInterval);
    };
}