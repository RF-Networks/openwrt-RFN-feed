// Load the default tab content on page load
window.addEventListener('DOMContentLoaded', function() {
	loadTabContent('system-info');
});

function openTab(evt, tabName) {
	// Remove active class from all tabs
	var tabs = document.getElementsByClassName("tab");
	for (var i = 0; i < tabs.length; i++) {
		tabs[i].classList.remove("active");
	}
	
	// Mark the clicked tab as active
	evt.currentTarget.classList.add("active");
	
	// Load the template content
	loadTabContent(tabName);
}

function loadTabContent(tabName) {
	var container = document.getElementById('tab-content-container');
	container.innerHTML = '<p>Loading...</p>';
	
	var endpoint = '/cgi-bin/rfn-' + tabName;
	console.log('Loading tab content from:', endpoint);
	
	fetch(endpoint)
		.then(response => {
			console.log('Response status:', response.status);
			console.log('Response ok:', response.ok);
			if (!response.ok) {
				throw new Error('HTTP ' + response.status + ': ' + response.statusText);
			}
			return response.text();
		})
		.then(html => {
			console.log('Tab content loaded successfully');
			container.innerHTML = html;
			
			// Execute scripts in the loaded content
			var scripts = container.querySelectorAll('script');
			for (var i = 0; i < scripts.length; i++) {
				var script = scripts[i];
				var newScript = document.createElement('script');
				if (script.src) {
					newScript.src = script.src;
				} else {
					newScript.textContent = script.textContent;
				}
				script.parentNode.replaceChild(newScript, script);
			}
		})
		.catch(error => {
			console.error('Error loading template:', error);
			container.innerHTML = '<p>Error loading content: ' + error.message + '<br>Endpoint: ' + endpoint + '<br>Make sure the CGI scripts are deployed to the device.</p>';
		});
}

// Password editing functions for system-info tab
function enableEdit() {
	var passwordDisplay = document.getElementById('password-display');
	var passwordInput = document.getElementById('password-input');
	var configureBtn = document.getElementById('configure-btn');
	var editButtons = document.getElementById('edit-buttons');
	
	if (passwordDisplay && passwordInput && configureBtn && editButtons) {
		passwordDisplay.style.display = 'none';
		passwordInput.style.display = 'block';
		passwordInput.focus();
		configureBtn.style.display = 'none';
		editButtons.style.display = 'flex';
	}
}

function cancelEdit() {
	var passwordDisplay = document.getElementById('password-display');
	var passwordInput = document.getElementById('password-input');
	var configureBtn = document.getElementById('configure-btn');
	var editButtons = document.getElementById('edit-buttons');
	
	if (passwordDisplay && passwordInput && configureBtn && editButtons) {
		passwordDisplay.style.display = 'inline';
		passwordInput.style.display = 'none';
		passwordInput.value = '';
		configureBtn.style.display = 'block';
		editButtons.style.display = 'none';
	}
}

function configureAndRestart() {
	var passwordInput = document.getElementById('password-input');
	if (!passwordInput) return;
	
	var newPassword = passwordInput.value;
	
	if (!newPassword) {
		alert('Please enter a password');
		return;
	}
	
	if (confirm('This will change the root password and restart the device. Continue?')) {
		fetch('/cgi-bin/rfn-system-info', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded',
			},
			body: 'action=change_password&new_password=' + encodeURIComponent(newPassword)
		})
		.then(response => response.json())
		.then(data => {
			if (data.success) {
				alert('Password changed successfully. Device will restart now.');
				passwordInput.value = '';
			} else {
				alert('Failed to change password: ' + (data.error || 'Unknown error'));
			}
		})
		.catch(error => {
			alert('Error: ' + error.message);
		});
	}
}

function factoryReset() {
    if (confirm('This will reset the device to factory settings and erase all data. Continue?')) {
        fetch('/cgi-bin/rfn-system-info', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded',
			},
			body: 'action=reset_factory'
		})
		.then(response => response.json())
		.then(data => {
			if (data.success) {
				showModal(
					'Device Restarting. Please Wait…', 
					'See the Wi-Fi LED, it will light on steadily and start to blink or turn off afterwards. When the LED starts to blink or turn off, reload this webpage to sign in again.',
					'/templates/rfn/img/7688.gif'
				);
			} else {
				alert('Failed to reset to factory settings: ' + (data.error || 'Unknown error'));
			}
		})
		.catch(error => {
			alert('Error: ' + error.message);
		});
    }
}

// Show modal dialog
function showModal(title, message, imageUrl) {
	// Create modal overlay
	var overlay = document.createElement('div');
	overlay.id = 'modal-overlay';
	overlay.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); z-index: 9999; display: flex; align-items: center; justify-content: center;';
	
	// Create modal content
	var modal = document.createElement('div');
	modal.style.cssText = 'background: white; border-radius: 8px; padding: 30px; max-width: 500px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3); text-align: center;';
	
	// Add title
	var titleEl = document.createElement('h2');
	titleEl.textContent = title;
	titleEl.style.cssText = 'margin: 0 0 20px 0; color: #333; font-size: 22px; font-weight: 600;';
	modal.appendChild(titleEl);
	
	// Add image if provided
	if (imageUrl) {
		var imgEl = document.createElement('img');
		imgEl.src = imageUrl;
		imgEl.style.cssText = 'max-width: 100%; height: auto; margin: 0 0 20px 0;';
		modal.appendChild(imgEl);
	}
	
	// Add message
	var messageEl = document.createElement('p');
	messageEl.textContent = message;
	messageEl.style.cssText = 'margin: 0 0 30px 0; color: #555; font-size: 15px; line-height: 1.6;';
	modal.appendChild(messageEl);
	
	// Add OK button
	var button = document.createElement('button');
	button.textContent = 'OK';
	button.style.cssText = 'padding: 12px 40px; background-color: #4caf50; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: 500;';
	button.onclick = function() {
		document.body.removeChild(overlay);
	};
	modal.appendChild(button);
	
	overlay.appendChild(modal);
	document.body.appendChild(overlay);
}

// Network configuration functions
var originalNetworkConfig = {};

function updateWiFiMode() {
	var wifiMode = document.querySelector('input[name="wifi-mode"]:checked').value;
	var networkGroup = document.getElementById('wifi-network-group');
	var passwordGroup = document.getElementById('wifi-password-group');

    console.log('Selected Wi-Fi mode:', wifiMode);
	
	if (wifiMode === 'station' || wifiMode === 'repeater') {
		networkGroup.style.display = 'block';
        scanWiFiNetworks();
	} else {
		networkGroup.style.display = 'none';
		passwordGroup.style.display = 'none';
	}
}

function checkPasswordRequired() {
	var select = document.getElementById('wifi-networks');
	var passwordGroup = document.getElementById('wifi-password-group');
	var selectedOption = select.options[select.selectedIndex];
	
	if (selectedOption && selectedOption.value && selectedOption.dataset.encrypted === 'true') {
		passwordGroup.style.display = 'block';
	} else {
		passwordGroup.style.display = 'none';
	}
}

var currentSsid = null;
function scanWiFiNetworks() {
	var select = document.getElementById('wifi-networks');
	var refreshBtn = document.querySelector('.refresh-btn');
	var saveBtn = document.querySelector('.save-btn');
	
	// Disable buttons and show loading
	refreshBtn.disabled = true;
	if (saveBtn) saveBtn.disabled = true;
	refreshBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="2" fill="none" opacity="0.3"/></svg> Scanning...';
	
	select.innerHTML = '<option value="">Scanning...</option>';
	
	fetch('/cgi-bin/rfn-network', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded',
		},
		body: 'action=scan_wifi'
	})
	.then(response => response.json())
	.then(data => {
		if (data.success && data.networks) {
			select.innerHTML = '<option value="">-- Select a network --</option>';
			
			// Get current SSID from the existing option if it exists
			var existingOptions = select.querySelectorAll('option');
			for (var i = 0; i < existingOptions.length; i++) {
				if (existingOptions[i].textContent.indexOf('(current)') > -1) {
					currentSsid = existingOptions[i].value;
					break;
				}
			}

			data.networks.forEach(function(network) {
				var option = document.createElement('option');
				option.value = network.ssid;
				option.textContent = network.ssid + ' (' + network.signal + '%)' + (network.encrypted ? ' 🔒' : '');
				option.dataset.encrypted = network.encrypted;
				
				// Select the current SSID if it matches
				if (currentSsid && network.ssid === currentSsid) {
					option.selected = true;
					// Show password field if network is encrypted
					if (network.encrypted) {
						document.getElementById('wifi-password-group').style.display = 'block';
					}
				}
				
				select.appendChild(option);
			});
		} else {
			select.innerHTML = '<option value="">No networks found</option>';
		}
		
		// Re-enable buttons
		refreshBtn.disabled = false;
		if (saveBtn) saveBtn.disabled = false;
		refreshBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/><path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/></svg> Refresh';
	})
	.catch(error => {
		select.innerHTML = '<option value="">Error scanning</option>';
		alert('Error scanning networks: ' + error.message);
		refreshBtn.disabled = false;
		if (saveBtn) saveBtn.disabled = false;
		refreshBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/><path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/></svg> Refresh';
	});
}

function cancelNetworkConfig() {
	// Reload the page to reset form
	loadTabContent('network');
}

function applyNetworkConfig() {
	if (!confirm('This will apply network configuration and restart the device. Continue?')) {
		return;
	}
	
	var lanMode = document.querySelector('input[name="lan-mode"]:checked').value;
	var wifiMode = document.querySelector('input[name="wifi-mode"]:checked').value;
	var wifiNetworkSelect = document.getElementById('wifi-networks');
	var wifiNetwork = wifiNetworkSelect.value;
	var wifiPassword = document.getElementById('wifi-password').value;
	
	// Get encryption type from selected network option
	var wifiEncryption = 'none';
	if (wifiNetworkSelect.selectedIndex >= 0) {
		var selectedOption = wifiNetworkSelect.options[wifiNetworkSelect.selectedIndex];
		if (selectedOption.dataset.encrypted === 'true') {
			wifiEncryption = 'sae-mixed';
		}
	}
	
	var cellularApn = document.getElementById('cellular-apn').value;
	var cellularPin = document.getElementById('cellular-pin').value;
	var cellularUsername = document.getElementById('cellular-username').value;
	var cellularPassword = document.getElementById('cellular-password').value;
	
	var config = {
		action: 'apply_config',
		lan_mode: lanMode,
		wifi_mode: wifiMode,
		wifi_network: wifiNetwork,
		wifi_password: wifiPassword,
		wifi_encryption: wifiEncryption,
		cellular_apn: cellularApn,
		cellular_pin: cellularPin,
		cellular_username: cellularUsername,
		cellular_password: cellularPassword
	};
	
	var formBody = [];
	for (var property in config) {
		var encodedKey = encodeURIComponent(property);
		var encodedValue = encodeURIComponent(config[property]);
		formBody.push(encodedKey + "=" + encodedValue);
	}
	formBody = formBody.join("&");
	
	fetch('/cgi-bin/rfn-network', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded',
		},
		body: formBody
	})
	.then(response => response.json())
	.then(data => {
		if (data.success) {
			alert('Network configuration applied successfully. Device will restart now. Please login again.');
			window.location.href = '/cgi-bin/rfn-login';
		} else {
			alert('Failed to apply configuration: ' + (data.error || 'Unknown error'));
		}
	})
	.catch(error => {
		alert('Error: ' + error.message);
	});
}

// Toggle password visibility
function togglePassword(fieldId) {
	var field = document.getElementById(fieldId);
	if (!field) return;
	
	var button = field.nextElementSibling;
	if (!button || !button.classList.contains('toggle-password-btn')) return;
	
	if (field.type === 'password') {
		field.type = 'text';
		button.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>';
	} else {
		field.type = 'password';
		button.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>';
	}
}

