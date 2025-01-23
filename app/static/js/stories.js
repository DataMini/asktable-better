async function loadStories() {
    const response = await axios.get('/api/home/stories');
    const stories = response.data.stories || [];
    const container = document.getElementById('story-panels');
    container.innerHTML = '';

    stories.forEach(story => {
        const { name, content } = story;
        const botName = content?.data?.bot_name_cn || "Unknown Bot";
        const caseCount = content?.cases?.length || 0;

        const card = `
            <div class="col">
                <div class="card h-100 shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title">${name}</h5>
                        <p><strong>Bot Name (Chinese):</strong> ${botName}</p>
                        <p><strong>Case Count:</strong> ${caseCount}</p>
                        <button class="btn btn-primary" onclick="openRunTestModal('${name}')">Run Test</button>
                    </div>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', card);
    });
}