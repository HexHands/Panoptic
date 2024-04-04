function saveButton() {
  const urlParts = window.location.pathname.split('/');
  const deviceName = urlParts[urlParts.length - 1];
  const encodedDeviceName = encodeURIComponent(deviceName);

  const postUrl = `/savesetting/${encodedDeviceName}`;

  const jsonData = {
    "active": document.getElementById('active').checked,
    "name": document.getElementById('displayname').value,
    "width": parseInt(document.getElementById('width').value) || 480,
    "height": parseInt(document.getElementById('height').value) || 360,
    "videonode": document.getElementById('videonode').value === "None" ? null : document.getElementById('videonode').value,
    "audionode": document.getElementById('audionode').value === "None" ? null : document.getElementById('audionode').value,
    "framerate": parseInt(document.getElementById('framerate').value) || 30,
    "recordinglength": parseInt(document.getElementById('recordinglength').value) || 600
  };

  fetch(postUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(jsonData),
  })
  .then(response => response.json())
  .then(data => {
    console.log(data);
    showNotification(data.message)
  })
  .catch((error) => {
    console.error(error);
  });
};

/////

function savesystemButton() {
  const postUrl = `/savesystemsetting`;

  const jsonData = {
    "disksize": parseInt(document.getElementById('disksize').value) || 20,
    "erasefrequency": parseInt(document.getElementById('erasefrequency').value) || 24,
    "password": document.getElementById('password').value || "panopticsystem"
  };

  fetch(postUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(jsonData),
  })
  .then(response => response.json())
  .then(data => {
    console.log(data);
    showNotification(data.message)
  })
  .catch((error) => {
    console.error(error);
  });
};

function logoutButton() {
  document.cookie = 'password=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
  window.location.href = '/';
};

/////

function rebootButton() {
  const putUrl = `/reboot`;

  fetch(putUrl, {
    method: 'PUT'
  })
  .then(response => response.json())
  .then(data => {
    console.log(data);
    showNotification(data.message)
  })
  .catch((error) => {
    console.error(error);
  });
};

/////

function showNotification(message) {
  const notificationEl = document.getElementById('notification');
  notificationEl.textContent = message;
  notificationEl.style.display = 'block';

  setTimeout(() => {
    notificationEl.style.display = 'none';
  }, 3000);
}
