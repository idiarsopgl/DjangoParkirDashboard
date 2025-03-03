<?php
/**
 * Process new vehicle entry form submission
 */

// Include the PHP bridge
require_once 'php_bridge.php';

// Check if form is submitted
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Validate and sanitize input
    $plate_number = isset($_POST['plate_number']) ? trim($_POST['plate_number']) : '';
    $vehicle_type = isset($_POST['vehicle_type']) ? trim($_POST['vehicle_type']) : '';
    $color = isset($_POST['color']) ? trim($_POST['color']) : '';
    
    // Basic validation
    $errors = [];
    
    if (empty($plate_number)) {
        $errors[] = 'Plate number is required';
    }
    
    if (empty($vehicle_type)) {
        $errors[] = 'Vehicle type is required';
    }
    
    if (empty($color)) {
        $errors[] = 'Vehicle color is required';
    }
    
    // If no errors, submit to Django backend
    if (empty($errors)) {
        $result = create_vehicle_entry($plate_number, $vehicle_type, $color);
        
        if ($result['status'] === 201 || $result['status'] === 200) {
            // Success
            $message = 'Vehicle entry created successfully!';
            $success = true;
        } else {
            // Error from Django backend
            $message = 'Error creating vehicle entry. Status: ' . $result['status'];
            $success = false;
        }
    } else {
        // Display validation errors
        $message = 'Please correct the following errors: ' . implode(', ', $errors);
        $success = false;
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Process Entry - Parking System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .card {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .success {
            color: #28a745;
        }
        .error {
            color: #dc3545;
        }
        .btn {
            display: inline-block;
            background-color: #0066cc;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
        }
        .btn:hover {
            background-color: #0052a3;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>Process Entry</h1>
            
            <?php if (isset($message)): ?>
                <div class="<?php echo $success ? 'success' : 'error'; ?>">
                    <p><?php echo htmlspecialchars($message); ?></p>
                </div>
            <?php endif; ?>
            
            <p>
                <a href="example.php" class="btn">Return to Main Page</a>
            </p>
        </div>
    </div>
</body>
</html> 