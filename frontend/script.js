// Upload file functionality
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData();
    const files = document.getElementById('file').files;

    // Append all selected files
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    formData.append('owner_name', document.getElementById('ownerName').value);
    formData.append('label_name', document.getElementById('labelName').value);
    formData.append('file_type', document.getElementById('fileType').value);
    formData.append('data_generator', document.getElementById('dataGenerator').value);
    formData.append('chemistry', document.getElementById('chemistry').value);
    formData.append('upload_date', document.getElementById('uploadDate').value);
    formData.append('description', document.getElementById('description').value);

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



// Search functionality with date range
document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const owner_name = document.getElementById('searchOwner').value;
    const label_name = document.getElementById('labelName').value;
    const file_type = document.getElementById('searchType').value;
    const data_generator = document.getElementById('dataGenerator').value;
    const chemistry = document.getElementById('chemistry').value;
    const start_date = document.getElementById('startDate').value;
    const end_date = document.getElementById('endDate').value;

    const queryString = new URLSearchParams({
        owner_name,
        file_type,
        start_date,
        end_date
    }).toString();

    console.log(`Searching with query: ${queryString}`); // Debugging log

    try {
        const response = await fetch(`/api/files/search?${queryString}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const files = await response.json();

        const results = document.getElementById('results');
        results.innerHTML = '';
        
	if (files.length === 0) {
            results.innerHTML = '<tr><td colspan="4">No results found</td></tr>'; 
        } else {
            files.forEach(file => {
                const fileId = file.id ? file.id : '';
                const fileName = file.filename ? file.filename : 'Unknown';
                const description = file.description ? file.description : 'No description available';
        
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${file.owner_name}</td>
                    <td>${file.label_name}</td>
                    <td>${file.file_type}</td>
                    <td>${file.data_generator}</td>
                    <td>${file.chemistry}</td>
                    <td>${file.upload_date}</td>
                    <td>${description}</td>
                    <td><a href="/api/files/download/${fileId}" class="download-link">Download</a></td>
                `;
                results.appendChild(tr);
            });
        }


    } catch (error) {
        alert(`Search failed: ${error.message}`);
    }
});

