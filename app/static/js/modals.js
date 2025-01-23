// 打开 Story 详情模态框
function showStoryDetails(name, encodedContent) {
    const modalTitle = document.getElementById('storyModalLabel');
    const modalBody = document.getElementById('story-content');

    modalTitle.innerText = `Story: ${name}`;

    try {
        // 解码并解析内容
        const content = JSON.parse(decodeURIComponent(encodedContent));
        modalBody.innerText = JSON.stringify(content, null, 2); // 格式化 JSON 输出
    } catch (e) {
        modalBody.innerText = "Failed to load story content. Error: " + e.message;
    }

    // 显示模态框
    const storyModal = new bootstrap.Modal(document.getElementById('storyModal'));
    storyModal.show();
}

// 打开 Run Test 模态框
function openRunTestModal(storyName) {
    const storyNameInput = document.getElementById('storyNameInput');
    if (!storyNameInput) {
        console.error("storyNameInput not found in DOM.");
        return;
    }

    storyNameInput.value = storyName; // 设置值
    const runTestModal = new bootstrap.Modal(document.getElementById('runTestModal'));
    runTestModal.show(); // 打开模态框
}

// 提交 Run Test 表单
async function submitRunTest() {
    const form = document.getElementById('runTestForm');
    const formData = new FormData(form);

    const requestBody = Object.fromEntries(formData);
    requestBody.force_recreate_db = formData.has('force_recreate_db'); // 处理复选框

    try {
        // 提交测试请求
        const response = await axios.post('/api/home/run-test', requestBody);

        // 获取任务 ID
        const { task_id, message } = response.data;

        // 关闭 Run Test Modal
        const runTestModal = bootstrap.Modal.getInstance(document.getElementById('runTestModal'));
        if (runTestModal) {
            runTestModal.hide();
        }

        // 弹出日志窗口
        openLogWindow(task_id);
        
    } catch (error) {
        console.error(error);
        alert("Failed to start the test. Check the console for details.");
    }
}