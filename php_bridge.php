<?php
/**
 * PHP Bridge for Django Parking System
 * 
 * Allows PHP applications to communicate with the Django backend
 * via HTTP requests to the internal Django server
 */

// Set error reporting
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Function to proxy requests to Django
function proxy_to_django($endpoint, $method = 'GET', $data = null) {
    $url = 'http://localhost:8000/' . ltrim($endpoint, '/');
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    if ($method === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        if ($data) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        }
    }
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    return [
        'status' => $httpCode,
        'data' => $response
    ];
}

// Example: Get parking records
function get_parking_records() {
    return proxy_to_django('api/parking-records/');
}

// Example: Create a new vehicle entry
function create_vehicle_entry($plate_number, $vehicle_type, $color) {
    $data = [
        'plate_number' => $plate_number,
        'vehicle_type' => $vehicle_type,
        'color' => $color
    ];
    
    return proxy_to_django('api/vehicle-entry/', 'POST', $data);
}

// Check if this file is being accessed directly
if (basename($_SERVER['PHP_SELF']) === 'php_bridge.php') {
    header('Content-Type: application/json');
    echo json_encode(['error' => 'Direct access not allowed']);
    exit();
} 