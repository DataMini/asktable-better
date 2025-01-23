async function loadStories() {
    const response = await axios.get('/api/home/stories');
    const stories = response.data.stories || [];
    const container = document.getElementById('story-panels');
    container.innerHTML = '';

    stories.forEach(story => {
        const { name, content } = story;
        const nameCn = content?.data?.name_cn || "未命名";
        const caseCount = content?.cases?.length || 0;

        const card = `
            <div class="col">
                <div class="card h-100 shadow-sm" style="cursor: pointer" onclick="openStoryWindow('${name}', '${encodeURIComponent(JSON.stringify(content))}')">
                    <div class="card-body">
                        <h6 class="card-title">${nameCn}（${name}）</h6>
                        <p>用例:<strong> ${caseCount} 个</strong></p>
                        <button class="btn btn-primary" onclick="event.stopPropagation(); openRunTestModal('${name}')">开始测试</button>
                    </div>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', card);
    });
}

/**
 * 打开一个模态框用于展示 Story 的内容
 * @param {string} storyName - Story 的名称
 * @param {string} storyContent - Story 的内容（JSON 格式字符串）
 */
function openStoryWindow(storyName, storyContent) {
    // 解析 content 并将其转换为 YAML 格式
    const parsedContent = JSON.parse(decodeURIComponent(storyContent));
    const yamlContent = jsyaml.dump(parsedContent); // 使用 js-yaml 将 JSON 转换为 YAML

    // 设置模态框标题和内容
    const modalTitle = document.getElementById('storyModalLabel');
    const modalContent = document.getElementById('story-content');
    
    modalTitle.innerText = `Story Details: ${storyName}`;
    modalContent.innerText = yamlContent;

    // 显示模态框
    const storyModal = new bootstrap.Modal(document.getElementById('storyModal'));
    storyModal.show();
}