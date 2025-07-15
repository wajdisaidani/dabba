/**
 * Real GPS Tracking System for dabba
 * Provides live location tracking for transporters
 */

class GPSTracker {
    constructor() {
        this.watchId = null;
        this.isTracking = false;
        this.currentShipmentId = null;
        this.lastPosition = null;
        this.trackingInterval = null;
        this.updateFrequency = 30000; // 30 seconds
        this.options = {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 10000
        };
    }

    /**
     * Check if geolocation is supported
     */
    isSupported() {
        return 'geolocation' in navigator;
    }

    /**
     * Request permission and start tracking
     */
    async startTracking(shipmentId) {
        if (!this.isSupported()) {
            this.showTrackingStatus('GPS non supportato su questo dispositivo', 'error');
            return false;
        }

        try {
            // Request permission first
            const permission = await this.requestPermission();
            if (permission !== 'granted') {
                this.showTrackingStatus('Permesso GPS negato. Abilita la geolocalizzazione.', 'error');
                return false;
            }

            this.currentShipmentId = shipmentId;
            this.isTracking = true;

            // Start watching position
            this.watchId = navigator.geolocation.watchPosition(
                (position) => this.onPositionUpdate(position),
                (error) => this.onPositionError(error),
                this.options
            );

            // Start auto-update timer
            this.startAutoUpdate();

            this.showTrackingStatus('Tracking GPS attivato', 'success');
            this.updateTrackingDisplay({ status: 'active' });

            // Request notification permission for background tracking
            await this.requestNotificationPermission();

            return true;
        } catch (error) {
            console.error('Errore avvio tracking:', error);
            this.showTrackingStatus('Errore nell\'avvio del tracking GPS', 'error');
            return false;
        }
    }

    /**
     * Stop tracking
     */
    stopTracking() {
        if (this.watchId !== null) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
        }

        this.clearAutoUpdate();
        this.isTracking = false;
        this.currentShipmentId = null;
        this.lastPosition = null;

        this.showTrackingStatus('Tracking GPS disattivato', 'info');
        this.updateTrackingDisplay({ status: 'inactive' });
    }

    /**
     * Request geolocation permission
     */
    async requestPermission() {
        if (!('permissions' in navigator)) {
            // Fallback for browsers without Permissions API
            return new Promise((resolve) => {
                navigator.geolocation.getCurrentPosition(
                    () => resolve('granted'),
                    () => resolve('denied'),
                    { timeout: 5000 }
                );
            });
        }

        try {
            const result = await navigator.permissions.query({ name: 'geolocation' });
            return result.state;
        } catch (error) {
            return 'prompt';
        }
    }

    /**
     * Handle position updates
     */
    onPositionUpdate(position) {
        const locationData = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: new Date(position.timestamp),
            speed: position.coords.speed,
            heading: position.coords.heading
        };

        this.lastPosition = locationData;
        console.log('Nuova posizione GPS:', locationData);

        // Update UI
        this.updateTrackingDisplay(locationData);

        // Save to server
        this.savePositionToServer(locationData);

        // Update tracking timeline
        this.updateTrackingTimeline(locationData);
    }

    /**
     * Handle position errors
     */
    onPositionError(error) {
        let message = 'Errore GPS sconosciuto';
        
        switch (error.code) {
            case error.PERMISSION_DENIED:
                message = 'Permesso GPS negato dall\'utente';
                break;
            case error.POSITION_UNAVAILABLE:
                message = 'Posizione GPS non disponibile';
                break;
            case error.TIMEOUT:
                message = 'Timeout nella richiesta GPS';
                break;
        }

        console.error('Errore GPS:', message, error);
        this.showTrackingStatus(message, 'warning');
    }

    /**
     * Update tracking display in UI
     */
    updateTrackingDisplay(locationData) {
        const statusElement = document.getElementById('tracking-status');
        const positionElement = document.getElementById('current-position');
        const accuracyElement = document.getElementById('position-accuracy');

        if (statusElement) {
            if (locationData.status === 'active') {
                statusElement.innerHTML = '<i class="fas fa-satellite-dish text-success"></i> Tracking Attivo';
                statusElement.className = 'badge bg-success';
            } else if (locationData.status === 'inactive') {
                statusElement.innerHTML = '<i class="fas fa-satellite-dish text-muted"></i> Tracking Inattivo';
                statusElement.className = 'badge bg-secondary';
            }
        }

        if (locationData.latitude && positionElement) {
            positionElement.innerHTML = `
                <i class="fas fa-map-marker-alt text-primary"></i>
                ${locationData.latitude.toFixed(6)}, ${locationData.longitude.toFixed(6)}
            `;
        }

        if (locationData.accuracy && accuracyElement) {
            const accuracyClass = locationData.accuracy < 10 ? 'text-success' : 
                                locationData.accuracy < 50 ? 'text-warning' : 'text-danger';
            accuracyElement.innerHTML = `
                <i class="fas fa-crosshairs ${accuracyClass}"></i>
                Precisione: ${Math.round(locationData.accuracy)}m
            `;
        }

        // Update last update time
        const lastUpdateElement = document.getElementById('last-update');
        if (lastUpdateElement && locationData.timestamp) {
            lastUpdateElement.innerHTML = `
                <i class="fas fa-clock text-muted"></i>
                Ultimo aggiornamento: ${locationData.timestamp.toLocaleTimeString()}
            `;
        }
    }

    /**
     * Update tracking timeline
     */
    updateTrackingTimeline(locationData) {
        const timelineElement = document.getElementById('tracking-timeline');
        if (!timelineElement) return;

        // Get location name via reverse geocoding
        this.reverseGeocode(locationData.latitude, locationData.longitude)
            .then(locationName => {
                const timelineItem = document.createElement('div');
                timelineItem.className = 'timeline-item mb-3';
                timelineItem.innerHTML = `
                    <div class="d-flex">
                        <div class="flex-shrink-0">
                            <div class="bg-primary rounded-circle p-2 text-white text-center" style="width: 40px; height: 40px;">
                                <i class="fas fa-map-marker-alt"></i>
                            </div>
                        </div>
                        <div class="flex-grow-1 ms-3">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h6 class="mb-1">${locationName}</h6>
                                    <p class="text-muted small mb-1">
                                        Lat: ${locationData.latitude.toFixed(6)}, 
                                        Lng: ${locationData.longitude.toFixed(6)}
                                    </p>
                                    <p class="text-muted small mb-0">
                                        Precisione: ${Math.round(locationData.accuracy)}m
                                        ${locationData.speed ? ` • Velocità: ${Math.round(locationData.speed * 3.6)} km/h` : ''}
                                    </p>
                                </div>
                                <small class="text-muted">${locationData.timestamp.toLocaleTimeString()}</small>
                            </div>
                        </div>
                    </div>
                `;

                // Add to top of timeline
                timelineElement.insertBefore(timelineItem, timelineElement.firstChild);

                // Keep only last 10 items
                while (timelineElement.children.length > 10) {
                    timelineElement.removeChild(timelineElement.lastChild);
                }
            });
    }

    /**
     * Reverse geocoding to get location name
     */
    async reverseGeocode(lat, lng) {
        try {
            // Using OpenStreetMap Nominatim (free service)
            const response = await fetch(
                `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json&addressdetails=1&accept-language=it`
            );
            
            if (response.ok) {
                const data = await response.json();
                const address = data.address || {};
                
                // Build readable address
                const parts = [];
                if (address.road) parts.push(address.road);
                if (address.house_number) parts.push(address.house_number);
                if (address.city || address.town || address.village) {
                    parts.push(address.city || address.town || address.village);
                }
                if (address.country) parts.push(address.country);
                
                return parts.length > 0 ? parts.join(', ') : `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
            }
        } catch (error) {
            console.error('Errore reverse geocoding:', error);
        }
        
        return `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
    }

    /**
     * Save position to server
     */
    async savePositionToServer(locationData) {
        if (!this.currentShipmentId) return;

        try {
            const csrfToken = this.getCSRFToken();
            const response = await fetch('/api/tracking/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    shipment_id: this.currentShipmentId,
                    latitude: locationData.latitude,
                    longitude: locationData.longitude,
                    accuracy: locationData.accuracy,
                    speed: locationData.speed,
                    heading: locationData.heading,
                    timestamp: locationData.timestamp.toISOString()
                })
            });

            if (!response.ok) {
                console.error('Errore salvataggio posizione:', response.statusText);
            }
        } catch (error) {
            console.error('Errore comunicazione server:', error);
        }
    }

    /**
     * Start auto-update timer
     */
    startAutoUpdate() {
        this.clearAutoUpdate();
        this.trackingInterval = setInterval(() => {
            if (this.isTracking && this.lastPosition) {
                this.savePositionToServer(this.lastPosition);
            }
        }, this.updateFrequency);
    }

    /**
     * Clear auto-update timer
     */
    clearAutoUpdate() {
        if (this.trackingInterval) {
            clearInterval(this.trackingInterval);
            this.trackingInterval = null;
        }
    }

    /**
     * Get CSRF token for Django/Flask
     */
    getCSRFToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            return metaTag.getAttribute('content');
        }
        
        const cookieMatch = document.cookie.match(/csrf_token=([^;]+)/);
        if (cookieMatch) {
            return cookieMatch[1];
        }
        
        // Flask-WTF token from form
        const tokenInput = document.querySelector('input[name="csrf_token"]');
        if (tokenInput) {
            return tokenInput.value;
        }
        
        return '';
    }

    /**
     * Request notification permission for background tracking alerts
     */
    async requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            try {
                await Notification.requestPermission();
            } catch (error) {
                console.error('Errore richiesta notifiche:', error);
            }
        }
    }

    /**
     * Send notification
     */
    sendNotification(title, message, options = {}) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/logo.png',
                ...options
            });
        }
    }

    /**
     * Show tracking status
     */
    showTrackingStatus(message, type = 'info') {
        console.log(`[GPS Tracker ${type.toUpperCase()}]:`, message);
        
        // Show toast notification if available
        if (typeof showToast === 'function') {
            showToast(message, type);
        } else {
            // Fallback to alert
            if (type === 'error') {
                alert('Errore GPS: ' + message);
            }
        }
    }

    /**
     * Get current position (one-time)
     */
    async getCurrentPosition() {
        return new Promise((resolve, reject) => {
            if (!this.isSupported()) {
                reject(new Error('Geolocation non supportata'));
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const locationData = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: new Date(position.timestamp)
                    };
                    resolve(locationData);
                },
                (error) => reject(error),
                this.options
            );
        });
    }

    /**
     * Calculate distance between two points
     */
    calculateDistance(lat1, lng1, lat2, lng2) {
        const R = 6371; // Earth's radius in km
        const dLat = this.toRadians(lat2 - lat1);
        const dLng = this.toRadians(lng2 - lng1);
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) *
                Math.sin(dLng / 2) * Math.sin(dLng / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c;
    }

    /**
     * Convert degrees to radians
     */
    toRadians(degrees) {
        return degrees * (Math.PI / 180);
    }

    /**
     * Get tracking statistics
     */
    getTrackingStats() {
        return {
            isTracking: this.isTracking,
            currentShipmentId: this.currentShipmentId,
            lastPosition: this.lastPosition,
            updateFrequency: this.updateFrequency
        };
    }
}

// Initialize GPS tracker globally
window.gpsTracker = new GPSTracker();

// Auto-start tracking if shipment ID is available and user is transporter
document.addEventListener('DOMContentLoaded', function() {
    const trackingContainer = document.getElementById('gps-tracking-container');
    if (trackingContainer) {
        const shipmentId = trackingContainer.dataset.shipmentId;
        const userRole = trackingContainer.dataset.userRole;
        
        console.log('GPS Tracker inicializado para spedizione:', shipmentId);
        
        // Add tracking controls
        const trackingControls = document.createElement('div');
        trackingControls.className = 'gps-controls mt-3';
        trackingControls.innerHTML = `
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h6 class="mb-0">
                                <i class="fas fa-satellite-dish"></i> Tracking GPS
                            </h6>
                            <span id="tracking-status" class="badge bg-secondary">
                                <i class="fas fa-satellite-dish"></i> Tracking Inattivo
                            </span>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <button id="start-tracking" class="btn btn-success me-2">
                                    <i class="fas fa-play"></i> Avvia Tracking
                                </button>
                                <button id="stop-tracking" class="btn btn-danger" disabled>
                                    <i class="fas fa-stop"></i> Ferma Tracking
                                </button>
                            </div>
                            
                            <div class="row text-center">
                                <div class="col-md-4">
                                    <div id="current-position" class="text-muted small">
                                        <i class="fas fa-map-marker-alt"></i> Posizione non disponibile
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div id="position-accuracy" class="text-muted small">
                                        <i class="fas fa-crosshairs"></i> Precisione: --
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div id="last-update" class="text-muted small">
                                        <i class="fas fa-clock"></i> Mai aggiornato
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-3">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-route"></i> Cronologia Posizioni
                            </h6>
                        </div>
                        <div class="card-body">
                            <div id="tracking-timeline">
                                <p class="text-muted text-center">Nessuna posizione registrata</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        trackingContainer.appendChild(trackingControls);
        
        // Add event listeners
        const startBtn = document.getElementById('start-tracking');
        const stopBtn = document.getElementById('stop-tracking');
        
        startBtn.addEventListener('click', async () => {
            const success = await window.gpsTracker.startTracking(shipmentId);
            if (success) {
                startBtn.disabled = true;
                stopBtn.disabled = false;
            }
        });
        
        stopBtn.addEventListener('click', () => {
            window.gpsTracker.stopTracking();
            startBtn.disabled = false;
            stopBtn.disabled = true;
        });
    }
});

// Handle page visibility changes for background tracking
document.addEventListener('visibilitychange', () => {
    if (window.gpsTracker && window.gpsTracker.isTracking) {
        if (document.hidden) {
            console.log('App in background - tracking continua');
            window.gpsTracker.sendNotification(
                'dabba GPS Tracking',
                'Tracking in background attivo'
            );
        } else {
            console.log('App in foreground - tracking attivo');
        }
    }
});