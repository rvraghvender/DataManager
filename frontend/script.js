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
		    <td>${file.filename}</td>
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


// Download all files
//document.getElementById('downloadAll').addEventListener('click', async () => {
//    const results = document.querySelectorAll('#results li');
//
//    if (results.length === 0) {
//        alert('No files to download.');
//        return;
//    }
//
//    // Create a zip file or handle the downloads here
//    const zip = new JSZip(); // You might need to include JSZip library
//    const folder = zip.folder("files");
//
//    results.forEach((li) => {
//        const fileId = li.querySelector('a').getAttribute('href').split('/').pop();
//        const fileName = li.innerText.split(' - ')[1]; // Extract the file name or any other identifier you want
//
//        // Here you would fetch the file content and add it to the zip
//        // Assuming you have a function to fetch files by id
//        fetch(`/api/files/download/${fileId}`)
//            .then(response => response.blob())
//            .then(blob => {
//                folder.file(fileName, blob);
//            });
//    });
//
//    zip.generateAsync({ type: "blob" }).then((content) => {
//        saveAs(content, "all_files.zip"); // You might need to include FileSaver.js library
//    });
//});


// Download all files
document.getElementById('downloadAll').addEventListener('click', async () => {
    const results = document.querySelectorAll('#results tr');

    if (results.length === 0) {
        alert('No files to download.');
        return;
    }

    const zip = new JSZip();
    const folder = zip.folder("files");
    const fetchPromises = [];

    results.forEach((tr) => {
        const fileId = tr.querySelector('a').getAttribute('href').split('/').pop();
        const fileName = tr.children[6].innerText; // Adjust to get the file name

        // Fetch each file and add to the zip
        const fetchPromise = fetch(`/api/files/download/${fileId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.blob();
            })
            .then(blob => {
                folder.file(fileName, blob);
            });

        fetchPromises.push(fetchPromise); // Collect the promise
    });

    // Wait for all fetches to complete
    await Promise.all(fetchPromises);

    zip.generateAsync({ type: "blob" }).then((content) => {
        saveAs(content, "all_files.zip");
    });
});

