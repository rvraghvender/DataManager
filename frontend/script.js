// Upload file functionality
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const uploadButton = document.querySelector('#uploadForm button'); //
    uploadButton.disabled = true;                                      //
    uploadButton.textContent = 'Uploading...';                         //

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
    } finally {                                       //
	uploadButton.disabled = false;                //
	uploadButton.textContent = 'Upload';          //
    }
});



// Search functionality with date range
document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const owner_name = document.getElementById('searchOwnerName').value;
    // console.log(`Owner Name: ${owner_name}`);
    const label_name = document.getElementById('searchLabelName').value;
    const file_type = document.getElementById('searchType').value;
    const data_generator = document.getElementById('searchDataGenerator').value;
    const chemistry = document.getElementById('searchChemistry').value;
    const start_date = document.getElementById('startDate').value;
    const end_date = document.getElementById('endDate').value;

    // Check if at least one field is filled
    if (!owner_name && !label_name && !file_type && !data_generator && !chemistry && !start_date && !end_date) {
        alert('Please fill in at least one search criteria.');
        return;
    }

    const queryString = new URLSearchParams({
        owner_name,
	label_name,
        file_type,
	data_generator,
	chemistry,
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
	    let totalSize = 0;
            files.forEach(file => {
		totalSize += file.file_size || 0; //
                results.appendChild(createRow(file));
            });

            const totalSizeInMB = (totalSize / (1024 * 1024)).toFixed(2);
	    document.getElementById('fileCount').textContent = `${files.length} file(s) found (Total size: ${totalSizeInMB} MB)`;
        }


    } catch (error) {
        alert(`Search failed: ${error.message}`);
    }
});


// Append a checkbox next to the download link for each file row
function createRow(file) {
    const tr = document.createElement('tr');
    const description = file.description ? file.description : 'No description available';
    tr.innerHTML = `
        <td>${file.owner_name}</td>
        <td>${file.label_name}</td>
        <td>${file.file_type}</td>
        <td>${file.data_generator}</td>
        <td>${file.chemistry}</td>
        <td>${file.upload_date}</td>
        <td>${file.filename}</td>
        <td>${file.description}</td>
        <td>
            <a href="/api/files/download/${file.id}" class="download-link">Download</a>
            <input type="checkbox" class="file-checkbox" data-file-id="${file.id}" data-file-name="${file.filename}">
        </td>
    `;
    return tr;
}

// Select/Deselect all files when "Select All" is clicked
document.getElementById('selectAll').addEventListener('change', (event) => {
    const isChecked = event.target.checked;
    document.querySelectorAll('.file-checkbox').forEach(checkbox => {
        checkbox.checked = isChecked;
    });
});

// Download only selected files
document.getElementById('downloadAll').addEventListener('click', async () => {
    const selectedFiles = document.querySelectorAll('.file-checkbox:checked');
    if (selectedFiles.length === 0) {
        alert('No files selected.');
        return;
    }

    const downloadButton = document.getElementById('downloadAll'); //
    downloadButton.disabled = true;                                //
    downloadButton.textContent = 'Preparing Download...';          //

    const zip = new JSZip();
    const folder = zip.folder("selected_files");

    for (const checkbox of selectedFiles) {
        const fileId = checkbox.getAttribute('data-file-id');
        const fileName = checkbox.getAttribute('data-file-name');

        // Fetch file content and add it to the zip
        const response = await fetch(`/api/files/download/${fileId}`);
        const blob = await response.blob();
        folder.file(fileName, blob);
    }

    zip.generateAsync({ type: "blob" }).then((content) => {
        saveAs(content, "selected_files.zip");
    }).finally(() => {                                          //
        downloadButton.disabled = false;                        //
        downloadButton.textContent = 'Download Selected';       //
    })
});

