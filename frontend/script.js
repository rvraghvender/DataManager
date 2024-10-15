document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('file', document.getElementById('file').files[0]);
    formData.append('owner_name', document.getElementById('ownerName').value);
    formData.append('file_type', document.getElementById('fileType').value);
    formData.append('upload_date', document.getElementById('uploadDate').value);

    const response = await fetch('/api/files/upload', {
        method: 'POST',
        body: formData,
    });

    const result = await response.json();
    alert(result.message);
});

document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const owner_name = document.getElementById('searchOwner').value;
    const file_type = document.getElementById('searchType').value;
    const upload_date = document.getElementById('searchDate').value;

    const queryString = new URLSearchParams({ owner_name, file_type, upload_date }).toString();
    const response = await fetch(`/api/files/search?${queryString}`);
    const files = await response.json();

    const results = document.getElementById('results');
    results.innerHTML = '';
    files.forEach(file => {
        const li = document.createElement('li');
        li.innerHTML = `
            ${file.owner_name} - ${file.file_type} - <a href="/api/files/download/${file._id}">Download</a>
        `;
        results.appendChild(li);
    });
});

