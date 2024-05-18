async function initdownload(baseUrl, day) {
    try {
        const response = await fetch(baseUrl);
        if (!response.ok) {
            throw new Error(`Error fetching video URLs: ${response.statusText}`);
        }
        const videoUrls = await response.json();

        const downloadLinkElement = document.getElementById(`downloadLink${day}`);
        const downloadProgressElement = document.getElementById(`downloadProgress${day}`);
        downloadLinkElement.textContent = '';
        downloadProgressElement.textContent = 'Preparing...';

        await handledownload(videoUrls, day, downloadLinkElement, downloadProgressElement);
    } catch (error) {
        console.error(error);
    }
}

function downloadfile(url, retries = 3) {
    return new Promise((resolve, reject) => {
        const attemptDownload = (n) => {
            fetch(url)
                .then(response => {
                    if (!response.ok) throw new Error(`Error fetching file: ${response.statusText}`);
                    return response.blob();
                })
                .then(blob => resolve(blob))
                .catch(async error => {
                    if (n > 1) {
                        attemptDownload(n - 1);
                    } else {
                        reject(error);
                    }
                });
        };
        attemptDownload(retries);
    });
}

async function handledownload(urls, day, downloadLinkElement, downloadProgressElement) {
    const zip = new JSZip();
    let downloadProgress = 0;

    await Promise.all(urls.map(async (url) => {
        try {
            const fileName = url.split('/').pop();
            const fileBlob = await downloadfile(url);
            zip.file(fileName, fileBlob, {binary: true});
            downloadProgress += 1 / urls.length;
            downloadProgressElement.textContent = `Downloading... ${(downloadProgress * 50).toFixed(2)}%`;
        } catch (error) {
            console.error(`Download failed for ${url}:`, error);
        }
    }));

    zip.generateAsync({type:"blob"}, (metadata) => {
        downloadProgressElement.textContent = `Zipping... ${(50 + (metadata.percent * 0.5)).toFixed(2)}%`;
    }).then(function(content) {
        downloadProgressElement.textContent = '';
        downloadLinkElement.style.display = '';

        const blobUrl = URL.createObjectURL(content);
        downloadLinkElement.href = blobUrl;
        downloadLinkElement.download = `${day}.zip`;
        downloadLinkElement.textContent = 'Download Ready';
        downloadLinkElement.style.display = 'inline';

	downloadLinkElement.removeAttribute('onclick');
        downloadLinkElement.click();

    }).catch(function(error) {
        downloadProgressElement.textContent = 'Download Failed';
        console.error("Failed to generate ZIP:", error);
    });
}
