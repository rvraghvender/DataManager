document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('file', document.getElementById('file').files[0]);
    formData.append('owner_name', document.getElementById('ownerName').value);
    formData.append('file_type', document.getElementById('fileType').value);
    formData.append('upload_date', document.getElementById('uploadDate').value);

    try {
        const response = await fetch('/api/files/upload', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorMessage = await response.text();
            alert(`Error: ${errorMessage}`);
        } else {
            const result = await response.json();
            alert(result.message);
        }
    } catch (error) {
        alert(`Upload failed: ${error.message}`);
    }
});

document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const owner_name = document.getElementById('searchOwner').value;
    const file_type = document.getElementById('searchType').value;
    const upload_date = document.getElementById('searchDate').value;

    const queryString = new URLSearchParams({ owner_name, file_type, upload_date }).toString();

    try {
        const response = await fetch(`/api/files/search?${queryString}`);
        const files = await response.json();

        const results = document.getElementById('results');
        results.innerHTML = '';

        files.forEach(file => {
            console.log('Current file:', file); // Log the entire file object for debugging
        
            // Use the 'id' property to get the fileId
            const fileId = file.id ? file.id : ''; // Update to use 'id'
		
	    const fileName = file.filename ? file.filename : 'Unknown';

        
            // Print the file_id to the terminal
            console.log(`File ID: ${fileId}, File Name: ${fileName}`); // This will print the file ID to the terminal
        
            const li = document.createElement('li');
            li.innerHTML = `
                ${file.owner_name} - ${file.file_type} - ${fileName} -  
                <a href="/api/files/download/${fileId}">Download</a>
            `;
            results.appendChild(li);
        });


    } catch (error) {
        alert(`Search failed: ${error.message}`);
    }
});

